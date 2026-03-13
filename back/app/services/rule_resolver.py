from sqlalchemy.orm import Session
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
    TwinEnclosure
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
            print(f"Formula eval failed: {e} for string '{formula_text}'")
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
        ac_rules = self.db.query(models.AccessoryRule).filter(
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
                    # We can fetch descriptions directly from Accessory_Catalog via relationships if needed. 
                    # For performance/minimalist JSON, part_number is enough or fetch it natively:
                    cat_details = self.db.query(models.AccessoryCatalog).filter(
                       models.AccessoryCatalog.part_number == rule.part_number
                    ).first()
                    acc_desc = cat_details.standard_use_case if cat_details else None

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
            notes=config_rule.rationale if config_rule else None
        )

        return response
