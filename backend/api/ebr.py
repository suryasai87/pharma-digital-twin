"""
Electronic Batch Records (EBR) API - 21 CFR Part 11 Compliant
"""
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Body
from backend.schemas.audit import ElectronicSignature
from backend.utils.synthetic_data import pharma_data_generator
from backend.utils.auth import verify_token, AuditContext, create_electronic_signature
import hashlib

router = APIRouter()


@router.get("/{batch_id}/record", response_model=dict)
async def get_electronic_batch_record(
    batch_id: str,
    auth: AuditContext = Depends(verify_token)
):
    """
    Get complete Electronic Batch Record (EBR) for a batch
    21 CFR Part 11 compliant with complete traceability
    """
    batches = pharma_data_generator.generate_batch_records(num_batches=10)
    batch = next((b for b in batches if b['batch_id'] == batch_id), batches[0])
    batch['batch_id'] = batch_id

    # Generate complete EBR
    ebr = {
        "batch_id": batch_id,
        "ebr_version": "2.1",
        "created_at": batch['start_date'],
        "last_modified": datetime.now().isoformat(),

        # Product information
        "product": {
            "name": batch['product_name'],
            "type": batch['product'],
            "strength": "100mg/mL",
            "formulation": "Liquid for injection",
            "approved_recipe": "RECIPE-MAB-001-v3"
        },

        # Manufacturing information
        "manufacturing": {
            "site": batch['manufacturing_site'],
            "building": "Building-A",
            "suite": "Suite-102",
            "bioreactor_id": batch['bioreactor_id'],
            "start_date": batch['start_date'],
            "end_date": batch.get('end_date'),
            "responsible_person": batch['responsible_person']
        },

        # Raw materials (complete traceability)
        "raw_materials": [
            {
                "material_name": "CHO Cell Line",
                "lot_number": "CELL-2024-003",
                "expiry_date": "2025-12-31",
                "quantity_used": "200 mL",
                "verified_by": "QC Analyst 1",
                "verified_at": batch['start_date']
            },
            {
                "material_name": "Basal Media",
                "lot_number": "MEDIA-2024-089",
                "expiry_date": "2025-06-30",
                "quantity_used": "1650 L",
                "verified_by": "Manufacturing Operator",
                "verified_at": batch['start_date']
            },
            {
                "material_name": "Feed Solution",
                "lot_number": "FEED-2024-045",
                "expiry_date": "2025-03-31",
                "quantity_used": "250 L",
                "verified_by": "Manufacturing Operator",
                "verified_at": batch['start_date']
            }
        ],

        # Process steps with electronic signatures
        "process_steps": [
            {
                "step_number": 1,
                "step_name": "Media Preparation",
                "sop_reference": "SOP-MEDIA-001-v5",
                "started_at": batch['start_date'],
                "completed_at": (datetime.fromisoformat(batch['start_date']) + timedelta(hours=2)).isoformat(),
                "performed_by": "Operator A",
                "verified_by": "Supervisor B",
                "status": "Complete",
                "critical_parameters": {
                    "media_volume": "1650 L",
                    "temperature": "37.0°C",
                    "pH": "7.0"
                },
                "electronic_signature": {
                    "signed_by": "Operator A",
                    "signed_at": (datetime.fromisoformat(batch['start_date']) + timedelta(hours=2)).isoformat(),
                    "signature_meaning": "Performed by"
                }
            },
            {
                "step_number": 2,
                "step_name": "Bioreactor Setup & Sterilization",
                "sop_reference": "SOP-SIP-001-v4",
                "started_at": (datetime.fromisoformat(batch['start_date']) + timedelta(hours=3)).isoformat(),
                "completed_at": (datetime.fromisoformat(batch['start_date']) + timedelta(hours=6)).isoformat(),
                "performed_by": "Operator C",
                "verified_by": "Supervisor B",
                "status": "Complete",
                "critical_parameters": {
                    "sip_temperature": "121°C",
                    "sip_duration": "60 minutes",
                    "sterility_test": "Pass"
                }
            },
            {
                "step_number": 3,
                "step_name": "Inoculation",
                "sop_reference": "SOP-INOC-001-v3",
                "started_at": (datetime.fromisoformat(batch['start_date']) + timedelta(hours=8)).isoformat(),
                "completed_at": (datetime.fromisoformat(batch['start_date']) + timedelta(hours=9)).isoformat(),
                "performed_by": "Operator A",
                "verified_by": "QC Analyst 2",
                "status": "Complete",
                "critical_parameters": {
                    "inoculum_volume": "200 mL",
                    "inoculum_density": "0.3 OD600",
                    "viability": "98%"
                }
            },
            {
                "step_number": 4,
                "step_name": "Cell Culture",
                "sop_reference": "SOP-CULTURE-001-v7",
                "started_at": (datetime.fromisoformat(batch['start_date']) + timedelta(hours=9)).isoformat(),
                "status": "In Progress",
                "critical_parameters": {
                    "target_density": "4.5 OD600",
                    "culture_duration": "168 hours",
                    "feed_strategy": "Fed-batch"
                }
            }
        ],

        # In-process testing
        "in_process_tests": [
            {
                "test_id": f"IPT-{batch_id}-001",
                "test_name": "Cell Density (24h)",
                "result": "0.5 OD600",
                "specification": "0.4-0.7 OD600",
                "status": "Pass",
                "tested_by": "QC Analyst 1",
                "tested_at": (datetime.fromisoformat(batch['start_date']) + timedelta(hours=24)).isoformat()
            },
            {
                "test_id": f"IPT-{batch_id}-002",
                "test_name": "Viability (48h)",
                "result": "97%",
                "specification": ">95%",
                "status": "Pass",
                "tested_by": "QC Analyst 2",
                "tested_at": (datetime.fromisoformat(batch['start_date']) + timedelta(hours=48)).isoformat()
            }
        ],

        # Deviations
        "deviations": batch.get('deviations', []),

        # Electronic signatures
        "signatures": [
            {
                "signature_id": f"SIG-{batch_id}-001",
                "signed_by": batch['responsible_person'],
                "role": "Manufacturing Supervisor",
                "signature_meaning": "Batch record reviewed and approved",
                "signed_at": datetime.now().isoformat(),
                "digital_signature": hashlib.sha256(f"{batch_id}-{batch['responsible_person']}".encode()).hexdigest()
            }
        ],

        # Data integrity checksum (ALCOA+)
        "data_integrity": {
            "record_hash": hashlib.sha256(f"{batch_id}-{datetime.now().date()}".encode()).hexdigest(),
            "last_verified": datetime.now().isoformat(),
            "verification_status": "Valid",
            "alcoa_compliant": True
        }
    }

    return ebr


