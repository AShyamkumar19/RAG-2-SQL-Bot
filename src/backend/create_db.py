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

CHROMA_PATH = "src/backend/chroma"
DATA_PATH = "./data"
JSON_FILE = "src/backend/knowledge.json"


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
    schema_data = load_json_file(JSON_FILE)
    chunks = split_text(schema_data)
    save_to_chroma(chunks)

def load_json_file(json_file_path):
    with open(json_file_path, 'r') as file:
        json_content = json.load(file)
    
    # Convert the loaded JSON into Document objects
    schema_data = []
    for table_name, table_info in json_content.items():
        document_content = json.dumps(table_info, indent=4)
        metadata = {"table_name": table_name}
        schema_data.append(Document(page_content=document_content, metadata=metadata))
    
    return schema_data

def split_text(schema_data: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    
    # Split each document into chunks
    chunks = text_splitter.split_documents(schema_data)
    print(f"Split {len(schema_data)} documents into {len(chunks)} chunks.")

    # Print a sample chunk to verify the output
    document = chunks[10] if len(chunks) > 10 else chunks[0]
    print(document.page_content)
    print(document.metadata)

    return chunks

def save_to_chroma(chunks: list[Document]):
    # Clear out the existing database first
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new Chroma vector database from the documents
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(), persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

if __name__ == "__main__":
    main()
