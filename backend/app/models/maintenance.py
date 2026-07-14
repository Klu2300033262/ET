from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MaintenanceRecord(BaseModel):
    record_id: str
    equipment_id: str
    logged_date: datetime
    technician: str
    issue_description: str
    action_taken: str
    parts_replaced: List[str] = []
    duration_hours: float
    cost: Optional[float] = None

class SafetyInstruction(BaseModel):
    title: str
    lockout_tagout_required: bool
    required_ppe: List[str] = []
    steps: List[str]

class MaintenancePlan(BaseModel):
    plan_id: str
    equipment_id: str
    title: str
    safety_instructions: SafetyInstruction
    steps: List[str]
    estimated_duration_hours: float
    recommended_interval_days: Optional[int] = None
