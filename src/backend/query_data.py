import openai
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
import os
import getpass
'''
This is just dummy code nothing for now
'''

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

CHROMA_PATH = "src/backend/chroma"

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
    if "stock_data" in chroma_result:
        return "SELECT * FROM stock_data LIMIT 10;"  
    else:
        return None

def execute_sql_query(sql_query: str):
    try:
        df = pd.read_sql(sql_query, engine)  
        return df
    except Exception as e:
        print("Error executing SQL query:", e)
        return None

if __name__ == "__main__":
    main()

# from langchain_community.utilities import SQLDatabase
# from sqlalchemy import create_engine, inspect
# from pyprojroot import here
# from langchain.chains import RetrievalQA
# from langchain_community.vectorstores import Chroma
# from langchain_community.embeddings import OpenAIEmbeddings
# from langchain.chains import SQLDatabaseChain
# from langchain.sql_database import SQLDatabase
# from langchain.llms import OpenAI
# import mysql.connector
# from mysql.connector import Error
# from dotenv import load_dotenv
# import openai
# import warnings
# import os

# load_dotenv()
# openai.api_key = os.getenv("OPENAI_API_KEY")

# # Setting up docker MySQL connection parameters
# user = os.getenv("DB_USER")
# password = os.getenv("DB_PASSWORD")
# host = os.getenv("DB_HOST")
# database = os.getenv("DB_db")

# engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')

# try:
#     connection = mysql.connector.connect(
#             host=host,
#             user=user,
#             password=password,
#             database=database
#     )

#     if connection.is_connected():
#         # For testing purposes
#         db_Info = connection.get_server_info()
#         print("Connected to MySQL Server version ", db_Info)
#         cursor = connection.cursor()
#         cursor.execute("SHOW TABLES;")
#         tables = cursor.fetchall()
#         print("Tables in the database:")
#         for table in tables:
#             print(table)
#         cursor.execute("SELECT * FROM stock_exchange;")
#         for row in cursor.fetchall():
#             print(row)

#         llm = OpenAI(temperature=0)
#         db = SQLDatabase(engine)
#         db_chain = SQLDatabaseChain(llm=llm, db=db, chain_type="stuff")
#         #db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
#         query = "What are the top 5 stocks in the stocks table with the highest volume?"
#         response = db_chain.run(query)
#         print(response)
#         embedding = OpenAIEmbeddings()
#         vector_store = Chroma(persist_directory='data\\chroma', embedding_function=embedding)
#         # qa = RetrievalQA(vector_store=vector_store, query_column='question', response_column='answer')
#         qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vector_store.as_retriever())
#         response = qa_chain.run("Query the schema to identify which table stores the highest stock prices.")
#         print(response)

#         cursor.close()

# except Error as e:
#     print("Error while connecting to MySQL", e)

# finally:
#     if connection.is_connected():
#         connection.close()
#         print("MySQL connection is closed")
