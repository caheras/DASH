import pandas as pd
from pymongo import MongoClient

# MongoDB connection and database setup
client = MongoClient('localhost', 27017)
db = client['COVID']

# CSV file path
csv_file_path = './owid-covid-data.csv'

# Function to create the time series collection
def create_time_series_collection(db, collection_name):
    if collection_name in db.list_collection_names():
        db[collection_name].drop()  # Optional: Drop existing collection
    db.create_collection(
        collection_name,
        timeseries={'timeField': 'date'}
    )

# Function to insert data from CSV to the time series collection
def insert_data_from_csv(filepath, db, collection_name):
    # Read the CSV file, ensuring the 'date' column is parsed as datetime
    data = pd.read_csv(filepath, parse_dates=['date'])
    
    # Convert 'date' to the appropriate format and the rest of the columns to Double
    data['date'] = pd.to_datetime(data['date'], errors='coerce')
    for col in data.columns:
        if col not in ['iso_code', 'continent', 'location', 'date']:
            data[col] = pd.to_numeric(data[col], errors='coerce', downcast='float')

    # Convert dataframe to dictionary and insert into MongoDB
    records = data.to_dict('records')
    db[collection_name].insert_many(records)

# Run the function to create a time series collection
create_time_series_collection(db, 'covid-data')

# Run the function to insert data
insert_data_from_csv(csv_file_path, db, 'covid-data')

print("Data inserted into MongoDB time series collection")
