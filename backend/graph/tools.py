import os
import psycopg2
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

_last_sql_query = None
_schema_cache = None

def get_database_connection():
    dbname = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    
    if not all([dbname, user, password, host, port]):
        missing = [var for var, val in [
            ("DB_NAME", dbname), ("DB_USER", user), ("DB_PASS", password),
            ("DB_HOST", host), ("DB_PORT", port)
        ] if not val]
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    return psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port,
    )

def discover_database_schema():
    global _schema_cache
    
    if _schema_cache:
        return _schema_cache
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    schema_info = {
        "tables": {},
        "relationships": []
    }
    
    try:
        schema_name = os.getenv("DB_SCHEMA", "public")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
        """, (schema_name,))
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = '{table}'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            schema_info["tables"][table] = {
                "columns": [{"name": col[0], "type": col[1], "nullable": col[2], "default": col[3]} for col in columns]
            }
        
        cursor.execute("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
        """)
        
        relationships = cursor.fetchall()
        for rel in relationships:
            schema_info["relationships"].append({
                "from_table": rel[0],
                "from_column": rel[1],
                "to_table": rel[2],
                "to_column": rel[3]
            })
    
    except Exception as e:
        print(f"Error discovering schema: {e}")
    
    finally:
        cursor.close()
        conn.close()
    
    _schema_cache = schema_info
    return schema_info

@tool("get_database_schema")
def get_database_schema(query: str = "schema") -> str:
    """
    ALWAYS USE THIS TOOL FIRST! Discovers and returns the complete database schema including tables, columns, and relationships.
    This is essential to understand the database structure before writing any SQL queries.
    
    Input: Any string (ignored, just for compatibility)
    Output: Complete database schema information with tables, columns, and relationships
    """
    schema = discover_database_schema()
    
    schema_description = "DATABASE SCHEMA:\n\n"
    
    for table_name, table_info in schema["tables"].items():
        schema_description += f"Table: {table_name}\n"
        for col in table_info["columns"]:
            schema_description += f"  - {col['name']} ({col['type']})\n"
        schema_description += "\n"
    
    if schema["relationships"]:
        schema_description += "FOREIGN KEY RELATIONSHIPS:\n"
        for rel in schema["relationships"]:
            schema_description += f"  - {rel['from_table']}.{rel['from_column']} -> {rel['to_table']}.{rel['to_column']}\n"
        schema_description += "\n"
    
    schema_description += "\nCOMMON QUERY PATTERNS:\n"
    
    tables = list(schema["tables"].keys())
    relationships = schema["relationships"]
    
    if len(tables) > 0:
        schema_description += f"- Count records: SELECT COUNT(*) FROM {tables[0]}\n"
        
        if relationships:
            for rel in relationships[:2]:  
                from_table = rel["from_table"]
                to_table = rel["to_table"]
                from_col = rel["from_column"]
                to_col = rel["to_column"]
                schema_description += f"- Join {from_table} with {to_table}: SELECT * FROM {from_table} f JOIN {to_table} t ON f.{from_col} = t.{to_col}\n"
        
        first_table = tables[0]
        columns = schema["tables"][first_table]["columns"]
        if columns:
            first_col = columns[0]["name"]
            schema_description += f"- Filter data: SELECT * FROM {first_table} WHERE {first_col} = 'value'\n"
    
    schema_description += "\nNOTE: Use the exact table and column names shown above in your SQL queries.\n"
    
    return schema_description

@tool("execute_sql", return_direct=True)
def execute_sql(sql_query: str) -> str:
    """
    Executes a SQL query on the connected database and returns results.
    
    IMPORTANT: Always use get_database_schema tool first to understand the database structure
    before writing SQL queries. This ensures you use correct table names, column names, and relationships.
    
    Input: SQL query as string (without backticks or markdown formatting).
    Output: Query results as string.
    """
    global _last_sql_query
    
    cleaned_query = sql_query.strip()
    if cleaned_query.startswith('`') and cleaned_query.endswith('`'):
        cleaned_query = cleaned_query[1:-1].strip()
    
    _last_sql_query = cleaned_query
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(cleaned_query)
        try:
            result = cursor.fetchall()
        except psycopg2.ProgrammingError:
            result = "Query executed successfully, no results to fetch."
    except Exception as e:
        result = f"Error executing query: {str(e)}"
    finally:
        cursor.close()
        conn.close()
    
    return str(result)

def get_last_sql_query():
    return _last_sql_query

def clear_schema_cache():
    global _schema_cache
    _schema_cache = None
