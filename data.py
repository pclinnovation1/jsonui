import pandas as pd
from pymongo import MongoClient

# Function to upload CSV data to MongoDB
def upload_csv_to_mongodb(csv_file_path, db_name, collection_name, mongo_uri="mongodb://dev1_user:dev1_pass@172.191.245.199:27017/dev1"):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)
    
    # Convert DataFrame to a list of dictionaries
    data = df.to_dict(orient='records')
    
    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    
    # Select the database and collection
    db = client[db_name]
    collection = db[collection_name]
    
    # Insert the data into the collection
    collection.insert_many(data)
    
    # Close the connection
    client.close()
    
    print(f"Data from {csv_file_path} has been uploaded to {db_name}.{collection_name} collection.")

# Example usage
csv_file_path = "Sample_Data\Sample_Course_Data__New.csv"  # Replace with your CSV file path
db_name = "dev1"        # Replace with your MongoDB database name
collection_name = "LRN_course_assignment"  # Replace with your MongoDB collection name

upload_csv_to_mongodb(csv_file_path, db_name, collection_name)
