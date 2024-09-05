import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MySQL connection parameters
user = 'root'
password = os.getenv("DB_PASSWORD")
host = 'localhost'
database = 'stock_info'

# Create SQLAlchemy engine
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')

# Map folder names to stock_exchange_id
exchange_ids = {
    'forbes2000': 1,
    'nyse': 2,
    'nasdaq': 3,
    'sp500': 4
}

# Base directory where your data is stored
base_directory = './data'

for exchange_name, exchange_id in exchange_ids.items():
    csv_directory = os.path.join(base_directory, exchange_name, 'csv')

    if os.path.exists(csv_directory):
        for csv_file in os.listdir(csv_directory):
            if csv_file.endswith('.csv'):
                file_path = os.path.join(csv_directory, csv_file)
                stock_name = os.path.splitext(csv_file)[0]

                try:
                    df = pd.read_csv(file_path, on_bad_lines='skip')
                    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
                    df.columns = ['date', 'low', 'open', 'volume', 'high', 'close', 'adjusted_close']
                    df['name'] = stock_name
                    df['stock_exchange_id'] = exchange_id
                    df = df.dropna(subset=['date'])
                    df.to_sql(name='stock_data', con=engine, if_exists='append', index=False)

                    print(f"Data from {csv_file} in {exchange_name} has been successfully inserted into the stock_data table.")
                except Exception as e:
                    print(f"Failed to process {csv_file} in {exchange_name}. Error: {e}")
    else:
        print(f"The directory {csv_directory} does not exist.")

print("All data has been successfully migrated.")
