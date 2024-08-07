from flask import Flask, jsonify, request
# import yaml
from pymongo import MongoClient

app = Flask(__name__)

# Load the YAML configuration
# with open('config.yaml', 'r') as file:
    # config = yaml.safe_load(file)

# MongoDB connection URI
uri = 'mongodb://dev1_user:dev1_pass@172.191.245.199:27017/dev1'
db_name = 'dev1'

# Initialize MongoDB client
client = MongoClient(uri)
db = client[db_name]

# List of allowed collections
allowed_collections = [
    "PGM_development_plan", "PGM_eligibility_profiles", "PGM_employee_performance_review",
    "PGM_feedback", "PGM_feedback_templates", "PGM_goal", "PGM_goal_offering",
    "PGM_goal_plan", "PGM_my_goal_plan_goals", "PGM_my_goals", "PGM_performance_document",
    "PGM_performance_goal_assignment", "PGM_question", "PGM_questionnaire_templates", "PGM_review_period"
]

@app.route('/process_data', methods=['POST'])
def process_data():
    # Retrieve request JSON body
    request_data = request.get_json()
    
    # Extract the collection name from the request
    collection_name = request_data.get('collection')
    
    # Check if the collection is allowed
    if collection_name not in allowed_collections:
        return jsonify({"error": "Collection not found or not allowed"}), 404
    
    # Fetch data for the specified collection
    collection = db[collection_name]
    collection_data = list(collection.find())
    
    # Convert ObjectId to string for JSON serialization
    for document in collection_data:
        document['_id'] = str(document['_id'])
    
    return jsonify(collection_data)

if __name__ == '__main__':
    app.run(debug=True)
