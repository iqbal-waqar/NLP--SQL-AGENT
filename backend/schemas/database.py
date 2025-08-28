from pydantic import BaseModel, Field
from typing import Optional

class DatabaseConfig(BaseModel):
    db_name: str
    db_user: Optional[str] = None
    db_pass: Optional[str] = None
    db_host: Optional[str] = None
    db_port: Optional[int] = None

class DatabaseInfo(BaseModel):
    host: str
    port: str
    user: str
    database: str

class DatabaseSchema(BaseModel):
    schema_data: str

class ErrorResponse(BaseModel):
    error: str

class SuccessResponse(BaseModel):
    message: str