"""
Pydantic schemas for audit trail (21 CFR Part 11 compliance)
"""
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class AuditAction(str, Enum):
    """Audit action types"""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    SIGN = "ELECTRONIC_SIGNATURE"


class AuditSeverity(str, Enum):
    """Audit event severity"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AuditLog(BaseModel):
    """Immutable audit log entry (21 CFR Part 11)"""
    audit_id: str = Field(..., description="Unique audit event ID")
    timestamp: datetime = Field(..., description="Event timestamp (NTP synchronized)")

    # User information (Attributable)
    user_id: str
    user_name: str
    user_role: str

    # Action details (Legible, Original)
    action: AuditAction
    entity_type: str = Field(..., description="batch, bioreactor, equipment, etc.")
    entity_id: str

    # Change tracking (Accurate, Complete, Consistent)
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    change_reason: Optional[str] = None

    # Context (Contemporaneous)
    ip_address: str
    session_id: str
    severity: AuditSeverity = AuditSeverity.INFO

    # Regulatory (Enduring, Available)
    retention_until: datetime = Field(..., description="Must retain for 10+ years")
    hash_signature: str = Field(..., description="Cryptographic hash for integrity")

    class Config:
        json_schema_extra = {
            "example": {
                "audit_id": "AUD-2024-000123",
                "timestamp": "2024-12-05T14:30:00.123456Z",
                "user_id": "USR-001",
                "user_name": "Jane Doe",
                "user_role": "Manufacturing Specialist",
                "action": "UPDATE",
                "entity_type": "batch",
                "entity_id": "B2024-001",
                "old_value": {"temperature": 36.9},
                "new_value": {"temperature": 37.0},
                "change_reason": "Temperature adjustment per SOP-123",
                "ip_address": "10.0.1.45",
                "session_id": "sess_abc123",
                "severity": "INFO"
            }
        }


class ElectronicSignature(BaseModel):
    """Electronic signature record (21 CFR Part 11)"""
    signature_id: str
    batch_id: str
    signed_by: str
    signature_meaning: str = Field(..., description="Reviewed by, Approved by, Released by")
    signed_at: datetime
    digital_signature: str = Field(..., description="Cryptographic signature")
    reason_for_signature: str


class DataIntegrityCheck(BaseModel):
    """ALCOA+ data integrity verification"""
    check_id: str
    entity_type: str
    entity_id: str
    checked_at: datetime

    # ALCOA+ principles
    attributable: bool = Field(..., description="User identified?")
    legible: bool = Field(..., description="Readable and permanent?")
    contemporaneous: bool = Field(..., description="Recorded in real-time?")
    original: bool = Field(..., description="Original data or certified copy?")
    accurate: bool = Field(..., description="Data accurate and validated?")
    complete: bool = Field(..., description="All data included?")
    consistent: bool = Field(..., description="Chronologically sound?")
    enduring: bool = Field(..., description="Preserved throughout lifecycle?")
    available: bool = Field(..., description="Accessible for review?")

    overall_compliance: bool
    issues_found: List[str] = []
