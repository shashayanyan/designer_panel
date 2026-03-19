import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app import models, auth
import os
from extract_master import extract_sheets_to_csv

csv_dir = os.path.join("dev-resources", "sheets")

def clean_df(df, columns_to_keep):
    # Keep only columns that exist in both DB and CSV
    keep = [c for c in columns_to_keep if c in df.columns]
    return df[keep].drop_duplicates()

def seed_users():
    db = SessionLocal()
    try:
        # Check if users exist
        admin = db.query(models.User).filter(models.User.email == "admin@designer-panel.com").first()
        if not admin:
            admin_user = models.User(
                username="admin",
                email="admin@designer-panel.com",
                hashed_password=auth.get_password_hash("des!gnPanel321"),
                role=models.Role.Admin
            )
            db.add(admin_user)
            
        user = db.query(models.User).filter(models.User.email == "user@designer-panel.com").first()
        if not user:
            standard_user = models.User(
                username="user",
                email="user@designer-panel.com",
                hashed_password=auth.get_password_hash("user123"),
                role=models.Role.User
            )
            db.add(standard_user)
            
        db.commit()
        print("Database seeded with default users successfully.")
    except Exception as e:
        print(f"Error seeding users: {e}")
        db.rollback()
    finally:
        db.close()

def seed_master_data():
    print("Starting master data ingestion from CSVs...")
    try:
        # Use pandas `if_exists="append"` directly on the engine.
        # To avoid DuplicateKey errors on re-runs, we truncate the tables first.
        with engine.connect() as conn:
            print("Cleaning existing master data...")
            conn.execute(text("TRUNCATE TABLE configuration, bom_line, configuration_rule, drawing_template, starter_option, enclosure_option, accessory_rule, accessory_catalog, component_catalog, size_class, series, application_io_template, application_alarm_template, application_option_matrix, data_quality_issue CASCADE;"))
            conn.commit()
        
        df_series = pd.read_csv(f"{csv_dir}/Series.csv")
        df_series_clean = clean_df(df_series, ["series_id", "series_name", "starter_method", "ats_scope", "notes"])
        df_series_clean.to_sql("series", engine, if_exists="append", index=False)
        print("Seeded series")

        df_size = pd.read_csv(f"{csv_dir}/Size_Classes.csv")
        df_size_clean = clean_df(df_size, ["size_class", "class_rank", "class_description", "typical_contactor_range", "branch_current_band_a", "engineering_note"])
        df_size_clean.to_sql("size_class", engine, if_exists="append", index=False)
        print("Seeded size_class")

        df_comp = pd.read_csv(f"{csv_dir}/Component_Catalog.csv")
        df_comp_clean = clean_df(df_comp, ["part_number", "component_type", "generic_description", "manufacturer", "part_family"])
        df_comp_clean.to_sql("component_catalog", engine, if_exists="append", index=False)
        print("Seeded component_catalog")

        df_acc = pd.read_csv(f"{csv_dir}/Accessory_Catalog.csv")
        df_acc_clean = clean_df(df_acc, ["accessory_id", "part_number", "accessory_category", "accessory_subcategory", "manufacturer", "product_range", "nominal_rating_or_size", "standard_use_case", "source_url", "notes"])
        df_acc_clean.to_sql("accessory_catalog", engine, if_exists="append", index=False)
        print("Seeded accessory_catalog")

        df_acc_rules = pd.read_csv(f"{csv_dir}/Accessory_Rules.csv")
        df_acc_rules_clean = clean_df(df_acc_rules, ["accessory_rule_id", "series_id", "size_class", "rule_scope", "include_in_default_bom", "accessory_subcategory", "part_number", "qty_per_feeder", "qty_per_panel", "qty_formula_text", "design_basis", "lookup_key", "engineering_note"])
        df_acc_rules_clean.to_sql("accessory_rule", engine, if_exists="append", index=False)
        print("Seeded accessory_rule")

        df_configs = pd.read_csv(f"{csv_dir}/Configurations.csv")

        # 8. Starter Options (Consolidated DOL, SS, VSD)
        df_dol = pd.read_csv(f"{csv_dir}/Starter_Catalog.csv")
        df_ss_raw = pd.read_csv(f"{csv_dir}/SoftStarter_Catalog.csv")
        df_vsd_raw = pd.read_csv(f"{csv_dir}/Drive_Catalog.csv")

        # Map SS
        df_ss = df_ss_raw.rename(columns={
            "soft_starter_option_id": "starter_option_id",
            "selected_soft_starter_part_number": "contactor_part_number",
            "default_magnetic_cb_part_number": "magnetic_cb_part_number",
            "default_overload_part_number": "overload_part_number"
        })
        
        # Map VSD
        df_vsd = df_vsd_raw.rename(columns={
            "drive_option_id": "starter_option_id",
            "selected_drive_part_number": "contactor_part_number",
            "default_magnetic_cb_part_number": "magnetic_cb_part_number",
            "default_overload_part_number": "overload_part_number"
        })

        df_starter_all = pd.concat([df_dol, df_ss, df_vsd], ignore_index=True)
        
        df_starter_clean = clean_df(df_starter_all, [
            "starter_option_id", "series_id", "rated_load_power_kw", "size_class", 
            "magnetic_cb_part_number", "contactor_part_number", "overload_part_number",
            "thermal_relay_range_text", "thermal_relay_min_a", "thermal_relay_max_a", 
            "nominal_circuit_breaker_current_a", "data_quality_flag"
        ])
        df_starter_clean.to_sql("starter_option", engine, if_exists="append", index=False)
        print(f"Seeded starter_option (consolidated, Total: {len(df_starter_clean)} rows)")

        # 9. Enclosure Options (from Full Catalog)
        df_enc_cat = pd.read_csv(f"{csv_dir}/Enclosure_Catalog.csv")
        df_enc_clean = clean_df(df_enc_cat, [
            "enclosure_option_id", "catalog_ref", "catalog_size_hxwxd", "mounting_type",
            "layout_dim_h_mm", "layout_dim_w_mm", "layout_dim_d_mm",
            "ip_rating", "ik_rating", "door_type"
        ])
        df_enc_clean.to_sql("enclosure_option", engine, if_exists="append", index=False)
        print("Seeded enclosure_option (full catalog)")

        # 10. Data Quality Issues
        df_dq = pd.read_csv(f"{csv_dir}/Data_Quality.csv")
        df_dq_clean = clean_df(df_dq, ["issue_id", "entity_type", "entity_id", "severity", "issue_text", "proposed_action"])
        df_dq_clean.to_sql("data_quality_issue", engine, if_exists="append", index=False)
        print("Seeded data_quality_issue")

        # 11. Drawing Templates (from Full Catalog)
        df_draw_cat = pd.read_csv(f"{csv_dir}/Drawing_Templates.csv")
        df_draw_clean = clean_df(df_draw_cat, ["drawing_template_id", "series_id", "load_count", "source_status", "template_description"])
        df_draw_clean.to_sql("drawing_template", engine, if_exists="append", index=False)
        print("Seeded drawing_template")

        # 12. Configurations
        df_cfg = df_configs[["config_id", "starter_option_id", "series_id", "load_count", "ats_included", "selected_enclosure_option_id", "drawing_template_id", "notes"]].drop_duplicates(subset=["config_id"])
        df_cfg.to_sql("configuration", engine, if_exists="append", index=False)
        print("Seeded configuration")

        # 13. BOM Lines
        df_bom = pd.read_csv(f"{csv_dir}/BOM_Lines.csv")
        df_bom_clean = clean_df(df_bom, ["bom_line_id", "config_id", "line_no", "item_category", "part_number", "qty", "description"])
        df_bom_clean.to_sql("bom_line", engine, if_exists="append", index=False)
        print(f"Seeded bom_line (Total: {len(df_bom_clean)} rows)")
        
        # 14. Enclosure Rules
        df_enc_rules = pd.read_csv(f"{csv_dir}/Enclosure_Rules.csv")
        df_conf_rules_clean = clean_df(df_enc_rules, ["rule_id", "series_id", "ats_included", "size_class", "load_count", "recommended_enclosure_option_id", "alternative_enclosure_option_ids", "rationale"])
        df_conf_rules_clean.to_sql("configuration_rule", engine, if_exists="append", index=False)
        print("Seeded configuration_rule")

        # Seed new Application Template tables
        df_io = pd.read_csv(f"{csv_dir}/Application_IO_Templates.csv")
        df_io_clean = clean_df(df_io, ["application_id", "tag_template", "description", "signal_type", "interface", "is_per_load", "required_communication_mode", "alarm_linked"])
        df_io_clean.to_sql("application_io_template", engine, if_exists="append", index=False)
        print("Seeded application_io_template")

        df_alarms = pd.read_csv(f"{csv_dir}/Application_Alarm_Templates.csv")
        df_alarms_clean = clean_df(df_alarms, ["application_id", "alarm_code_template", "tag_source_template", "condition", "priority", "is_per_load", "operator_message"])
        df_alarms_clean.to_sql("application_alarm_template", engine, if_exists="append", index=False)
        print("Seeded application_alarm_template")

        df_options = pd.read_csv(f"{csv_dir}/Application_Option_Matrix.csv")
        df_options_clean = clean_df(df_options, ["application_id", "option_category", "option_name", "is_base_or_optional", "spec_text_hint", "engineering_notes"])
        df_options_clean.to_sql("application_option_matrix", engine, if_exists="append", index=False)
        print("Seeded application_option_matrix")

        print("Master Data ingestion completed successfully!")

    except Exception as e:
        print(f"Error during master data ingestion: {e}")
        # Consider this an append logic issue if duplicate keys exist. Usually, the DB should be dropped and rebuilt.

if __name__ == "__main__":
    from app import models
    from app.database import engine
    
    extract_sheets_to_csv()
    seed_users()
    seed_master_data()
