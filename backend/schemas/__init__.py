"""
Pydantic schemas for the SQL Agent API.

This module contains all the Pydantic models used for request/response validation
across the different API endpoints.
"""

from .database import (
    DatabaseConfig,
    DatabaseInfo,
    DatabaseSchema,
    ErrorResponse,
    SuccessResponse
)
from .query import (
    QueryRequest,
    QueryResponse
)

__all__ = [
    "DatabaseConfig",
    "DatabaseInfo", 
    "DatabaseSchema",
    "ErrorResponse",
    "SuccessResponse",
    "QueryRequest",
    "QueryResponse"
]