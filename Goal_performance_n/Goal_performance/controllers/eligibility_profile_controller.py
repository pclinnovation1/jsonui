
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import config

eligibility_profile_bp = Blueprint('eligibility_profile_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
profile_collection = db[config.ELIGIBILITY_PROFILES_COLLECTION_NAME]

# Helper function to convert keys to lowercase and replace spaces with underscores
def lowercase_keys(data):
    if isinstance(data, dict):
        return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [lowercase_keys(item) for item in data]
    else:
        return data

@eligibility_profile_bp.route('/', methods=['POST'])
def create_profile():
    data = request.json
    data = lowercase_keys(data)  # Convert keys to lowercase and replace spaces with underscores

    profiles = []
    if isinstance(data, list):
        profiles = [profile for profile in data]
        inserted_ids = profile_collection.insert_many(profiles).inserted_ids
        new_profiles = [profile_collection.find_one({'_id': _id}) for _id in inserted_ids]
    else:
        profile_id = profile_collection.insert_one(data).inserted_id
        new_profiles = [profile_collection.find_one({'_id': profile_id})]

    for profile in new_profiles:
        profile['_id'] = str(profile['_id'])

    return jsonify(new_profiles), 201

@eligibility_profile_bp.route('/', methods=['GET'])
def get_profiles():
    profiles = list(profile_collection.find())
    for profile in profiles:
        profile['_id'] = str(profile['_id'])
    return jsonify(profiles), 200

@eligibility_profile_bp.route('/<profile_id>', methods=['GET'])
def get_profile(profile_id):
    profile = profile_collection.find_one({'_id': ObjectId(profile_id)})
    if profile:
        profile['_id'] = str(profile['_id'])
        return jsonify(profile), 200
    else:
        return jsonify({'error': 'Profile not found'}), 404

@eligibility_profile_bp.route('/<profile_id>', methods=['PUT'])
def update_profile(profile_id):
    data = request.json
    data = lowercase_keys(data)  # Convert keys to lowercase and replace spaces with underscores
    result = profile_collection.update_one({'_id': ObjectId(profile_id)}, {'$set': data})
    if result.matched_count:
        updated_profile = profile_collection.find_one({'_id': ObjectId(profile_id)})
        updated_profile['_id'] = str(updated_profile['_id'])
        return jsonify(updated_profile), 200
    else:
        return jsonify({'error': 'Profile not found'}), 404

@eligibility_profile_bp.route('/<profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    result = profile_collection.delete_one({'_id': ObjectId(profile_id)})
    if result.deleted_count:
        return jsonify({'message': 'Profile deleted successfully'}), 200
    else:
        return jsonify({'error': 'Profile not found'}), 404
