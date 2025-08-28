from backend.utils.db_manager import switch_database, get_current_database_info
from backend.graph.tools import get_database_schema
from backend.schemas.database import DatabaseConfig

def switch_database_interactor(config: DatabaseConfig):
    try:
        switch_database(
            db_name=config.db_name,
            db_user=config.db_user,
            db_pass=config.db_pass,
            db_host=config.db_host,
            db_port=config.db_port
        )
        return {"success": True, "message": f"Successfully switched to database: {config.db_name}"}
    except Exception as e:
        return {"success": False, "error": f"Failed to switch database: {str(e)}"}

def get_current_database_interactor():
    return get_current_database_info()

def get_database_schema_interactor():
    try:
        schema = get_database_schema.invoke({"query": "schema"})
        return {"success": True, "schema": schema}
    except Exception as e:
        return {"success": False, "error": f"Failed to get schema: {str(e)}"}