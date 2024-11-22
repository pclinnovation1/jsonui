from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime

# Initialize Blueprint for eligibility profile 
eligibility_profile_bp = Blueprint('eligibility_profile_bp', __name__)

# MongoDB connection setup
MONGODB_URI = "mongodb://oras_user:oras_pass@172.191.245.199:27017/oras"
DATABASE_NAME = "oras"

# Set up MongoDB client and database 
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

# MongoDB collections
profile_collection = db["PGM_eligibility_profiles"]

# Helper function to convert keys to lowercase and replace spaces with underscores
# This function is recursive, works for both dictionaries and lists
def lowercase_keys(data):
    if isinstance(data, dict):
        # For dictionary, convert keys and apply recursively
        return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        # For list, apply recursively on all elements
        return [lowercase_keys(item) for item in data]
    else:
        return data # Base case: return the data if neither dict nor list

# Route to create a new profile
@eligibility_profile_bp.route('/create', methods=['POST'])
def create_profile():
    # Convert keys to lowercase and replace spaces with underscores
    data = lowercase_keys(request.json)  

    current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = data.get("updated_by", "Admin")  # Capture updated_by from the request data
    data["updated_by"] = updated_by  # Set updated_by
    data["updated_date"] = current_time  # Set updated_date

    if isinstance(data, list):
        for profile in data:
            profile["updated_date"] = current_time  # Set updated_date
            profile["updated_by"] = updated_by  # Set updated_by
        inserted_ids = profile_collection.insert_many(data).inserted_ids
        new_profiles = [profile_collection.find_one({'_id': _id}) for _id in inserted_ids]
    else:
        profile_id = profile_collection.insert_one(data).inserted_id
        new_profiles = [profile_collection.find_one({'_id': profile_id})]

    for profile in new_profiles:
        profile['_id'] = str(profile['_id'])

    return jsonify(new_profiles), 201
