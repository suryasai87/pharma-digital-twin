"""
Equipment and predictive maintenance API endpoints
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from backend.utils.synthetic_data import pharma_data_generator
from backend.utils.auth import verify_token, AuditContext

router = APIRouter()


@router.get("/list", response_model=List[dict])
async def list_equipment(
    status: Optional[str] = Query(None, description="Filter by status"),
    equipment_type: Optional[str] = Query(None, description="Filter by type"),
    auth: AuditContext = Depends(verify_token)
):
    """
    List all equipment with health status
    """
    equipment_list = pharma_data_generator.generate_equipment_health(num_equipment=15)

    # Apply filters
    if status:
        equipment_list = [e for e in equipment_list if e['status'] == status]
    if equipment_type:
        equipment_list = [e for e in equipment_list if equipment_type.lower() in e['type'].lower()]

    return equipment_list


@router.get("/{equipment_id}/health", response_model=dict)
async def get_equipment_health(
    equipment_id: str,
    auth: AuditContext = Depends(verify_token)
):
    """
    Get detailed health metrics and predictive maintenance data
    """
    import random

    health_score = random.uniform(65, 98)

    if health_score >= 85:
        status = "Operational"
        maintenance_urgency = "Low"
        days_until_maintenance = random.randint(30, 90)
    elif health_score >= 70:
        status = "Warning"
        maintenance_urgency = "Medium"
        days_until_maintenance = random.randint(7, 30)
    else:
        status = "Critical"
        maintenance_urgency = "High"
        days_until_maintenance = random.randint(1, 7)

    return {
        "equipment_id": equipment_id,
        "health_score": round(health_score, 1),
        "status": status,
        "maintenance_urgency": maintenance_urgency,
        "predicted_failure_probability": round((100 - health_score) / 100, 2),
        "days_until_maintenance": days_until_maintenance,
        "health_metrics": {
            "vibration_level": round(random.uniform(0.5, 3.0), 2),
            "temperature_deviation": round(random.uniform(0, 5), 1),
            "cycles_since_maintenance": random.randint(50, 500),
            "runtime_hours": random.randint(1000, 10000),
            "error_count_7d": random.randint(0, 5)
        },
        "maintenance_history": [
            {
                "date": (datetime.now() - timedelta(days=45)).isoformat(),
                "type": "Preventive Maintenance",
                "description": "Routine inspection and calibration",
                "performed_by": "Maintenance Tech A"
            },
            {
                "date": (datetime.now() - timedelta(days=90)).isoformat(),
                "type": "Corrective Maintenance",
                "description": "Replaced temperature sensor",
                "performed_by": "Maintenance Tech B"
            }
        ],
        "recommendations": [
            "Schedule preventive maintenance within next 30 days",
            "Monitor vibration levels closely",
            "Consider sensor recalibration"
        ] if health_score < 85 else ["Equipment operating normally"]
    }


@router.get("/predictive-maintenance/alerts", response_model=List[dict])
async def get_maintenance_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    auth: AuditContext = Depends(verify_token)
):
    """
    Get predictive maintenance alerts
    """
    equipment_list = pharma_data_generator.generate_equipment_health(num_equipment=15)

    alerts = []
    for eq in equipment_list:
        if eq['health_score'] < 85:
            severity_level = "Critical" if eq['health_score'] < 70 else "Warning"

            alerts.append({
                "alert_id": f"PM-{eq['equipment_id']}-{datetime.now().strftime('%Y%m%d')}",
                "equipment_id": eq['equipment_id'],
                "equipment_name": eq['name'],
                "severity": severity_level,
                "health_score": eq['health_score'],
                "predicted_failure_days": 7 if severity_level == "Critical" else 30,
                "message": f"{eq['name']} requires attention - Health score: {eq['health_score']}",
                "created_at": datetime.now().isoformat(),
                "acknowledged": False
            })

    # Apply filter
    if severity:
        alerts = [a for a in alerts if a['severity'] == severity]

    return sorted(alerts, key=lambda x: x['health_score'])
