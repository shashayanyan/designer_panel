from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from .database import Base
import enum

# --- Existing Auth Models ---

class Role(str, enum.Enum):
    Admin = "Admin"
    User = "User"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(Role), default=Role.User, nullable=False)

# --- Engineering Configurator Models ---

class Series(Base):
    __tablename__ = "series"
    series_id = Column(String, primary_key=True, index=True)
    series_name = Column(String)
    starter_method = Column(String)
    ats_scope = Column(String)
    notes = Column(String)

class SizeClass(Base):
    __tablename__ = "size_class"
    size_class = Column(String, primary_key=True, index=True)
    class_rank = Column(Integer)
    class_description = Column(String)
    typical_contactor_range = Column(String)
    branch_current_band_a = Column(String)
    engineering_note = Column(String)

class ComponentCatalog(Base):
    __tablename__ = "component_catalog"
    part_number = Column(String, primary_key=True, index=True)
    component_type = Column(String)
    generic_description = Column(String)
    manufacturer = Column(String)
    part_family = Column(String)
    used_in_starter_option_ids = Column(String)
    notes = Column(String)

class StarterOption(Base):
    __tablename__ = "starter_option"
    starter_option_id = Column(String, primary_key=True, index=True)
    series_id = Column(String, ForeignKey("series.series_id"))
    rated_load_power_kw = Column(Numeric(6, 2))
    availability_status = Column(String)
    selection_basis = Column(String)
    product_range = Column(String)
    controller_dims_wxhxd_mm = Column(String)
    thermal_relay_range_text = Column(String)
    thermal_relay_min_a = Column(Numeric(6, 2))
    thermal_relay_max_a = Column(Numeric(6, 2))
    nominal_circuit_breaker_current_a = Column(Integer)
    magnetic_cb_part_number = Column(String, ForeignKey("component_catalog.part_number"))
    contactor_part_number = Column(String, ForeignKey("component_catalog.part_number"))
    overload_part_number = Column(String, ForeignKey("component_catalog.part_number"))
    size_class = Column(String, ForeignKey("size_class.size_class"))
    data_quality_flag = Column(String)

class EnclosureOption(Base):
    __tablename__ = "enclosure_option"
    enclosure_option_id = Column(String, primary_key=True, index=True)
    layout_dim_h_mm = Column(Integer)
    layout_dim_w_mm = Column(Integer)
    layout_dim_d_mm = Column(Integer)
    catalog_ref = Column(String)
    catalog_size_hxwxd = Column(String)
    mounting_type = Column(String)
    ip_rating = Column(String)
    ik_rating = Column(String)
    door_type = Column(String)
    description = Column(String)
    data_quality_note = Column(String)

class ConfigurationRule(Base):
    __tablename__ = "configuration_rule"
    rule_id = Column(String, primary_key=True, index=True)
    series_id = Column(String, ForeignKey("series.series_id"))
    ats_included = Column(Boolean)
    size_class = Column(String, ForeignKey("size_class.size_class"))
    load_count = Column(Integer)
    recommended_enclosure_option_id = Column(String, ForeignKey("enclosure_option.enclosure_option_id"))
    recommended_catalog_ref = Column(String)
    recommended_layout_dims_mm = Column(String)
    alternative_enclosure_option_ids = Column(String)
    rationale = Column(String)
    lookup_key = Column(String)
    recommended_summary = Column(String)

class DrawingTemplate(Base):
    __tablename__ = "drawing_template"
    drawing_template_id = Column(String, primary_key=True, index=True)
    series_id = Column(String, ForeignKey("series.series_id"))
    load_count = Column(Integer)
    source_status = Column(String)
    template_description = Column(String)
    engineering_note = Column(String)

