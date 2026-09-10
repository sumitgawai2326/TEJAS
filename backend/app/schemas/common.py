"""
Common Schemas & Standard Error Definitions.
"""
from typing import Optional
import datetime
from pydantic import BaseModel, Field
from app.core.errors import ErrorCode

class ErrorResponse(BaseModel):
    code: ErrorCode = Field(..., description="Standardized error code")
    message: str = Field(..., description="Human-readable error description")
    details: Optional[str] = Field(None, description="Detailed diagnostic or troubleshooting advice")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
