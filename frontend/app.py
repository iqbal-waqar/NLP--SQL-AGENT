import streamlit as st
import requests
import json
import time
import re
from typing import Dict, Any

st.set_page_config(
    page_title="🤖 SQL Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #1e2130;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background-color: #262730;
        color: white;
        border: 1px solid #4a4a4a;
        border-radius: 8px;
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        background-color: #262730;
        color: white;
        border: 1px solid #4a4a4a;
        border-radius: 8px;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #00d4aa;
        color: black;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #00b894;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 212, 170, 0.3);
    }
    
    /* Success message */
    .success-box {
        background-color: #1e3a2e;
        border: 1px solid #00d4aa;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Error message */
    .error-box {
        background-color: #3a1e1e;
        border: 1px solid #ff6b6b;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Code block styling */
    .stCode {
        background-color: #1a1a1a !important;
        border: 1px solid #4a4a4a;
        border-radius: 8px;
    }
    
    /* Metric styling */
    .css-1xarl3l {
        background-color: #262730;
        border: 1px solid #4a4a4a;
        border-radius: 8px;
        padding: 10px;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #00d4aa, #74b9ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .info-card {
        background-color: #1e2130;
        border: 1px solid #4a4a4a;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Animation for loading */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .loading {
        animation: pulse 1.5s infinite;
    }
</style>
""", unsafe_allow_html=True)

API_BASE_URL = "http://localhost:8000"

def make_api_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": f"API Error: {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "❌ Cannot connect to API. Make sure the FastAPI server is running on http://localhost:8000"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "⏱️ Request timed out. The query might be taking too long."}
    except Exception as e:
        return {"success": False, "error": f"❌ Unexpected error: {str(e)}"}

def format_sql_query(sql_query: str) -> str:
    if not sql_query:
        return sql_query
    
    sql_query = ' '.join(sql_query.split())

    keywords = [
        'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL JOIN',
        'ON', 'GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT', 'UNION', 'INSERT', 'UPDATE', 'DELETE',
        'AND', 'OR'
    ]
    
    formatted_query = sql_query
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        formatted_query = re.sub(pattern, '\n' + keyword, formatted_query, flags=re.IGNORECASE)
    
    lines = formatted_query.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if line:
            if any(line.upper().startswith(kw) for kw in ['AND', 'OR', 'ON']):
                formatted_lines.append('    ' + line)
            else:
                formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def main():
    st.markdown('<h1 class="main-header">🤖 SQL Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #74b9ff; margin-bottom: 2rem;">Ask questions about your database in natural language</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("## 🗄️ Database Management")
        
        with st.expander("📊 Current Database", expanded=True):
            if st.button("🔄 Refresh Info", key="refresh_db"):
                with st.spinner("Getting database info..."):
                    result = make_api_request("/database/current")
                    if result["success"]:
                        db_info = result["data"]
                        st.success("✅ Connected")
                        st.write(f"**Host:** {db_info.get('host', 'N/A')}")
                        st.write(f"**Port:** {db_info.get('port', 'N/A')}")
                        st.write(f"**User:** {db_info.get('user', 'N/A')}")
                        st.write(f"**Database:** {db_info.get('database', 'N/A')}")
                    else:
                        st.error(result["error"])
        
        with st.expander("🔄 Switch Database"):
            st.markdown("Connect to a different database:")
            
            new_db_name = st.text_input("Database Name", placeholder="my_database")
            new_db_user = st.text_input("Username", placeholder="postgres")
            new_db_pass = st.text_input("Password", type="password", placeholder="password")
            new_db_host = st.text_input("Host", value="localhost", placeholder="localhost")
            new_db_port = st.number_input("Port", value=5432, min_value=1, max_value=65535)
            
            if st.button("🔌 Connect", key="switch_db"):
                if new_db_name:
                    with st.spinner("Connecting to database..."):
                        switch_data = {
                            "db_name": new_db_name,
                            "db_user": new_db_user if new_db_user else None,
                            "db_pass": new_db_pass if new_db_pass else None,
                            "db_host": new_db_host if new_db_host else None,
                            "db_port": new_db_port if new_db_port else None
                        }
                        result = make_api_request("/database/switch", "POST", switch_data)
                        if result["success"]:
                            st.success("✅ Successfully connected!")
                            st.rerun()
                        else:
                            st.error(result["error"])
                else:
                    st.error("Please enter a database name")

    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### 💬 Ask Your Question")
        
        user_question = st.text_area(
            "Your Question:",
            value=st.session_state.get('user_question', ''),
            height=100,
            placeholder="Type your question about the database here...",
            key="question_input"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            query_button = st.button("🚀 Ask Question", type="primary", key="ask_question")
        with col_btn2:
            clear_button = st.button("🗑️ Clear", key="clear_question")
        
        if clear_button:
            st.session_state.user_question = ""
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if query_button and user_question.strip():
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("### 🔍 Query Results")
            
            with st.spinner("🤖 AI is analyzing your question and querying the database..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                result = make_api_request("/query/ask", "POST", {"question": user_question})
            
            progress_bar.empty()
            
            if result["success"]:
                data = result["data"]
                sql_query = data.get("sql_query", "No query generated")
                answer = data.get("answer", "No answer generated")
                
                tab1, tab2 = st.tabs(["📝 Answer", "🔧 SQL Query"])
                
                with tab1:
                    st.markdown('<div class="success-box">', unsafe_allow_html=True)
                    st.markdown("#### 🎯 Answer:")
                    st.markdown(f"**{answer}**")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with tab2:
                    st.markdown("#### 🔧 Generated SQL Query:")
                    formatted_sql = format_sql_query(sql_query)
                    st.code(formatted_sql, language="sql")
                    
                    if st.button("📋 Copy SQL", key="copy_sql"):
                        st.success("SQL query copied to clipboard! (Feature simulated)")
                
            else:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.markdown("#### ❌ Error:")
                st.markdown(result["error"])
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Quick Stats")
        
        api_status = make_api_request("/")
        if api_status["success"]:
            st.metric("🟢 API Status", "Online", "✅")
        else:
            st.metric("🔴 API Status", "Offline", "❌")
        
        st.markdown("---")
        
        st.markdown("### ✨ Features")
        features = [
            "🤖 Natural Language to SQL",
            "🔄 Multi-Database Support",
            "📊 Auto Schema Discovery",
            "🎯 Intelligent Query Generation",
            "⚡ Real-time Results",
            "🛡️ Error Handling"
        ]
        
        for feature in features:
            st.markdown(f"• {feature}")
        
        st.markdown("---")
        
        st.markdown("### 📋 Database Schema")
        if st.button("🔍 Get Schema", key="get_schema"):
            with st.spinner("Fetching database schema..."):
                result = make_api_request("/database/schema")
                if result["success"]:
                    schema_text = result["data"].get("schema_data", "No schema found")
                    st.text_area("Database Schema", schema_text, height=300, key="schema_display")
                else:
                    st.error(result["error"])
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #74b9ff; margin-top: 2rem;">🤖 Powered by Agent + Groq + PostgreSQL | Built with ❤️ by Waqar</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()