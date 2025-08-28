from fastapi import APIRouter
from backend.schemas.database import (
    DatabaseConfig,
    DatabaseInfo,
    DatabaseSchema,
    ErrorResponse,
    SuccessResponse
)
from backend.interactors.database import (
    switch_database_interactor,
    get_current_database_interactor,
    get_database_schema_interactor
)

router = APIRouter()


@router.post("/switch", response_model=SuccessResponse)
def switch_db(config: DatabaseConfig):
    result = switch_database_interactor(config)
    
    if result["success"]:
        return SuccessResponse(message=result["message"])
    else:
        return ErrorResponse(error=result["error"])



@router.get("/current", response_model=DatabaseInfo)
def get_current_db():
    return get_current_database_interactor()



@router.get("/schema", response_model=DatabaseSchema)
def get_schema():
    result = get_database_schema_interactor()
    
    if result["success"]:
        return DatabaseSchema(schema_data=result["schema"])
    else:
        return ErrorResponse(error=result["error"])