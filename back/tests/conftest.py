import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app import models, auth

# Use an in-memory SQLite database for testing to ensure isolation and speed
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
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
    db.add(models.User(
        username="testuser",
        email="test@example.com",
        hashed_password=auth.get_password_hash("testpass"),
        role=models.Role.User
    ))
    
    # Create generic series and rule targets
    db.add(models.Series(series_id="TEST_SR", series_name="Test Series", starter_method="DOL", ats_scope="NO"))
    db.add(models.SizeClass(size_class="TEST_SIZE", class_rank=1, class_description="Test Size"))
    db.add(models.ComponentCatalog(part_number="TEST_CB", component_type="Magnetic Circuit Breaker", generic_description="Dummy CB", manufacturer="TestCorp"))
    db.add(models.ComponentCatalog(part_number="TEST_CONT", component_type="Contactor", generic_description="Dummy Contactor", manufacturer="TestCorp"))
    db.add(models.ComponentCatalog(part_number="TEST_OVL", component_type="Overload Relay", generic_description="Dummy Overload", manufacturer="TestCorp"))
    
    db.add(models.StarterOption(
        starter_option_id="TEST_OPT_1",
        series_id="TEST_SR",
        rated_load_power_kw=10.0,
        size_class="TEST_SIZE",
        magnetic_cb_part_number="TEST_CB",
        contactor_part_number="TEST_CONT",
        overload_part_number="TEST_OVL",
        nominal_circuit_breaker_current_a=32
    ))
    
    db.add(models.EnclosureOption(
        enclosure_option_id="TEST_ENC_1",
        catalog_ref="ENC-001",
        catalog_size_hxwxd="1200x800x400",
        layout_dim_h_mm=1200,
        layout_dim_w_mm=800,
        layout_dim_d_mm=400,
        mounting_type="Floor",
        ip_rating="IP54"
    ))
    
    db.add(models.ConfigurationRule(
        rule_id="RULE_1",
        series_id="TEST_SR",
        ats_included=False,
        size_class="TEST_SIZE",
        load_count=2,
        recommended_enclosure_option_id="TEST_ENC_1"
    ))
    
    db.commit()
    db.close()
