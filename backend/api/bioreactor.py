"""
Bioreactor monitoring API endpoints
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from backend.schemas.bioreactor import (
    BioreactorSensorData,
    BioreactorStatus,
    BioreactorDigitalTwin
)
from backend.utils.synthetic_data import pharma_data_generator
from backend.utils.auth import verify_token, AuditContext

router = APIRouter()


@router.get("/list", response_model=List[BioreactorStatus])
async def list_bioreactors(
    site: Optional[str] = Query(None, description="Filter by manufacturing site"),
    status: Optional[str] = Query(None, description="Filter by status"),
    auth: AuditContext = Depends(verify_token)
):
    """
    List all bioreactors with current status
    """
    bioreactors = [
        BioreactorStatus(
            bioreactor_id="BR-01",
            name="Bioreactor-01",
            status="Operational",
            current_batch_id="B2024-001",
            start_time=datetime.now() - timedelta(days=7),
            estimated_harvest=datetime.now() + timedelta(days=7),
            phase="exponential",
            working_volume=2000.0,
            last_updated=datetime.now()
        ),
        BioreactorStatus(
            bioreactor_id="BR-02",
            name="Bioreactor-02",
            status="Operational",
            current_batch_id="B2024-005",
            start_time=datetime.now() - timedelta(days=3),
            estimated_harvest=datetime.now() + timedelta(days=11),
            phase="lag",
            working_volume=2000.0,
            last_updated=datetime.now()
        ),
        BioreactorStatus(
            bioreactor_id="BR-03",
            name="Bioreactor-03",
            status="Warning",
            current_batch_id=None,
            start_time=None,
            estimated_harvest=None,
            phase=None,
            working_volume=1000.0,
            last_updated=datetime.now()
        ),
        BioreactorStatus(
            bioreactor_id="BR-04",
            name="Bioreactor-04",
            status="Operational",
            current_batch_id="B2024-003",
            start_time=datetime.now() - timedelta(days=10),
            estimated_harvest=datetime.now() + timedelta(days=4),
            phase="stationary",
            working_volume=2000.0,
            last_updated=datetime.now()
        ),
        BioreactorStatus(
            bioreactor_id="BR-05",
            name="Bioreactor-05",
            status="Offline",
            current_batch_id=None,
            start_time=None,
            estimated_harvest=None,
            phase=None,
            working_volume=500.0,
            last_updated=datetime.now()
        ),
    ]

    return bioreactors


@router.get("/{bioreactor_id}/sensors", response_model=List[dict])
async def get_sensor_data(
    bioreactor_id: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of historical data"),
    auth: AuditContext = Depends(verify_token)
):
    """
    Get real-time sensor data for a bioreactor
    Returns CPPs (Critical Process Parameters) and CQAs (Critical Quality Attributes)
    """
    df = pharma_data_generator.generate_bioreactor_timeseries(
        bioreactor_id=bioreactor_id,
        hours=hours,
        interval_minutes=5,
        add_anomalies=True
    )

    return df.to_dict('records')


@router.get("/{bioreactor_id}/digital-twin", response_model=dict)
async def get_digital_twin(
    bioreactor_id: str,
    auth: AuditContext = Depends(verify_token)
):
    """
    Get complete digital twin model of bioreactor
    """
    # Generate recent sensor data
    df = pharma_data_generator.generate_bioreactor_timeseries(
        bioreactor_id=bioreactor_id,
        hours=24,
        interval_minutes=10
    )

    latest_data = df.iloc[-1].to_dict()

    digital_twin = {
        "bioreactor_id": bioreactor_id,
        "physical_model": {
            "working_volume": 2000.0,
            "max_pressure": 1.5,
            "max_temperature": 42.0,
            "heating_cooling_capacity_kw": 50,
            "agitation_system": "Rushton turbines",
            "sparger_type": "ring sparger",
            "vessel_material": "316L stainless steel",
            "sensor_count": 25,
            "manufacturer": "Sartorius",
            "model": "BIOSTAT STR 2000"
        },
        "process_state": {
            "current_batch": "B2024-001",
            "inoculation_date": (datetime.now() - timedelta(days=7)).isoformat(),
            "estimated_harvest": (datetime.now() + timedelta(days=7)).isoformat(),
            "phase": latest_data.get('phase', 'exponential'),
            "current_volume": 1850.0,
            "cell_line": "CHO-K1",
            "product": "mAb-A"
        },
        "maintenance_history": {
            "last_cip": (datetime.now() - timedelta(days=15)).isoformat(),
            "last_sip": (datetime.now() - timedelta(days=14)).isoformat(),
            "impeller_replacement": (datetime.now() - timedelta(days=60)).isoformat(),
            "ph_probe_calibration": (datetime.now() - timedelta(days=7)).isoformat(),
            "do_probe_calibration": (datetime.now() - timedelta(days=7)).isoformat(),
            "next_validation": (datetime.now() + timedelta(days=30)).isoformat()
        },
        "current_sensors": {
            "temperature": latest_data.get('temperature'),
            "ph": latest_data.get('ph'),
            "dissolved_oxygen": latest_data.get('dissolved_oxygen'),
            "agitation_rpm": latest_data.get('agitation_rpm'),
            "pressure": latest_data.get('pressure'),
            "cell_density": latest_data.get('cell_density'),
            "viable_cell_count": latest_data.get('viable_cell_count'),
            "glucose": latest_data.get('glucose'),
            "lactate": latest_data.get('lactate')
        },
        "health_score": 94.5,
        "alerts": [
            {
                "severity": "info",
                "message": "Glucose feeding scheduled in 2 hours",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "predictions": {
            "estimated_peak_density": 4.8,
            "estimated_peak_time": (datetime.now() + timedelta(hours=48)).isoformat(),
            "predicted_yield_percent": 93.2,
            "contamination_risk": 0.05
        }
    }

    return digital_twin


@router.get("/{bioreactor_id}/current", response_model=dict)
async def get_current_status(
    bioreactor_id: str,
    auth: AuditContext = Depends(verify_token)
):
    """
    Get current real-time status of bioreactor (for dashboard)
    """
    df = pharma_data_generator.generate_bioreactor_timeseries(
        bioreactor_id=bioreactor_id,
        hours=1,
        interval_minutes=5
    )

    latest = df.iloc[-1].to_dict()

    # Check if parameters are within specification
    temp_ok = 36.9 <= latest['temperature'] <= 37.1
    ph_ok = 6.95 <= latest['ph'] <= 7.05
    do_ok = 40 <= latest['dissolved_oxygen'] <= 50

    return {
        "bioreactor_id": bioreactor_id,
        "timestamp": latest['timestamp'].isoformat(),
        "status": "Operational" if (temp_ok and ph_ok and do_ok) else "Warning",
        "phase": latest['phase'],
        "cpps": {
            "temperature": {
                "value": latest['temperature'],
                "unit": "°C",
                "spec_min": 36.9,
                "spec_max": 37.1,
                "in_spec": temp_ok
            },
            "ph": {
                "value": latest['ph'],
                "unit": "pH",
                "spec_min": 6.95,
                "spec_max": 7.05,
                "in_spec": ph_ok
            },
            "dissolved_oxygen": {
                "value": latest['dissolved_oxygen'],
                "unit": "%",
                "spec_min": 40,
                "spec_max": 50,
                "in_spec": do_ok
            },
            "agitation_rpm": {
                "value": latest['agitation_rpm'],
                "unit": "RPM",
                "spec_min": 115,
                "spec_max": 125,
                "in_spec": True
            }
        },
        "cqas": {
            "cell_density": {
                "value": latest['cell_density'],
                "unit": "OD600"
            },
            "viable_cell_count": {
                "value": latest['viable_cell_count'],
                "unit": "cells/mL"
            }
        }
    }
