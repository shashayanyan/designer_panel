from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from decimal import Decimal

# --- INPUT SCHEMAS ---
class DigitalTwinRequest(BaseModel):
    series_id: str = Field(..., description="E.g., DOL, YD, VFD")
    motor_power_kw: Decimal = Field(..., description="Rated power in kW")
    load_count: int = Field(..., gt=0, description="Number of parallel starters/feeders")
    ats_included: bool = Field(False, description="Whether an Auto Transfer Switch is included")
    control_mode: Optional[str] = Field("Local", description="Control modality (Local, Remote, Auto)")
    ip_rating: Optional[str] = Field("IP54", description="Desired enclosure IP rating")
    communication: Optional[str] = Field("No", description="Network protocol (No, ModbusTCP, ProfiNet)")
    selected_assets: Optional[List[str]] = Field(default_factory=list, description="Requested documents from the UI checklist")


# --- OUTPUT SCHEMAS (DIGITAL TWIN) ---
class TwinComponent(BaseModel):
    part_number: str
    description: Optional[str] = None
    qty: Decimal
    item_category: str = Field(..., description="E.g., Magnetic CB, Contactor, Overload")

class TwinAccessory(BaseModel):
    part_number: str
    description: Optional[str] = None
    qty: Decimal
    category: Optional[str] = None

class TwinEnclosure(BaseModel):
    catalog_ref: str
    dimensions_mm: str = Field(..., description="Format: HxWxD")
    mounting_type: str

class TwinIO(BaseModel):
    tag: str
    description: str
    signal_type: str
    interface: str
    ip_address: Optional[str] = None

class TwinAlarm(BaseModel):
    code: str
    source_tag: str
    condition: str
    priority: str
    operator_message: str

class TwinOption(BaseModel):
    category: str
    name: str
    is_base: bool
    spec_text: Optional[str] = None
    engineering_notes: Optional[str] = None

class DigitalTwinResponse(BaseModel):
    config_id: str = Field(..., description="Unique ID for this configuration result")
    series_id: str
    motor_power_kw: Decimal
    load_count: int
    enclosure: TwinEnclosure
    components: List[TwinComponent]
    accessories: List[TwinAccessory]
    drawing_template_id: Optional[str] = None
    notes: Optional[str] = None
    communication: Optional[str] = "No"
    bypass_strategy: Optional[str] = None
    bypass_contactor_part_number: Optional[str] = None
    selected_assets: Optional[List[str]] = None
    
    # New Application Data Sheets
    network_plan: List[TwinIO] = Field(default_factory=list)
    alarm_list: List[TwinAlarm] = Field(default_factory=list)
    option_matrix: List[TwinOption] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
