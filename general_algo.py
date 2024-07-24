from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
import os
from dotenv import load_dotenv

load_dotenv()

db = None

def connect_database():
    global db 
    try:
        print("Connecting to the database...")
        username = os.getenv('MONGODB_USERNAME')
        password = os.getenv('MONGODB_PASSWORD')
        host = os.getenv('MONGODB_HOST')
        port = os.getenv('MONGODB_PORT')
        dbname = os.getenv('MONGODB_DBNAME') 
               
        if not username or not password:
            raise ValueError("Username or password environment variables not set")
                
        mongoDB_url = f'mongodb://{username}:{password}@{host}:{port}/{dbname}'     
        client = MongoClient(mongoDB_url)       
        db = client[dbname]
        print("Connected to the database: ", db)
        return db
    except (ConnectionFailure, ConfigurationError) as e:
        print(f"Error connecting to MongoDB: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
      
def get_database():
    global db
    if db is None:
        return connect_database()
    return db

def get_collection_schema(collection):
    """Retrieve the schema of the collection, excluding the '_id' field."""
    print("Fetching collection schema...")
    sample_document = collection.find_one()
    if not sample_document:
        print("No documents found in collection.")
        return {}
    
    schema = {
        key: type(value).__name__ if value is not None else 'NoneType' 
        for key, value in sample_document.items() 
        if key != '_id'
    }
    
    print(f"Collection schema: {schema}")
    return schema


def validate_data_schema1(schema, data):
    """Validate the data against the schema."""
    print(f"Validating data against schema: {schema}")
    for item in data:
        for key, value in item.items():
            if value is None:
                continue
            if key not in schema or schema[key] != type(value).__name__:
                print(f"Validation failed for key and value: {key} & {value}")
                return False
    print("All items validated successfully.")
    return True

def validate_data_schema2(schema, data):
    """Validate the data against the schema."""
    print(f"Validating data against schema: {schema}")
    for item in data:
        for key in schema.keys():
            if key not in item:
                print(f"Validation failed: missing key '{key}' in item {item}")
                return False
            value = item[key]
            expected_type = schema[key]
            if value is None:
                continue
                # if expected_type != 'NoneType':
                #     print(f"Validation failed for key '{key}': expected type '{expected_type}', got 'NoneType'")
                #     return False
            else:
                actual_type = type(value).__name__
                if actual_type != expected_type:
                    print(f"Validation failed for key '{key}': expected type '{expected_type}', got '{actual_type}'")
                    return False
    print("All items validated successfully.")
    return True

def data_validation_against_schema(collection, data):
    """Perform data validation against the collection schema."""
    schema = get_collection_schema(collection)
    if schema and not validate_data_schema1(schema, data):
        return False
    if schema and not validate_data_schema2(schema, data):
        return False
    return True