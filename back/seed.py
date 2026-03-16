import pandas as pd
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
        # Use pandas `if_exists="append"` directly on the engine
        # We assume the database has been rebuilt or relies on unique constraints dropping duplicates naturally if handled.
        
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

        df_starter = df_configs[["starter_option_id", "series_id", "rated_load_power_kw", "size_class", "magnetic_cb_part_number", "contactor_part_number", "overload_part_number"]].drop_duplicates(subset=["starter_option_id"])
        df_starter.to_sql("starter_option", engine, if_exists="append", index=False)
        print("Seeded starter_option")

        df_enc_raw = df_configs[["selected_enclosure_option_id", "selected_enclosure_ref", "selected_enclosure_layout_dims_mm", "selected_enclosure_catalog_size", "mounting_type"]].drop_duplicates(subset=["selected_enclosure_option_id"])
        df_enc = pd.DataFrame()
        df_enc["enclosure_option_id"] = df_enc_raw["selected_enclosure_option_id"]
        df_enc["catalog_ref"] = df_enc_raw["selected_enclosure_ref"]
        df_enc["catalog_size_hxwxd"] = df_enc_raw["selected_enclosure_catalog_size"]
        df_enc["mounting_type"] = df_enc_raw["mounting_type"]
        dims = df_enc_raw["selected_enclosure_layout_dims_mm"].str.split("x", expand=True)
        df_enc["layout_dim_h_mm"] = pd.to_numeric(dims[0], errors='coerce')
        df_enc["layout_dim_w_mm"] = pd.to_numeric(dims[1], errors='coerce')
        df_enc["layout_dim_d_mm"] = pd.to_numeric(dims[2], errors='coerce')
        df_enc.to_sql("enclosure_option", engine, if_exists="append", index=False)
        print("Seeded enclosure_option")

        df_draw = df_configs[["drawing_template_id", "series_id", "load_count"]].drop_duplicates(subset=["drawing_template_id"])
        df_draw.to_sql("drawing_template", engine, if_exists="append", index=False)
        print("Seeded drawing_template")

        df_cfg = df_configs[["config_id", "starter_option_id", "series_id", "load_count", "ats_included", "selected_enclosure_option_id", "drawing_template_id", "notes"]].drop_duplicates(subset=["config_id"])
        df_cfg.to_sql("configuration", engine, if_exists="append", index=False)
        print("Seeded configuration")
        
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
    
    # Optional: Clear tables to avoid conflicts for a fresh seed.
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    
    extract_sheets_to_csv()
    seed_users()
    seed_master_data()
