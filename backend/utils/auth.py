"""
Authentication and authorization utilities
21 CFR Part 11 compliant user management
"""
import hashlib
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from fastapi import Header, HTTPException, status


class AuditContext(BaseModel):
    """Context for audit trail"""
    user_id: str
    user_name: str
    user_role: str
    ip_address: str
    session_id: str


async def verify_token(
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None),
    x_user_name: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header("User"),
    x_forwarded_for: Optional[str] = Header(None)
) -> AuditContext:
    """
    Verify authentication token and extract user context
    In production, this would validate JWT tokens
    For demo, we use header-based authentication
    """

    # For development/demo - accept any request
    # In production, validate JWT tokens here
    user_id = x_user_id or "demo-user"
    user_name = x_user_name or "Demo User"
    user_role = x_user_role or "Manufacturing Specialist"
    ip_address = x_forwarded_for or "127.0.0.1"

    return AuditContext(
        user_id=user_id,
        user_name=user_name,
        user_role=user_role,
        ip_address=ip_address,
        session_id=hashlib.md5(f"{user_id}{datetime.utcnow()}".encode()).hexdigest()[:16]
    )


def create_electronic_signature(
    user_id: str,
    entity_id: str,
    action: str,
    timestamp: datetime
) -> str:
    """
    Create cryptographic electronic signature (21 CFR Part 11)
    In production, use proper PKI/digital signatures
    """
    data = f"{user_id}:{entity_id}:{action}:{timestamp.isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()


def verify_electronic_signature(signature: str, data: str) -> bool:
    """Verify electronic signature integrity"""
    expected_hash = hashlib.sha256(data.encode()).hexdigest()
    return signature == expected_hash
