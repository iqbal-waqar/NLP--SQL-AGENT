from fastapi import FastAPI
from dotenv import load_dotenv
from backend.routes import query, database
from backend.utils.db_manager import apply_database_config

load_dotenv()

apply_database_config()

app = FastAPI()

app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(database.router, prefix="/database", tags=["Database"])
