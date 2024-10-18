from langchain_chroma import Chroma 
from langchain_openai import OpenAIEmbeddings 
from langchain_community.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import openai
import os
import re
import logging

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
database = os.getenv('DB_db')

engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')

embedding = OpenAIEmbeddings()
vector_store = Chroma(persist_directory='data\\chroma', embedding_function=embedding)

# Function to get schema information from Chroma
def get_schema_info_from_chroma(query):
    retrieved_docs = vector_store.similarity_search(query, k=4)
    if retrieved_docs:
        schema_info = "\n".join([f"Table: {doc.metadata['table_name']}\n{doc.page_content}" for doc in retrieved_docs])
        print(f"Retrieved schema info from Chroma: {schema_info}") # This can be deleted later, just shows the schema info
        return schema_info
    else:
        return ""

# Function to convert natural language to SQL using schema info from Chroma and OpenAI GPT
def text_to_sql_with_chroma(natural_language_query):
    schema_info = get_schema_info_from_chroma("Database schema information")
    
    try:
        response = openai.ChatCompletion.create(  
            model="gpt-4",  
            messages=[
                {"role": "system", "content": f"""You are an expert SQL query generator. Your task is to convert natural language queries into accurate SQL queries based on the following database schema:

{schema_info}

Follow these rules:
1. Always use proper SQL syntax and formatting.
2. Use appropriate table and column names as specified in the schema.
3. Include necessary JOINs if the query involves multiple tables.
4. Use appropriate SQL functions and operators.
5. If the query is ambiguous, ask for clarification.
6. Provide a brief explanation of the generated SQL query.
7. Ensure the SQL query is executable and optimized for performance.
8. Handle potential NULL values appropriately.
9. Use appropriate data types for comparisons and operations.
10. Implement proper error handling and provide informative error messages.
11. Limit the number of rows to 10 unless specified otherwise.

Provide your response in the following format:
SQL Query:
<SQL query>

Explanation:
<Explanation of the SQL query>

The SQL query should be a valid SQL statement without any markdown or additional text."""},
                {"role": "user", "content": natural_language_query}
            ],
            max_tokens=300
        )
        
        full_response = response['choices'][0]['message']['content'].strip()
        
        # Extract SQL query and explanation
        sql_match = re.search(r'SQL Query:\n(.*?)(?:\n\nExplanation:|$)', full_response, re.DOTALL)
        explanation_match = re.search(r'Explanation:\n(.*)', full_response, re.DOTALL)
        
        sql_query = sql_match.group(1).strip() if sql_match else ""
        explanation = explanation_match.group(1).strip() if explanation_match else ""
        
        # Remove any remaining markdown
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        
        return sql_query, explanation
    except Exception as e:
        logging.error(f"Error generating SQL: {e}")
        return None, None

# Function that removes any markdown formatting and capitalizes SQL keywords
def post_process_sql_query(sql_query):
    sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
    
    keywords = ['SELECT', 'FROM', 'WHERE', 'JOIN', 'ON', 'GROUP BY', 'ORDER BY', 'LIMIT']
    for keyword in keywords:
        sql_query = sql_query.replace(keyword.lower(), keyword)
    
    return sql_query

# Function to execute the generated SQL query using SQLAlchemy
def execute_sql_query(sql_query):
    if not sql_query:
        print("No SQL query to execute.")
        return
    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            for row in result:
                print(row)
    except Exception as e:
        print(f"Error executing SQL: {e}")

# Function to validate a SQL query
def validate_sql_query(sql_query):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            return True, None
    except Exception as e:
        return False, str(e)

# Example usage
natural_language_query = "What is the average closing price of stocks in the NYSE"
sql_query, explanation = text_to_sql_with_chroma(natural_language_query)

print("SQL Query:")
print(sql_query)
print("\nExplanation:")
print(explanation)

sql_query = post_process_sql_query(sql_query)
execute_sql_query(sql_query)
