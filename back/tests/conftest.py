import pytest
from app import auth, models
from app.database import Base, get_db
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Use an in-memory SQLite database for testing to ensure isolation and speed
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Create the tables in the in-memory database
    Base.metadata.create_all(bind=engine)

    # Inject dummy master test data
    db = TestingSessionLocal()

    # Create test user
    db.add(
        models.User(
            username="testuser",
            email="test@example.com",
            hashed_password=auth.get_password_hash("testpass"),
            role=models.Role.User,
        )
    )

    # Create admin user
    db.add(
        models.User(
            username="adminuser",
            email="admin@example.com",
            hashed_password=auth.get_password_hash("adminpass"),
            role=models.Role.Admin,
        )
    )

    # Create generic series and rule targets
    db.add(
        models.Series(
            series_id="DOL",
            series_name="Test Series",
            starter_method="DOL",
            ats_scope="NO",
        )
    )
    db.add(
        models.SizeClass(
            size_class="TEST_SIZE", class_rank=1, class_description="Test Size"
        )
    )
    db.add(
        models.ComponentCatalog(
            part_number="TEST_CB",
            component_type="Magnetic Circuit Breaker",
            generic_description="Dummy CB",
            manufacturer="TestCorp",
        )
    )
    db.add(
        models.ComponentCatalog(
            part_number="TEST_CONT",
            component_type="Contactor",
            generic_description="Dummy Contactor",
            manufacturer="TestCorp",
        )
    )
    db.add(
        models.ComponentCatalog(
            part_number="TEST_OVL",
            component_type="Overload Relay",
            generic_description="Dummy Overload",
            manufacturer="TestCorp",
        )
    )

    db.add(
        models.StarterOption(
            starter_option_id="TEST_OPT_1",
            series_id="DOL",
            rated_load_power_kw=10.0,
            size_class="TEST_SIZE",
            magnetic_cb_part_number="TEST_CB",
            contactor_part_number="TEST_CONT",
            overload_part_number="TEST_OVL",
            nominal_circuit_breaker_current_a=32,
        )
    )

    db.add(
        models.EnclosureOption(
            enclosure_option_id="TEST_ENC_1",
            catalog_ref="ENC-001",
            catalog_size_hxwxd="1200x800x400",
            layout_dim_h_mm=1200,
            layout_dim_w_mm=800,
            layout_dim_d_mm=400,
            mounting_type="Floor",
            ip_rating="IP54",
        )
    )

    db.add(
        models.ConfigurationRule(
            rule_id="RULE_1",
            series_id="DOL",
            ats_included=False,
            size_class="TEST_SIZE",
            load_count=2,
            recommended_enclosure_option_id="TEST_ENC_1",
        )
    )

    db.add(
        models.Series(
            series_id="VSD",
            series_name="Variable Speed Drive",
            starter_method="VFD",
            ats_scope="NO",
        )
    )
    db.add(
        models.Series(
            series_id="SS",
            series_name="Soft Starter",
            starter_method="SS",
            ats_scope="NO",
        )
    )
    db.add(
        models.ComponentCatalog(
            part_number="TEST_VSD_CORE",
            component_type="Drive",
            generic_description="Dummy VSD",
            manufacturer="TestCorp",
        )
    )
    db.add(
        models.ComponentCatalog(
            part_number="TEST_SS_CORE",
            component_type="Soft Starter",
            generic_description="Dummy SS",
            manufacturer="TestCorp",
        )
    )

    db.add(
        models.StarterOption(
            starter_option_id="VSD_OPT",
            series_id="VSD",
            rated_load_power_kw=15.0,
            size_class="TEST_SIZE",
            magnetic_cb_part_number="TEST_CB",
            contactor_part_number="TEST_VSD_CORE",
            nominal_circuit_breaker_current_a=40,
        )
    )
    db.add(
        models.StarterOption(
            starter_option_id="SS_OPT",
            series_id="SS",
            rated_load_power_kw=15.0,
            size_class="TEST_SIZE",
            magnetic_cb_part_number="TEST_CB",
            contactor_part_number="TEST_SS_CORE",
            nominal_circuit_breaker_current_a=40,
        )
    )

    db.add(
        models.ConfigurationRule(
            rule_id="RULE_VSD",
            series_id="VSD",
            ats_included=False,
            size_class="TEST_SIZE",
            load_count=2,
            recommended_enclosure_option_id="TEST_ENC_1",
        )
    )
    db.add(
        models.ConfigurationRule(
            rule_id="RULE_SS",
            series_id="SS",
            ats_included=False,
            size_class="TEST_SIZE",
            load_count=2,
            recommended_enclosure_option_id="TEST_ENC_1",
        )
    )

    db.add(
        models.SizeClass(
            size_class="LARGE_SIZE", class_rank=2, class_description="Large Size"
        )
    )
    db.add(
        models.ComponentCatalog(
            part_number="LARGE_CB",
            component_type="Magnetic Circuit Breaker",
            generic_description="Large CB",
            manufacturer="TestCorp",
        )
    )
    db.add(
        models.StarterOption(
            starter_option_id="LARGE_DOL_OPT",
            series_id="DOL",
            rated_load_power_kw=55.0,
            size_class="LARGE_SIZE",
            magnetic_cb_part_number="LARGE_CB",
            contactor_part_number="TEST_CONT",
            overload_part_number="TEST_OVL",
            nominal_circuit_breaker_current_a=125,
        )
    )

    db.add(
        models.EnclosureOption(
            enclosure_option_id="TEST_ENC_LARGE",
            catalog_ref="ENC-LARGE",
            catalog_size_hxwxd="2000x1200x600",
            layout_dim_h_mm=2000,
            layout_dim_w_mm=1200,
            layout_dim_d_mm=600,
            mounting_type="Floor",
            ip_rating="IP54",
        )
    )
    db.add(
        models.EnclosureOption(
            enclosure_option_id="TEST_ENC_ATS",
            catalog_ref="ENC-ATS",
            catalog_size_hxwxd="2000x1600x600",
            layout_dim_h_mm=2000,
            layout_dim_w_mm=1600,
            layout_dim_d_mm=600,
            mounting_type="Floor",
            ip_rating="IP54",
        )
    )

    db.add(
        models.ConfigurationRule(
            rule_id="RULE_LARGE_NO_ATS",
            series_id="DOL",
            ats_included=False,
            size_class="LARGE_SIZE",
            load_count=3,
            recommended_enclosure_option_id="TEST_ENC_LARGE",
        )
    )
    db.add(
        models.ConfigurationRule(
            rule_id="RULE_LARGE_ATS",
            series_id="DOL",
            ats_included=True,
            size_class="LARGE_SIZE",
            load_count=3,
            recommended_enclosure_option_id="TEST_ENC_ATS",
        )
    )
    db.add(
        models.ConfigurationRule(
            rule_id="RULE_STRESS_TEST",
            series_id="DOL",
            ats_included=False,
            size_class="TEST_SIZE",
            load_count=10,
            recommended_enclosure_option_id="TEST_ENC_LARGE",
        )
    )

    db.add(
        models.AccessoryCatalog(
            accessory_id="ACC_1",
            part_number="PART_FORMULA",
            accessory_subcategory="Formula Accessory",
            manufacturer="TestCorp",
            standard_use_case="Testing formulas",
        )
    )
    db.add(
        models.AccessoryCatalog(
            accessory_id="ACC_2",
            part_number="PART_FEEDER",
            accessory_subcategory="Feeder Accessory",
            manufacturer="TestCorp",
            standard_use_case="Testing per-feeder",
        )
    )
    db.add(
        models.AccessoryCatalog(
            accessory_id="ACC_3",
            part_number="PART_PANEL",
            accessory_subcategory="Panel Accessory",
            manufacturer="TestCorp",
            standard_use_case="Testing per-panel",
        )
    )

    db.add(
        models.AccessoryRule(
            accessory_rule_id="RULE_ACC_1",
            series_id="DOL",
            size_class="TEST_SIZE",
            include_in_default_bom=True,
            accessory_subcategory="Formula Accessory",
            part_number="PART_FORMULA",
            qty_formula_text="load_count + 5",
        )
    )
    db.add(
        models.AccessoryRule(
            accessory_rule_id="RULE_ACC_2",
            series_id="DOL",
            size_class="TEST_SIZE",
            include_in_default_bom=True,
            accessory_subcategory="Feeder Accessory",
            part_number="PART_FEEDER",
            qty_per_feeder=2.0,
        )
    )
    db.add(
        models.AccessoryRule(
            accessory_rule_id="RULE_ACC_3",
            series_id="DOL",
            size_class="TEST_SIZE",
            include_in_default_bom=True,
            accessory_subcategory="Panel Accessory",
            part_number="PART_PANEL",
            qty_per_panel=1.0,
        )
    )

    # Add a Configuration and BOM Lines for source mapping tests
    # config_id format: CFG-TEST_OPT_1-2X
    db.add(
        models.Configuration(
            config_id="CFG-TEST_OPT_1-2X",
            starter_option_id="TEST_OPT_1",
            series_id="DOL",
            rated_load_power_kw=10.0,
            load_count=2,
            selected_enclosure_ref="ENC-001",
        )
    )

    db.add(
        models.BomLine(
            bom_line_id="BL_1",
            config_id="CFG-TEST_OPT_1-2X",
            line_no=1,
            item_category="Enclosure",
            part_number="ENC-001",
            description="Base Enclosure",
            qty=1,
            uom="PC",
            source_type="enclosure",
            source_id="TEST_ENC_1",
        )
    )
    db.add(
        models.BomLine(
            bom_line_id="BL_2",
            config_id="CFG-TEST_OPT_1-2X",
            line_no=2,
            item_category="Component",
            part_number="TEST_CB",
            description="Base CB",
            qty=2,
            uom="PC",
            source_type="component",
        )
    )
    db.add(
        models.BomLine(
            bom_line_id="BL_3",
            config_id="CFG-TEST_OPT_1-2X",
            line_no=3,
            item_category="Accessory",
            part_number="PART_PANEL",
            description="Base Accessory",
            qty=1,
            uom="PC",
            source_type="accessory",
        )
    )

    db.commit()
    db.close()
