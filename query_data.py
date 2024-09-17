import openai
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

CHROMA_PATH = "chroma"

# MySQL connection parameters (Docker)
user = 'root'
password = os.getenv("DB_PASSWORD")
host = 'localhost'  # Or Docker container IP
database = 'stock_info'

# Create SQLAlchemy engine to connect to MySQL
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')

def main():
    # Example query from the user
    user_query = "What's the schema of stock_data?"

    # 1. Query Chroma for schema information
    relevant_info = query_chroma(user_query)

    # 2. Based on Chroma result, generate SQL query (if applicable)
    if relevant_info:
        sql_query = generate_sql_query(relevant_info)

        # 3. Execute the generated SQL query on the MySQL database
        if sql_query:
            results = execute_sql_query(sql_query)
            print("Query Results:", results)
        else:
            print("No valid SQL query generated.")
    else:
        print("No relevant information found in Chroma.")

def query_chroma(user_query: str):
    # Load Chroma vector store
    chroma_db = Chroma(persist_directory=CHROMA_PATH, embedding_function=OpenAIEmbeddings())

    # Query Chroma for relevant schema information
    results = chroma_db.similarity_search(user_query, k=1)  # You can adjust 'k' to return more results
    if results:
        print("Chroma Results:", results[0].page_content)  # Print the closest match
        return results[0].page_content  # Return the schema-related information
    else:
        print("No results found in Chroma.")
        return None

def generate_sql_query(chroma_result):
    """
    Here, you would extract the table name and column names from the Chroma result (schema info).
    Based on this, you can generate the SQL query.
    """
    # Example: If the schema information indicates the "stock_data" table
    if "stock_data" in chroma_result:
        return "SELECT * FROM stock_data LIMIT 10;"  # Example SQL query
    else:
        return None

def execute_sql_query(sql_query: str):
    # Execute SQL query on MySQL database
    try:
        df = pd.read_sql(sql_query, engine)  # Use pandas to run the query and fetch results
        return df
    except Exception as e:
        print("Error executing SQL query:", e)
        return None

if __name__ == "__main__":
    main()
