"""
Batch quality control API endpoints
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from backend.schemas.batch import BatchRecord, QualityControlTest, BatchYieldPrediction
from backend.utils.synthetic_data import pharma_data_generator
from backend.utils.auth import verify_token, AuditContext

router = APIRouter()


@router.get("/list", response_model=List[dict])
async def list_batches(
    status: Optional[str] = Query(None, description="Filter by status"),
    product: Optional[str] = Query(None, description="Filter by product"),
    limit: int = Query(50, ge=1, le=500),
    auth: AuditContext = Depends(verify_token)
):
    """
    List batch records with filtering
    """
    batches = pharma_data_generator.generate_batch_records(num_batches=limit)

    # Apply filters
    if status:
        batches = [b for b in batches if b['status'] == status]
    if product:
        batches = [b for b in batches if product.lower() in b['product_name'].lower()]

    return batches


@router.get("/{batch_id}", response_model=dict)
async def get_batch_details(
    batch_id: str,
    auth: AuditContext = Depends(verify_token)
):
    """
    Get detailed batch record including process parameters, quality tests, and deviations
    """
    # Generate realistic batch data
    batches = pharma_data_generator.generate_batch_records(num_batches=10)
    batch = next((b for b in batches if b['batch_id'] == batch_id), None)

    if not batch:
        # Create a synthetic batch for demo
        batch = batches[0]
        batch['batch_id'] = batch_id

    # Add detailed information
    batch['process_parameters'] = {
        "inoculation_density": 0.3,
        "seed_volume": 200.0,
        "working_volume": 1850.0,
        "target_harvest_density": 4.5,
        "culture_duration_hours": 168
    }

    batch['quality_tests'] = [
        {
            "test_id": f"QC-{batch_id}-001",
            "test_name": "Identity (SDS-PAGE)",
            "result": "Pass",
            "tested_by": "QC Analyst 1",
            "tested_at": "2024-12-05T10:00:00Z"
        },
        {
            "test_id": f"QC-{batch_id}-002",
            "test_name": "Purity (HPLC)",
            "result_value": batch['purity_percent'],
            "specification": ">95%",
            "result": "Pass",
            "tested_by": "QC Analyst 2",
            "tested_at": "2024-12-05T14:00:00Z"
        },
        {
            "test_id": f"QC-{batch_id}-003",
            "test_name": "Potency (ELISA)",
            "result_value": batch['potency_percent'],
            "specification": "90-110%",
            "result": "Pass" if 90 <= batch['potency_percent'] <= 110 else "Fail",
            "tested_by": "QC Analyst 3",
            "tested_at": "2024-12-05T16:00:00Z"
        },
        {
            "test_id": f"QC-{batch_id}-004",
            "test_name": "Endotoxin",
            "result_value": 0.15,
            "specification": "<0.5 EU/mL",
            "result": "Pass",
            "tested_by": "QC Analyst 1",
            "tested_at": "2024-12-05T18:00:00Z"
        }
    ]

    batch['material_traceability'] = {
        "cell_line_lot": "CHO-K1-LOT-2024-003",
        "media_lot": "MEDIA-XYZ-2024-089",
        "feed_lot": "FEED-ABC-2024-045",
        "buffer_lots": ["BUF-001-2024", "BUF-002-2024"]
    }

    return batch


@router.get("/{batch_id}/yield-prediction", response_model=dict)
async def predict_batch_yield(
    batch_id: str,
    auth: AuditContext = Depends(verify_token)
):
    """
    Get ML-based yield prediction for ongoing batch
    """
    import random

    predicted_yield = random.uniform(88, 96)
    confidence_low = predicted_yield - random.uniform(2, 4)
    confidence_high = predicted_yield + random.uniform(2, 4)

    return {
        "batch_id": batch_id,
        "predicted_yield_percent": round(predicted_yield, 1),
        "confidence_interval": [round(confidence_low, 1), round(confidence_high, 1)],
        "prediction_timestamp": datetime.now().isoformat(),
        "model_version": "yield-predictor-v1.3",
        "features_used": [
            "cell_density_24h",
            "glucose_consumption_rate",
            "lactate_production_rate",
            "viable_cell_count_48h",
            "temperature_stability",
            "ph_stability"
        ],
        "model_confidence": 0.87,
        "days_until_harvest": 5,
        "recommendation": "Batch progressing well. Maintain current parameters." if predicted_yield > 90 else "Consider feed adjustment to improve yield."
    }


@router.get("/analytics/yield-trends", response_model=dict)
async def get_yield_trends(
    days: int = Query(90, ge=7, le=365),
    product: Optional[str] = Query(None),
    auth: AuditContext = Depends(verify_token)
):
    """
    Get batch yield trends and analytics
    """
    batches = pharma_data_generator.generate_batch_records(num_batches=50)

    yields = [b['yield_percent'] for b in batches if b['yield_percent']]
    avg_yield = sum(yields) / len(yields) if yields else 0

    return {
        "period_days": days,
        "total_batches": len(batches),
        "average_yield": round(avg_yield, 1),
        "min_yield": round(min(yields), 1) if yields else 0,
        "max_yield": round(max(yields), 1) if yields else 0,
        "batches_below_target": len([y for y in yields if y < 90]),
        "target_achievement_rate": round(len([y for y in yields if y >= 90]) / len(yields) * 100, 1) if yields else 0,
        "recent_batches": batches[:10]
    }
