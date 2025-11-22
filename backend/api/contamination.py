"""
Contamination detection API endpoints
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from backend.utils.synthetic_data import pharma_data_generator
from backend.utils.auth import verify_token, AuditContext

router = APIRouter()


@router.get("/alerts", response_model=List[dict])
async def get_contamination_alerts(
    status: Optional[str] = Query(None, description="Filter by risk status"),
    bioreactor_id: Optional[str] = Query(None, description="Filter by bioreactor"),
    limit: int = Query(20, ge=1, le=100),
    auth: AuditContext = Depends(verify_token)
):
    """
    Get contamination detection alerts from ML model
    """
    alerts = pharma_data_generator.generate_contamination_alerts(num_alerts=limit)

    # Apply filters
    if status:
        alerts = [a for a in alerts if a['status'] == status]
    if bioreactor_id:
        alerts = [a for a in alerts if a['bioreactor'] == bioreactor_id]

    return alerts


@router.get("/realtime-risk/{bioreactor_id}", response_model=dict)
async def get_realtime_risk(
    bioreactor_id: str,
    auth: AuditContext = Depends(verify_token)
):
    """
    Get real-time contamination risk score for a bioreactor
    """
    import random

    risk_score = random.betavariate(2, 8)  # Skewed toward low values

    if risk_score < 0.3:
        risk_level = "Low"
        action = "Continue monitoring"
    elif risk_score < 0.7:
        risk_level = "Medium"
        action = "Investigate sensor patterns"
    else:
        risk_level = "High"
        action = "Immediate sampling and testing required"

    return {
        "bioreactor_id": bioreactor_id,
        "timestamp": datetime.now().isoformat(),
        "risk_score": round(risk_score, 3),
        "risk_level": risk_level,
        "recommended_action": action,
        "model_version": "contamination-detector-v2.1",
        "confidence": round(random.uniform(0.75, 0.95), 2),
        "contributing_factors": [
            {"factor": "pH stability", "contribution": 0.35},
            {"factor": "Cell morphology", "contribution": 0.25},
            {"factor": "Metabolite profile", "contribution": 0.20},
            {"factor": "Dissolved oxygen trend", "contribution": 0.15},
            {"factor": "Temperature variance", "contribution": 0.05}
        ],
        "historical_context": {
            "avg_risk_7d": round(random.uniform(0.1, 0.3), 2),
            "max_risk_7d": round(random.uniform(0.3, 0.6), 2),
            "contamination_events_90d": 0
        }
    }


@router.get("/analytics/summary", response_model=dict)
async def get_contamination_summary(
    days: int = Query(30, ge=7, le=90),
    auth: AuditContext = Depends(verify_token)
):
    """
    Get contamination analytics summary
    """
    alerts = pharma_data_generator.generate_contamination_alerts(num_alerts=50)

    high_risk = len([a for a in alerts if a['status'] == 'High'])
    medium_risk = len([a for a in alerts if a['status'] == 'Medium'])
    low_risk = len([a for a in alerts if a['status'] == 'Low'])

    return {
        "period_days": days,
        "total_alerts": len(alerts),
        "risk_distribution": {
            "high": high_risk,
            "medium": medium_risk,
            "low": low_risk
        },
        "contamination_events": 0,
        "false_positive_rate": 0.02,
        "model_accuracy": 0.96,
        "avg_risk_score": round(sum(a['risk_score'] for a in alerts) / len(alerts), 3) if alerts else 0,
        "bioreactor_risk_ranking": [
            {"bioreactor": "BR-04", "avg_risk": 0.45, "alert_count": 8},
            {"bioreactor": "BR-01", "avg_risk": 0.32, "alert_count": 5},
            {"bioreactor": "BR-02", "avg_risk": 0.18, "alert_count": 3},
            {"bioreactor": "BR-03", "avg_risk": 0.12, "alert_count": 2},
            {"bioreactor": "BR-05", "avg_risk": 0.08, "alert_count": 1}
        ]
    }
