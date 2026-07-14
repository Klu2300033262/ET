from pydantic import BaseModel, Field
from typing import Any, Dict, Generic, Optional, TypeVar

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    """Standardized API response structure."""
    success: bool = Field(..., description="Indicates if the request was successful")
    message: str = Field(..., description="A brief human-readable message")
    data: Optional[T] = Field(None, description="The payload data (if any)")

class ErrorResponse(BaseModel):
    """Standardized error response structure."""
    success: bool = Field(False, description="Always False for errors")
    message: str = Field(..., description="Error summary")
    detail: Optional[Any] = Field(None, description="Detailed error information or validation errors")
