from sqlalchemy.orm import Session, joinedload
import logging
from fastapi import HTTPException
from decimal import Decimal
import ast
import operator
import re

from .. import models
from ..schemas.configurator import (
    DigitalTwinRequest,
    DigitalTwinResponse,
    TwinComponent,
    TwinAccessory,
    TwinEnclosure,
    TwinIO,
    TwinAlarm,
    TwinOption
)

class MathSafeParser:
    """Safely evaluates basic math string formulas (e.g. 'load_count * 2')"""
    
    ALLOWED_OPERATORS = {
        ast.Add: operator.add, ast.Sub: operator.sub, 
        ast.Mult: operator.mul, ast.Div: operator.truediv, 
        ast.USub: operator.neg
    }

    def __init__(self, variables: dict):
        self.variables = variables

    def _eval(self, node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)): # <number>
            return node.value
        elif isinstance(node, ast.Name): # <variable>
            if node.id in self.variables:
                return self.variables[node.id]
            raise ValueError(f"Unknown variable in formula: {node.id}")
        elif isinstance(node, ast.BinOp): # <left> <operator> <right>
            return self.ALLOWED_OPERATORS[type(node.op)](self._eval(node.left), self._eval(node.right))
        elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
            return self.ALLOWED_OPERATORS[type(node.op)](self._eval(node.operand))
        else:
            raise TypeError(f"Unsupported formula element: {node}")

    def evaluate(self, formula_text: str):
        if not formula_text or formula_text.strip().upper() == "N/A":
            return Decimal("0")
        try:
            # First map string replacements for specific brackets logic if they exist (e.g., "[X] * 2")
            clean_formula = formula_text.lower()
            # In our CSVs formulas are something like "load_count * 2"
            tree = ast.parse(clean_formula, mode='eval').body
            return Decimal(str(self._eval(tree)))
        except SyntaxError:
            try:
                # If there's an alphanumeric text (like "See rules"), return 0
                return Decimal("0") 
            except Exception:
                return Decimal("0")
        except Exception as e:
            # Fallback fail safe
            logging.error(f"Formula evaluation failed for string '{formula_text}': {e}. Variables context: {self.variables}. Returning quantity 0.")
            return Decimal("0")

