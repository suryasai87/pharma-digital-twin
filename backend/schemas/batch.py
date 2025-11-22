"""
Pydantic schemas for batch quality control
"""
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum
from pydantic import BaseModel, Field


class BatchStatus(str, Enum):
    """Batch status enumeration"""
    IN_PROGRESS = "In Progress"
    QC_REVIEW = "QC Review"
    QA_REVIEW = "QA Review"
    RELEASED = "Released"
    REJECTED = "Rejected"
    ON_HOLD = "On Hold"


class ProductType(str, Enum):
    """Product type enumeration"""
    MAB = "Monoclonal Antibody"
    VACCINE = "Vaccine"
    INSULIN = "Insulin"
    BIOSIMILAR = "Biosimilar"
    CELL_THERAPY = "Cell Therapy"


class BatchRecord(BaseModel):
    """Batch manufacturing record"""
    batch_id: str = Field(..., description="Unique batch identifier")
    product: ProductType
    product_name: str
    start_date: datetime
    end_date: Optional[datetime] = None
    status: BatchStatus

    # Yield metrics
    target_yield: float = Field(..., description="Target yield in kg or units")
    actual_yield: Optional[float] = Field(None, description="Actual yield achieved")
    yield_percent: Optional[float] = Field(None, ge=0.0, le=100.0)

    # Quality metrics
    quality_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    purity_percent: Optional[float] = Field(None, ge=0.0, le=100.0)
    potency_percent: Optional[float] = Field(None, ge=0.0, le=120.0)

    # Manufacturing details
    bioreactor_id: str
    manufacturing_site: str
    responsible_person: str

    # Deviations and investigations
    deviations: List[Dict] = []
    capa_required: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "batch_id": "B2024-001",
                "product": "MAB",
                "product_name": "mAb-A",
                "start_date": "2024-12-01T08:00:00Z",
                "status": "In Progress",
                "target_yield": 50.0,
                "bioreactor_id": "BR-01",
                "manufacturing_site": "Site-Boston",
                "responsible_person": "John Smith"
            }
        }


class QualityControlTest(BaseModel):
    """Quality control test result"""
    test_id: str
    batch_id: str
    test_name: str
    test_type: str = Field(..., description="Identity, Purity, Potency, Safety")
    result_value: float
    specification_min: float
    specification_max: float
    pass_fail: str
    tested_by: str
    tested_at: datetime
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


class BatchYieldPrediction(BaseModel):
    """ML-based batch yield prediction"""
    batch_id: str
    predicted_yield_percent: float
    confidence_interval: tuple[float, float]
    prediction_timestamp: datetime
    model_version: str
    features_used: List[str]
