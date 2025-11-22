"""
Pydantic schemas for bioreactor data models
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class BioreactorSensorData(BaseModel):
    """Real-time sensor data from bioreactor"""
    timestamp: datetime = Field(..., description="Sensor reading timestamp")
    bioreactor_id: str = Field(..., description="Bioreactor identifier")

    # Critical Process Parameters (CPPs)
    temperature: float = Field(..., ge=30.0, le=42.0, description="Temperature in °C (±0.1°C precision)")
    ph: float = Field(..., ge=5.0, le=9.0, description="pH level (±0.05 pH units)")
    dissolved_oxygen: float = Field(..., ge=0.0, le=100.0, description="Dissolved oxygen % saturation")
    agitation_rpm: int = Field(..., ge=0, le=500, description="Agitation speed in RPM")
    pressure: float = Field(..., ge=0.0, le=2.0, description="Pressure in bar (±0.01 bar)")

    # Critical Quality Attributes (CQAs)
    cell_density: Optional[float] = Field(None, ge=0.0, description="Cell density (OD600)")
    viable_cell_count: Optional[float] = Field(None, ge=0.0, description="Viable cells/mL")

    # Nutrient levels
    glucose: Optional[float] = Field(None, description="Glucose concentration g/L")
    lactate: Optional[float] = Field(None, description="Lactate concentration g/L")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-12-05T14:30:00Z",
                "bioreactor_id": "BR-01",
                "temperature": 37.0,
                "ph": 7.0,
                "dissolved_oxygen": 45.5,
                "agitation_rpm": 120,
                "pressure": 1.2,
                "cell_density": 3.5,
                "viable_cell_count": 8.5e6
            }
        }


class BioreactorStatus(BaseModel):
    """Current bioreactor status"""
    bioreactor_id: str
    name: str
    status: str = Field(..., description="Operational, Warning, Critical, Offline")
    current_batch_id: Optional[str] = None
    start_time: Optional[datetime] = None
    estimated_harvest: Optional[datetime] = None
    phase: Optional[str] = Field(None, description="lag, exponential, stationary, death")
    working_volume: float = Field(..., description="Working volume in liters")
    last_updated: datetime


class BioreactorDigitalTwin(BaseModel):
    """Complete digital twin model of bioreactor"""
    bioreactor_id: str
    physical_model: dict = Field(..., description="Physical specifications")
    process_state: dict = Field(..., description="Current process state")
    maintenance_history: dict = Field(..., description="CIP/SIP and maintenance records")
    sensor_data: List[BioreactorSensorData]
    health_score: float = Field(..., ge=0.0, le=100.0)
    alerts: List[dict] = []