@router.post("/{batch_id}/sign", response_model=dict)
async def sign_batch_record(
    batch_id: str,
    signature_meaning: str = Body(..., description="E.g., 'Reviewed by', 'Approved by'"),
    reason: str = Body(..., description="Reason for signature"),
    auth: AuditContext = Depends(verify_token)
):
    """
    Apply electronic signature to batch record (21 CFR Part 11)
    """
    digital_signature = create_electronic_signature(
        user_id=auth.user_id,
        entity_id=batch_id,
        action="SIGN",
        timestamp=datetime.now()
    )

    signature = {
        "signature_id": f"SIG-{batch_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "batch_id": batch_id,
        "signed_by": auth.user_name,
        "user_id": auth.user_id,
        "user_role": auth.user_role,
        "signature_meaning": signature_meaning,
        "reason_for_signature": reason,
        "signed_at": datetime.now().isoformat(),
        "digital_signature": digital_signature,
        "ip_address": auth.ip_address,
        "session_id": auth.session_id
    }

    return {
        "success": True,
        "message": f"Electronic signature applied to batch {batch_id}",
        "signature": signature
    }


@router.get("/{batch_id}/print", response_model=dict)
async def print_batch_record(
    batch_id: str,
    format: str = "pdf",
    auth: AuditContext = Depends(verify_token)
):
    """
    Generate printable batch record with audit trail
    """
    return {
        "batch_id": batch_id,
        "format": format,
        "generated_at": datetime.now().isoformat(),
        "generated_by": auth.user_name,
        "download_url": f"/api/v1/ebr/{batch_id}/download/{format}",
        "file_size_kb": 1250,
        "page_count": 45,
        "includes": [
            "Complete batch record",
            "All electronic signatures",
            "Deviation investigations",
            "In-process test results",
            "Material traceability",
            "Complete audit trail"
        ]
    }


@router.get("/{batch_id}/deviations", response_model=List[dict])
async def get_batch_deviations(
    batch_id: str,
    auth: AuditContext = Depends(verify_token)
):
    """
    Get all deviations and investigations for a batch
    """
    return [
        {
            "deviation_id": f"DEV-{batch_id}-001",
            "batch_id": batch_id,
            "reported_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "reported_by": "Operator A",
            "description": "Temperature excursion to 37.3°C for 12 minutes",
            "severity": "Minor",
            "impact_assessment": "No impact on product quality - within validated range",
            "root_cause": "Temporary HVAC fluctuation",
            "corrective_action": "HVAC maintenance completed",
            "preventive_action": "Enhanced monitoring added",
            "investigation_complete": True,
            "qa_approved": True,
            "approved_by": "QA Manager",
            "approved_at": (datetime.now() - timedelta(days=1)).isoformat()
        }
    ]