class ConfigurationEngine:
    def __init__(self, db: Session):
        self.db = db

    def generate_twin(self, request: DigitalTwinRequest) -> DigitalTwinResponse:
        """
        Main execution flow resolving the digital twin based on input constraints.
        Resolves starter -> enclosure -> accessories -> full configuration.
        """
        # 1. Base Query: Find matching Starter Option
        starter = self.db.query(models.StarterOption).filter(
            models.StarterOption.series_id == request.series_id,
            models.StarterOption.rated_load_power_kw == request.motor_power_kw
        ).first()

        if not starter:
            raise HTTPException(status_code=404, detail="No matching starter option found for this configuration requirements.")

        # 2. Extract base core components
        components = []
        
        # Determine Core Device Type based on Series
        core_type = ""
        core_part = ""
        if request.series_id == "VSD":
            core_type = "Variable Speed Drive"
            # As a simplified placeholder until 'drive_part_number' is formally in StarterOption, we infer it or leave blank:
            core_part = getattr(starter, 'drive_part_number', 'VSD-PENDING-MASTER-DATA')
            components.append(TwinComponent(item_category="Core Device", part_number=core_part, description=core_type, qty=Decimal(request.load_count)))
        elif request.series_id == "SS":
            core_type = "Soft Starter"
            core_part = getattr(starter, 'soft_starter_part_number', 'SS-PENDING-MASTER-DATA')
            components.append(TwinComponent(item_category="Core Device", part_number=core_part, description=core_type, qty=Decimal(request.load_count)))

        if starter.magnetic_cb_part_number:
            components.append(TwinComponent(
                item_category="Magnetic CB", 
                part_number=starter.magnetic_cb_part_number, 
                qty=Decimal(request.load_count)
            ))
        if starter.contactor_part_number:
            components.append(TwinComponent(
                item_category="Contactor", 
                part_number=starter.contactor_part_number, 
                qty=Decimal(request.load_count)
            ))
        if starter.overload_part_number:
            components.append(TwinComponent(
                item_category="Thermal Overload", 
                part_number=starter.overload_part_number, 
                qty=Decimal(request.load_count)
            ))

        # 3. Enclosure Logic: Evaluate Configuration Rule based on size_class and load_count
        config_rule = self.db.query(models.ConfigurationRule).filter(
            models.ConfigurationRule.series_id == request.series_id,
            models.ConfigurationRule.size_class == starter.size_class,
            models.ConfigurationRule.load_count == request.load_count,
            models.ConfigurationRule.ats_included == request.ats_included
        ).first()

        if not config_rule:
             raise HTTPException(status_code=404, detail="No matching enclosure configuration rule found.")

        enclosure_option = self.db.query(models.EnclosureOption).filter(
            models.EnclosureOption.enclosure_option_id == config_rule.recommended_enclosure_option_id
        ).first()

        if not enclosure_option:
            raise HTTPException(status_code=404, detail="Mapped Enclosure ID not found in database.")

        enclosure_data = TwinEnclosure(
            catalog_ref=enclosure_option.catalog_ref,
            dimensions_mm=f"{enclosure_option.layout_dim_h_mm}x{enclosure_option.layout_dim_w_mm}x{enclosure_option.layout_dim_d_mm}",
            mounting_type=enclosure_option.mounting_type
        )

        # 4. Drawing Template Logic
        drawing = self.db.query(models.DrawingTemplate).filter(
            models.DrawingTemplate.series_id == request.series_id,
            models.DrawingTemplate.load_count == request.load_count
        ).first()
        dt_id = drawing.drawing_template_id if drawing else None

        # 5. Build Configuration lookup ID
        # Configurations table holds config_id format like: CFG-ST001-1X
        # To strictly map it back, we can infer it or fetch it.
        config_db_record = self.db.query(models.Configuration).filter(
            models.Configuration.starter_option_id == starter.starter_option_id,
            models.Configuration.load_count == request.load_count
        ).first()
        cid = config_db_record.config_id if config_db_record else f"CFG-{starter.starter_option_id}-{request.load_count}X"

        # 6. Evaluate Accessory Rules
        accessories = []
        ac_rules = self.db.query(models.AccessoryRule).options(
            joinedload(models.AccessoryRule.catalog_item)
        ).filter(
            models.AccessoryRule.series_id == request.series_id,
            models.AccessoryRule.size_class == starter.size_class
        ).all()

        parser = MathSafeParser({"load_count": request.load_count})

        for rule in ac_rules:
            if not rule.include_in_default_bom:
                continue

            try:
                # Determine qty logic
                qty_val = Decimal("0")
                if rule.qty_formula_text:
                    qty_val = parser.evaluate(rule.qty_formula_text)
                elif rule.qty_per_feeder:
                    qty_val = rule.qty_per_feeder * Decimal(request.load_count)
                elif rule.qty_per_panel:
                    qty_val = Decimal(rule.qty_per_panel)

                # Ensure we skip zero quantities
                if qty_val > Decimal("0"):
                    # Utilizing the joinedload ORM relationship to avoid N+1 DB round-trips
                    acc_desc = rule.catalog_item.standard_use_case if rule.catalog_item else None

                    accessories.append(TwinAccessory(
                        category=rule.accessory_subcategory,
                        part_number=rule.part_number,
                        description=acc_desc,
                        qty=qty_val
                    ))
            except Exception as e:
                print(f"Skipping rule {rule.accessory_rule_id} due to eval error: {e}")
                pass

        # 7. Assemble Unified Response (Digital Twin)
        response = DigitalTwinResponse(
            config_id=cid,
            series_id=request.series_id,
            motor_power_kw=request.motor_power_kw,
            load_count=request.load_count,
            enclosure=enclosure_data,
            components=components,
            accessories=accessories,
            drawing_template_id=dt_id,
            notes=config_rule.rationale if config_rule else None,
            communication=request.communication,
            bypass_strategy=getattr(starter, 'bypass_strategy', 'None'),
            bypass_contactor_part_number=getattr(starter, 'bypass_contactor_part_number', None),
            selected_assets=request.selected_assets,
            single_line_diagram_b64=request.single_line_diagram_b64
        )

        # 8. Resolve Application-Specific Templates (IO, Alarms, Options)
        app_id = "APP-WATER-BOOSTER" # Fixed for this specific application page
        
        # 8a. IO Templates -> Network Plan
        io_templates = self.db.query(models.ApplicationIOTemplate).filter(
            models.ApplicationIOTemplate.application_id == app_id
        ).all()
        
        network_plan = []
        for iot in io_templates:
            # Filter by communication mode if required
            if iot.required_communication_mode and iot.required_communication_mode != request.communication:
                continue
            
            if iot.is_per_load:
                for i in range(1, request.load_count + 1):
                    tag = (iot.tag_template or "").replace("{i}", str(i))
                    desc = (iot.description or "").replace("{i}", str(i))
                    # Simple IP assignment logic if communication is ModbusTCP
                    ip = None
                    if request.communication == "ModbusTCP" and iot.interface == "Modbus TCP":
                        ip = f"192.168.1.{10 + i}" # Simple sequential assignment starting .11
                    
                    network_plan.append(TwinIO(
                        tag=tag,
                        description=desc,
                        signal_type=iot.signal_type,
                        interface=iot.interface,
                        ip_address=ip
                    ))
            else:
                network_plan.append(TwinIO(
                    tag=iot.tag_template,
                    description=iot.description,
                    signal_type=iot.signal_type,
                    interface=iot.interface,
                    ip_address="192.168.1.10" if request.communication == "ModbusTCP" and iot.interface == "Modbus TCP" else None
                ))
        response.network_plan = network_plan

        # 8b. Alarm Templates -> Alarm List
        alarm_templates = self.db.query(models.ApplicationAlarmTemplate).filter(
            models.ApplicationAlarmTemplate.application_id == app_id
        ).all()
        
        alarm_list = []
        for alt in alarm_templates:
            if alt.is_per_load:
                for i in range(1, request.load_count + 1):
                    code = (alt.alarm_code_template or "").replace("{i}", str(i))
                    source = (alt.tag_source_template or "").replace("{i}", str(i))
                    msg = (alt.operator_message or "").replace("{i}", str(i))
                    alarm_list.append(TwinAlarm(
                        code=code,
                        source_tag=source,
                        condition=alt.condition,
                        priority=alt.priority,
                        operator_message=msg
                    ))
            else:
                alarm_list.append(TwinAlarm(
                    code=alt.alarm_code_template,
                    source_tag=alt.tag_source_template,
                    condition=alt.condition,
                    priority=alt.priority,
                    operator_message=alt.operator_message
                ))
        response.alarm_list = alarm_list

        # 8c. Option Matrix Logic
        option_matrix = self.db.query(models.ApplicationOptionMatrix).filter(
            models.ApplicationOptionMatrix.application_id == app_id
        ).all()
        
        # In a real engine, we'd filter based on 'selected' options, 
        # but for now we list the matrix applicable to this twin.
        response.option_matrix = [
            TwinOption(
                category=opt.option_category,
                name=opt.option_name,
                is_base=(opt.is_base_or_optional == "Base"),
                spec_text=opt.spec_text_hint,
                engineering_notes=opt.engineering_notes
            ) for opt in option_matrix
        ]

        return response
