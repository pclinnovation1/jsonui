import pandas as pd
from pymongo import MongoClient

def excel_to_mongodb(excel_file, sheet_name, collection_name):
    # Read data from Excel file, specifying that the header is on the third row (index 2) and data starts from the fourth row
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=1)
    
    # Convert all datetime columns to strings to avoid NaTType errors
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].astype(str)
    
    # Convert DataFrame to JSON
    data = df.to_dict(orient='records')
    
    # Connect to MongoDB
    client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')  # Replace with your MongoDB URI
    db = client['PCL_Interns']  # Replace with your database name
    collection = db[collection_name]
    
    # Insert data into MongoDB collection
    collection.insert_many(data)
    print(f'Data from {excel_file} (sheet: {sheet_name}) has been inserted into the {collection_name} collection.')

# Example usage
excel_to_mongodb('/Users/vishalmeena/Downloads/Personal data_PCL_R.xlsx', 'Sheet1 (3)', 'ORAS_Sheet2')
