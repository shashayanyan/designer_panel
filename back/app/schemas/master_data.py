from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal

class SeriesBase(BaseModel):
    series_name: Optional[str] = None
    starter_method: Optional[str] = None
    ats_scope: Optional[str] = None
    notes: Optional[str] = None

class Series(SeriesBase):
    series_id: str
    model_config = ConfigDict(from_attributes=True)


class SizeClassBase(BaseModel):
    class_rank: Optional[int] = None
    class_description: Optional[str] = None
    typical_contactor_range: Optional[str] = None
    branch_current_band_a: Optional[str] = None
    engineering_note: Optional[str] = None

class SizeClass(SizeClassBase):
    size_class: str
    model_config = ConfigDict(from_attributes=True)


class ComponentCatalogBase(BaseModel):
    component_type: Optional[str] = None
    generic_description: Optional[str] = None
    manufacturer: Optional[str] = None
    part_family: Optional[str] = None

class ComponentCatalog(ComponentCatalogBase):
    part_number: str
    model_config = ConfigDict(from_attributes=True)


class StarterOptionBase(BaseModel):
    series_id: Optional[str] = None
    rated_load_power_kw: Optional[Decimal] = None
    thermal_relay_range_text: Optional[str] = None
    thermal_relay_min_a: Optional[Decimal] = None
    thermal_relay_max_a: Optional[Decimal] = None
    nominal_circuit_breaker_current_a: Optional[int] = None
    magnetic_cb_part_number: Optional[str] = None
    contactor_part_number: Optional[str] = None
    overload_part_number: Optional[str] = None
    size_class: Optional[str] = None
    data_quality_flag: Optional[str] = None

class StarterOption(StarterOptionBase):
    starter_option_id: str
    model_config = ConfigDict(from_attributes=True)


class EnclosureOptionBase(BaseModel):
    layout_dim_h_mm: Optional[int] = None
    layout_dim_w_mm: Optional[int] = None
    layout_dim_d_mm: Optional[int] = None
    catalog_ref: Optional[str] = None
    catalog_size_hxwxd: Optional[str] = None
    mounting_type: Optional[str] = None
    ip_rating: Optional[str] = None
    ik_rating: Optional[str] = None
    door_type: Optional[str] = None

class EnclosureOption(EnclosureOptionBase):
    enclosure_option_id: str
    model_config = ConfigDict(from_attributes=True)


class ConfigurationRuleBase(BaseModel):
    series_id: Optional[str] = None
    ats_included: Optional[bool] = None
    size_class: Optional[str] = None
    load_count: Optional[int] = None
    recommended_enclosure_option_id: Optional[str] = None
    alternative_enclosure_option_ids: Optional[str] = None
    rationale: Optional[str] = None

class ConfigurationRule(ConfigurationRuleBase):
    rule_id: str
    model_config = ConfigDict(from_attributes=True)


class DrawingTemplateBase(BaseModel):
    series_id: Optional[str] = None
    load_count: Optional[int] = None
    source_status: Optional[str] = None
    template_description: Optional[str] = None

class DrawingTemplate(DrawingTemplateBase):
    drawing_template_id: str
    model_config = ConfigDict(from_attributes=True)


class ConfigurationBase(BaseModel):
    starter_option_id: Optional[str] = None
    series_id: Optional[str] = None
    load_count: Optional[int] = None
    ats_included: Optional[bool] = None
    selected_enclosure_option_id: Optional[str] = None
    drawing_template_id: Optional[str] = None
    notes: Optional[str] = None

class ConfigurationRes(ConfigurationBase):
    config_id: str
    model_config = ConfigDict(from_attributes=True)


class BomLineBase(BaseModel):
    config_id: Optional[str] = None
    line_no: Optional[int] = None
    item_category: Optional[str] = None
    part_number: Optional[str] = None
    qty: Optional[Decimal] = None
    description: Optional[str] = None

class BomLine(BomLineBase):
    bom_line_id: str
    model_config = ConfigDict(from_attributes=True)


class DataQualityIssueBase(BaseModel):
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    severity: Optional[str] = None
    issue_text: Optional[str] = None
    proposed_action: Optional[str] = None

class DataQualityIssue(DataQualityIssueBase):
    issue_id: str
    model_config = ConfigDict(from_attributes=True)


class AccessoryCatalogBase(BaseModel):
    part_number: Optional[str] = None
    accessory_category: Optional[str] = None
    accessory_subcategory: Optional[str] = None
    manufacturer: Optional[str] = None
    product_range: Optional[str] = None
    nominal_rating_or_size: Optional[str] = None
    standard_use_case: Optional[str] = None
    source_url: Optional[str] = None
    notes: Optional[str] = None

class AccessoryCatalog(AccessoryCatalogBase):
    accessory_id: str
    model_config = ConfigDict(from_attributes=True)


class AccessoryRuleBase(BaseModel):
    series_id: Optional[str] = None
    size_class: Optional[str] = None
    rule_scope: Optional[str] = None
    include_in_default_bom: Optional[bool] = None
    accessory_subcategory: Optional[str] = None
    part_number: Optional[str] = None
    qty_per_feeder: Optional[Decimal] = None
    qty_per_panel: Optional[Decimal] = None
    qty_formula_text: Optional[str] = None
    design_basis: Optional[str] = None
    lookup_key: Optional[str] = None
    engineering_note: Optional[str] = None

class AccessoryRule(AccessoryRuleBase):
    accessory_rule_id: str
    model_config = ConfigDict(from_attributes=True)
