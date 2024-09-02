import pandas as pd
from sqlalchemy import create_engine, inspect
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import openai
from dotenv import load_dotenv
import os
import shutil
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

CHROMA_PATH = "chroma"
DATA_PATH = "./data"

# Docker MySQL connection parameters
user = 'root'
password = os.getenv("DB_PASSWORD")
host = 'localhost'  # Or use the Docker container's IP address or name if running within Docker
database = 'stock_info'

# Create SQLAlchemy engine
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')

def main():
    generate_data_store()

def generate_data_store():
    sql_data = load_sql_data_as_json()  # Load data from SQL and convert to JSON
    chunks = split_text(sql_data)
    save_to_chroma(chunks)

def load_sql_data_as_json():
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    sql_data = []

    for table in tables:
        # Get table schema
        columns = inspector.get_columns(table)
        schema = {col['name']: str(col['type']) for col in columns}

        # Get data dictionary (e.g., column descriptions or other metadata)
        # In a real scenario, this could come from an external source or be hardcoded
        data_dictionary = {col['name']: f"Description of {col['name']}" for col in columns} # Example, needs changes

        # Contextual information (could be custom metadata)
        contextual_info = {
            "table_name": table,
            "description": f"This table contains information about {table}.",
            "row_count": engine.execute(f"SELECT COUNT(*) FROM stock_data;").scalar(),
        }

        # Combine into a single JSON object
        json_content = json.dumps({
            "schema": schema,
            "data_dictionary": data_dictionary,
            "context": contextual_info
        }, indent=4)

        # Create a Document object
        metadata = {"table_name": table}
        sql_data.append(Document(page_content=json_content, metadata=metadata))

    return sql_data

def split_text(sql_data: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(sql_data)
    print(f"Split {len(sql_data)} documents into {len(chunks)} chunks.")

    document = chunks[10] if len(chunks) > 10 else chunks[0]
    print(document.page_content)
    print(document.metadata)

    return chunks

def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(), persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

if __name__ == "__main__":
    main()
