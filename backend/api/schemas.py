from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for context")


class AuditRequest(BaseModel):
    """Audit request schema"""
    model_path: str = Field(..., description="HuggingFace ID or local path")
    mode: str = Field("standard", description="Audit mode: quick, standard, or deep")


class AuditResponse(BaseModel):
    """Audit response schema"""
    verdict: str = Field(..., description="MATCH, NO_MATCH, SUSPICIOUS, or ERROR")
    confidence: float = Field(..., description="Confidence percentage (0-100)")
    matches: Optional[int] = Field(None, description="Number of matching fingerprints")
    total_tested: Optional[int] = Field(None, description="Total fingerprints tested")
    mode: str = Field(..., description="Audit mode used")
    duration_seconds: float = Field(..., description="Audit duration")
    model_path: str = Field(..., description="Audited model path")
    timestamp: Optional[float] = Field(None, description="Unix timestamp")
    error: Optional[str] = Field(None, description="Error message if any")


class FingerprintGenerateRequest(BaseModel):
    """Fingerprint generation request"""
    num_fingerprints: int = Field(100, ge=10, le=10000, description="Number of fingerprints")
    key_length: int = Field(32, ge=8, le=100, description="Key phrase length")
    response_length: int = Field(32, ge=8, le=100, description="Response phrase length")