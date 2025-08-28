from backend.graph.agent import run_agent
from backend.graph.answer import generate_answer
from backend.graph.tools import get_last_sql_query

def process_user_query(question: str):
    response = run_agent(question)
    
    sql_query = get_last_sql_query() or "UNKNOWN"
    
    answer = generate_answer(question, sql_query, response)
    return sql_query, answer
