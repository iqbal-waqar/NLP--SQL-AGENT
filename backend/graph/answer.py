import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def generate_answer(user_question, sql_query, db_result):
    prompt = ChatPromptTemplate.from_template("""
        User asked: {user_question}
        SQL Query: {sql_query}
        Database result: {db_result}

        Provide ONLY a direct, natural language answer. Do not include explanations, reasoning, or extra text.

        Examples:
        - If result = [(20,)] → "There are 20 students."
        - If result = [('John',), ('Jane',)] → "The students are John and Jane."
        - If result = [(100, 'CS'), (50, 'Math')] → "There are 100 students in CS and 50 students in Math."
        
        Answer:
    """)

    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-8b-8192"
    )

    chain = prompt | llm | StrOutputParser()
    return chain.invoke({
        "user_question": user_question,
        "sql_query": sql_query,
        "db_result": db_result
    })
