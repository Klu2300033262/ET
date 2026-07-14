from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class EquipmentBase(BaseModel):
    equipment_id: str = Field(..., description="Unique alphanumeric identifier for equipment")
    name: str = Field(..., description="Standard name of the equipment")
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    location: Optional[str] = None
    status: str = Field("active", description="Operational status: active, maintenance, decommissioning")

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentRelationship(BaseModel):
    source_id: str
    target_id: str
    relation_type: str  # PART_OF, CONNECTED_TO, LOCATED_IN
    properties: Dict[str, Any] = {}

class EquipmentDetail(EquipmentBase):
    parent_id: Optional[str] = None
    subcomponents: List[str] = []
    attributes: Dict[str, Any] = {}
