from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime


eligibility_profile_bp = Blueprint('eligibility_profile_bp', __name__)

MONGODB_URI = "mongodb://oras_user:oras_pass@172.191.245.199:27017/oras"
DATABASE_NAME = "oras"

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
# MongoDB client setup
profile_collection = db["PGM_eligibility_profiles"]

# Helper function to convert keys to lowercase and replace spaces with underscores
def lowercase_keys(data):
    if isinstance(data, dict):
        return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [lowercase_keys(item) for item in data]
    else:
        return data

# Route to create a new profile
@eligibility_profile_bp.route('/create', methods=['POST'])
def create_profile():
    data = request.json
    data = lowercase_keys(data)  # Convert keys to lowercase and replace spaces with underscores

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

# Route to get all profiles
@eligibility_profile_bp.route('/view', methods=['POST'])
def get_profiles():
    profiles = list(profile_collection.find())
    for profile in profiles:
        profile['_id'] = str(profile['_id'])
    return jsonify(profiles), 200

# Route to get a specific profile by name
@eligibility_profile_bp.route('/view/<profile_name>', methods=['POST'])
def get_profile(profile_name):
    profile = profile_collection.find_one({'profile_name': profile_name})
    if profile:
        profile['_id'] = str(profile['_id'])
        return jsonify(profile), 200
    else:
        return jsonify({'error': 'Profile not found'}), 404

# Route to update a specific profile by name
@eligibility_profile_bp.route('/update/<profile_name>', methods=['POST'])
def update_profile(profile_name):
    data = request.json
    data = lowercase_keys(data)  # Convert keys to lowercase and replace spaces with underscores
    data['updated_date'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')  # Add the updated_date field with the current date and time
    data['updated_by'] = data.get("updated_by", "Unknown")  # Capture updated_by from the request data

    result = profile_collection.update_one({'profile_name': profile_name}, {'$set': data})
    if result.matched_count:
        updated_profile = profile_collection.find_one({'profile_name': profile_name})
        updated_profile['_id'] = str(updated_profile['_id'])
        return jsonify(updated_profile), 200
    else:
        return jsonify({'error': 'Profile not found'}), 404

# Route to delete a specific profile by name
@eligibility_profile_bp.route('/delete/<profile_name>', methods=['POST'])
def delete_profile(profile_name):
    result = profile_collection.delete_one({'profile_name': profile_name})
    if result.deleted_count:
        return jsonify({'message': 'Profile deleted successfully'}), 200
    else:
        return jsonify({'error': 'Profile not found'}), 404
