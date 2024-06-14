# # app.py
# from flask import Flask, request, jsonify
# from pymongo import MongoClient
# from config import load_criteria

# app = Flask(__name__)

# # MongoDB client setup
# client = MongoClient('mongodb://localhost:27017/')  # Adjust the connection string as necessary
# db = client['PCL_Interns']  # Database name
# collection = db['S_EmployeeDetails_UK']  # Collection name

# eligibility_criteria = load_criteria()

# def check_eligibility(record, criteria):
#     for category, fields in criteria.items():
#         if category in record:
#             for field, value in fields.items():
#                 if value.strip() and field in record[category]:
#                     if record[category][field] != value:
#                         return False
#     return True

# @app.route('/check_eligibility', methods=['POST'])
# def check_eligibility_route():
#     input_data = request.json
#     matching_persons = []
    
#     # Fetch all records from the MongoDB collection
#     all_records = collection.find()
    
#     for record in all_records:
#         if check_eligibility(record, input_data):
#             matching_persons.append(record["Person_Number"])
    
#     if matching_persons:
#         return jsonify({"matching_person_numbers": matching_persons})
#     else:
#         return jsonify({"error": "No records found that satisfy the criteria"}), 404

# @app.route('/fill_criteria', methods=['POST'])
# def fill_criteria():
#     input_data = request.json
#     filled_criteria = load_criteria()  # Load criteria again to avoid modifying the original

#     for category, fields in filled_criteria.items():
#         if category in input_data:
#             for field in fields:
#                 if field in input_data[category]:
#                     filled_criteria[category][field] = input_data[category][field]

#     return jsonify(filled_criteria)

# if __name__ == '__main__':
#     app.run(debug=True)












# # app.py
# from flask import Flask, request, jsonify
# from pymongo import MongoClient
# from config import load_criteria

# app = Flask(__name__)

# # MongoDB client setup
# client = MongoClient('mongodb://localhost:27017/')  # Adjust the connection string as necessary
# # db = client['PCL_Interns']  # Database name
# db = client['PCL_Database'] 
# collection = db['EmployeeDetails_UK']  # Collection name

# eligibility_criteria = load_criteria()

# def check_eligibility(record, criteria):
#     for category, fields in criteria.items():
#         if category in record:
#             for field, value in fields.items():
#                 if value.strip():
#                     if field not in record[category] or str(record[category][field]).strip() != str(value).strip():
#                         print(f"Mismatch found in category '{category}', field '{field}': Record value '{record[category].get(field, 'N/A')}', Criteria value '{value}'")
#                         return False
#     return True

# @app.route('/check_eligibility', methods=['POST'])
# def check_eligibility_route():
#     input_data = request.json
#     matching_persons = []
    
#     # Fetch all records from the MongoDB collection
#     all_records = collection.find()
#     print("In",input_data)
#     print("record",all_records)
    
#     for record in all_records:
#         if check_eligibility(record, input_data):
#             matching_persons.append(record["Person_Number"])
    
#     if matching_persons:
#         return jsonify({"matching_person_numbers": matching_persons})
#     else:
#         return jsonify({"error": "No records found that satisfy the criteria"}), 404

# @app.route('/fill_criteria', methods=['POST'])
# def fill_criteria():
#     input_data = request.json
#     filled_criteria = load_criteria()  # Load criteria again to avoid modifying the original

#     for category, fields in filled_criteria.items():
#         if category in input_data:
#             for field in fields:
#                 if field in input_data[category]:
#                     filled_criteria[category][field] = input_data[category][field]

#     return jsonify(filled_criteria)

# if __name__ == '__main__':
#     app.run(debug=True)










# # app.py
# from flask import Flask, request, jsonify
# from pymongo import MongoClient
# from config import load_criteria

# app = Flask(__name__)

# # MongoDB client setup
# client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')  # Adjust the connection string as necessary
# db = client['PCL_Interns']  # Database name
# collection = db['S_EmployeeDetails_UK']  # Collection name

# eligibility_criteria = load_criteria()

# def check_eligibility(record, criteria):
#     for category, fields in criteria.items():
#         if category in record:
#             for field, value in fields.items():
#                 if value.strip():  # Only check non-blank criteria
#                     if field not in record[category] or str(record[category][field]).strip() != str(value).strip():
#                         return False
#     return True

# @app.route('/check_eligibility', methods=['POST'])
# def check_eligibility_route():
#     input_data = request.json
#     matching_persons = []

#     # Fetch all records from the MongoDB collection
#     all_records = collection.find()

#     for record in all_records:
#         if check_eligibility(record, input_data):
#             matching_persons.append(record["Person_Number"])

#     if matching_persons:
#         return jsonify({"matching_person_numbers": matching_persons})
#     else:
#         return jsonify({"error": "No records found that satisfy the criteria"}), 404

# if __name__ == '__main__':
#     app.run(debug=True)





from flask import Flask, request, jsonify
from pymongo import MongoClient
from config import load_criteria

app = Flask(__name__)

# MongoDB client setup
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')  # Adjust the connection string as necessary
db = client['PCL_Interns']  # Database name
collection = db['S_EmployeeDetails_UK']  # Collection name

eligibility_criteria = load_criteria()

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
    return query

@app.route('/check_eligibility', methods=['POST'])
def check_eligibility_route():
    input_data = request.json
    schema = fetch_schema(collection)
    filtered_criteria = filter_criteria(input_data, schema)
    query = create_mongo_query(filtered_criteria)
    # print(f"Constructed MongoDB Query: {query}")  # Log the constructed query for debugging purposes
    matching_persons = []

    # Fetch records from the MongoDB collection based on the query
    all_records = collection.find(query)
    # print(all_records[0])

    for record in all_records:
        if "Person_Number" in record:
            matching_persons.append(record["Person_Number"])

    if matching_persons:
        return jsonify({"matching_person_numbers": matching_persons})
    else:
        return jsonify({"error": "No records found that satisfy the criteria"}), 404

if __name__ == '__main__':
    app.run(debug=True)
