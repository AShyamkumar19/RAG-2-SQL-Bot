from langchain_chroma import Chroma  # Updated import for Chroma
from langchain_openai import OpenAIEmbeddings  # Updated import for OpenAIEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine, text
import openai
import os

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
database = os.getenv("DB_db")

# Set up the SQLAlchemy engine for MySQL
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')

# Initialize the Chroma vector store
embedding = OpenAIEmbeddings()
vector_store = Chroma(persist_directory='data\\chroma', embedding_function=embedding)

# Function to get schema information from Chroma
def get_schema_info_from_chroma(query):
    retrieved_docs = vector_store.similarity_search(query, k=1)
    if retrieved_docs:
        schema_info = retrieved_docs[0].page_content
        print(f"Retrieved schema info from Chroma: {schema_info}")
        return schema_info
    else:
        return ""

# Function to convert natural language to SQL using schema info from Chroma and OpenAI GPT
def text_to_sql_with_chroma(natural_language_query):
    schema_info = get_schema_info_from_chroma("Database schema information")

    try:
        response = openai.ChatCompletion.create(  
            model="gpt-4",  # Chat model
            messages=[
                {"role": "system", "content": f"You are a helpful assistant with access to the following database schema: {schema_info}. Convert the following natural language query into a SQL query."},
                {"role": "user", "content": natural_language_query}
            ],
            max_tokens=150
        )
        sql_query = response['choices'][0]['message']['content'].strip()
        print(f"Generated SQL query: {sql_query}")
        return sql_query
    except Exception as e:
        print(f"Error generating SQL: {e}")
        return None

# Function to execute the generated SQL query using SQLAlchemy
def execute_sql_query(sql_query):
    if not sql_query:
        print("No SQL query to execute.")
        return
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute(sql_query)
            for row in cursor.fetchall():
                print(row)
            cursor.close()
            connection.close()
    except Exception as e:
        print(f"Error executing SQL: {e}")

# Example usage
natural_language_query = "Show the top 5 stocks with the highest volume."
sql_query = text_to_sql_with_chroma(natural_language_query)
print(sql_query)
execute_sql_query(sql_query)
