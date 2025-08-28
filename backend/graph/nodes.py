import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import END
from backend.graph.tools import execute_sql, get_database_schema

load_dotenv()

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.0,
    max_tokens=1000
)

tools = [get_database_schema, execute_sql]
llm_with_tools = llm.bind_tools(tools)

system_message = SystemMessage(content="""You are a SQL expert assistant. When answering questions about data:

WORKFLOW:
1. ALWAYS start by using the get_database_schema tool to understand the database structure
2. Pay careful attention to which table contains which columns and their relationships
3. Use proper JOINs when data spans multiple tables based on foreign key relationships
4. Use the exact table and column names shown in the schema
5. Generate efficient SQL queries based on the discovered schema
6. ALWAYS execute the SQL query using execute_sql tool and provide the actual results

CRITICAL QUERY REQUIREMENTS:
- When asked about "customers", always include customer names (first_name, last_name) by joining with the customers table
- When asked about "products", always include product names by joining with the products table  
- When asked about "orders", include relevant details like order_date, total_amount
- Always provide meaningful, human-readable results, not just IDs
- When using GROUP BY with JOINs, include all non-aggregate columns in the GROUP BY clause

WORKFLOW RULES:
- Call get_database_schema ONLY ONCE at the beginning to understand the structure
- After getting the schema, immediately proceed to execute_sql with your query
- Do NOT call get_database_schema multiple times for the same question
- Be consistent in your approach for similar questions

EXAMPLE PATTERNS:
- Customers with multiple orders: SELECT c.first_name, c.last_name, COUNT(o.order_id) FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id, c.first_name, c.last_name HAVING COUNT(o.order_id) > 1

Remember: Always provide the final answer based on the actual query results, not just the query itself.""")

def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return END

def call_model(state):
    messages = state["messages"]
    
    if not any(isinstance(msg, SystemMessage) for msg in messages):
        messages = [system_message] + messages
    
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def check_greeting_or_irrelevant(state):
    messages = state["messages"]
    if not messages:
        return state
        
    human_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]
    if not human_messages:
        return state
        
    question = human_messages[-1].content.lower().strip()
    
    greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'how are you']
    
    irrelevant_patterns = ['weather', 'joke', 'story', 'recipe', 'movie', 'music', 'sports', 'news']
    
    if any(greeting in question for greeting in greetings):
        response = AIMessage(content="Hello! I'm a SQL agent specialized in database queries. Please ask me questions about your data and I'll help you write and execute SQL queries.")
        return {"messages": [response]}
    
    if any(pattern in question for pattern in irrelevant_patterns) or len(question) < 3:
        response = AIMessage(content="I'm a SQL agent and can only help with database queries and data analysis. Please ask me questions about your data.")
        return {"messages": [response]}
    
    return state