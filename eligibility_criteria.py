from pymongo import MongoClient

# MongoDB client setup
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')  # Adjust the connection string as necessary
db = client['PCL_Interns']  # Database name
collection = db['S_EmployeeDetails_UK']  # Collection name

# Function to fetch the schema from the collection
def fetch_schema(collection, sample_size=100):
    schema = {}
    cursor = collection.find().limit(sample_size)
    for doc in cursor:
        process_document(doc, schema)
    return schema

def process_document(doc, schema, path=''):
    if isinstance(doc, dict):
        for key, value in doc.items():
            new_path = f"{path}.{key}" if path else key
            schema[new_path] = True
            if isinstance(value, dict):
                process_document(value, schema, new_path)
            elif isinstance(value, list) and value:
                process_document(value[0], schema, new_path + '[]')

def filter_criteria(criteria, schema):
    filtered = {}
    for category, fields in criteria.items():
        for field, value in fields.items():
            if value.strip():  # Only add non-blank criteria to the query
                full_path = f"{field}"
                if full_path in schema:
                    if category not in filtered:
                        filtered[category] = {}
                    filtered[category][field] = value
    return filtered

def create_mongo_query(filtered_criteria):
    query = {}
    for category, fields in filtered_criteria.items():
        for field, value in fields.items():
            if value.strip():  # Only add non-blank criteria to the query
                query[f"{field}"] = value
    query["Effective_End_Date"] = None  # Only pick records where Effective_End_Date is null
    return query

def check_eligibility(input_data):
    schema = fetch_schema(collection)
    filtered_criteria = filter_criteria(input_data, schema)
    query = create_mongo_query(filtered_criteria)
    print(query)
    matching_persons = []

    # Fetch records from the MongoDB collection based on the query
    all_records = collection.find(query)

    for record in all_records:
        if "Person_Number" in record:
            matching_persons.append(record["Person_Number"])

    return matching_persons