class Configuration(Base):
    __tablename__ = "configuration"
    config_id = Column(String, primary_key=True, index=True)
    starter_option_id = Column(String, ForeignKey("starter_option.starter_option_id"))
    series_id = Column(String, ForeignKey("series.series_id"))
    rated_load_power_kw = Column(Numeric(6, 2))
    size_class = Column(String)
    load_count = Column(Integer)
    ats_included = Column(Boolean)
    magnetic_cb_part_number = Column(String)
    magnetic_cb_qty = Column(Integer)
    contactor_part_number = Column(String)
    contactor_qty = Column(Integer)
    overload_part_number = Column(String)
    overload_qty = Column(Integer)
    selected_enclosure_option_id = Column(String, ForeignKey("enclosure_option.enclosure_option_id"))
    selected_enclosure_ref = Column(String)
    selected_enclosure_layout_dims_mm = Column(String)
    selected_enclosure_catalog_size = Column(String)
    mounting_type = Column(String)
    drawing_template_id = Column(String, ForeignKey("drawing_template.drawing_template_id"))
    bom_scope = Column(String)
    notes = Column(String)
    core_device_type = Column(String)
    core_device_part_number = Column(String)
    core_device_qty = Column(Integer)
    core_device_source_id = Column(String)
    line_contactor_role = Column(String)
    bypass_strategy = Column(String)
    bypass_contactor_part_number = Column(String)
    bypass_contactor_qty = Column(Integer)

class BomLine(Base):
    __tablename__ = "bom_line"
    bom_line_id = Column(String, primary_key=True, index=True)
    config_id = Column(String, ForeignKey("configuration.config_id"))
    line_no = Column(Integer)
    item_category = Column(String)
    part_number = Column(String)
    description = Column(String)
    qty = Column(Numeric(9, 2))
    uom = Column(String)
    source_type = Column(String)
    source_id = Column(String)

class DataQualityIssue(Base):
    __tablename__ = "data_quality_issue"
    issue_id = Column(String, primary_key=True, index=True)
    entity_type = Column(String)
    entity_id = Column(String)
    severity = Column(String)
    issue_text = Column(String)
    proposed_action = Column(String)

class AccessoryCatalog(Base):
    __tablename__ = "accessory_catalog"
    accessory_id = Column(String, primary_key=True, index=True)
    part_number = Column(String, unique=True, index=True) # Must be referenced by rule.
    accessory_category = Column(String)
    accessory_subcategory = Column(String)
    manufacturer = Column(String)
    product_range = Column(String)
    nominal_rating_or_size = Column(String)
    standard_use_case = Column(String)
    source_url = Column(String)
    notes = Column(String)

class AccessoryRule(Base):
    __tablename__ = "accessory_rule"
    accessory_rule_id = Column(String, primary_key=True, index=True)
    series_id = Column(String, ForeignKey("series.series_id"))
    size_class = Column(String) # Can be "ALL", so not strict FK
    rule_scope = Column(String)
    include_in_default_bom = Column(Boolean)
    accessory_subcategory = Column(String)
    part_number = Column(String, ForeignKey("accessory_catalog.part_number"))
    qty_per_feeder = Column(Numeric(9, 2))
    qty_per_panel = Column(Numeric(9, 2))
    qty_formula_text = Column(String)
    design_basis = Column(String)
    lookup_key = Column(String)
    engineering_note = Column(String)

class ApplicationIOTemplate(Base):
    __tablename__ = "application_io_template"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String)
    tag_template = Column(String)
    description = Column(String)
    signal_type = Column(String)
    interface = Column(String)
    is_per_load = Column(Boolean)
    required_communication_mode = Column(String)
    alarm_linked = Column(String)

class ApplicationAlarmTemplate(Base):
    __tablename__ = "application_alarm_template"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String)
    alarm_code_template = Column(String)
    tag_source_template = Column(String)
    condition = Column(String)
    priority = Column(String)
    is_per_load = Column(Boolean)
    operator_message = Column(String)

class ApplicationOptionMatrix(Base):
    __tablename__ = "application_option_matrix"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(String)
    option_category = Column(String)
    option_name = Column(String)
    is_base_or_optional = Column(String)
    spec_text_hint = Column(String)
    engineering_notes = Column(String)
