from fastapi import APIRouter
from backend.schemas.query import QueryRequest, QueryResponse
from backend.interactors.nlp import process_user_query

router = APIRouter()

@router.post("/ask", response_model=QueryResponse)
def ask_db(query: QueryRequest):
    sql_query, answer = process_user_query(query.question)
    return QueryResponse(sql_query=sql_query, answer=answer)
