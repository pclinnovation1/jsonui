

from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import config

eligibility_profile_bp = Blueprint('eligibility_profile_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
eligibility_profile_collection = db[config.ELIGIBILITY_PROFILES_COLLECTION_NAME]

@eligibility_profile_bp.route('/', methods=['POST'])
def create_eligibility_profile():
    data = request.json

    if isinstance(data, list):
        inserted_ids = eligibility_profile_collection.insert_many(data).inserted_ids
        new_profiles = [eligibility_profile_collection.find_one({'_id': _id}) for _id in inserted_ids]
        for profile in new_profiles:
            profile['_id'] = str(profile['_id'])
        return jsonify(new_profiles), 201
    else:
        eligibility_profile_id = eligibility_profile_collection.insert_one(data).inserted_id
        new_eligibility_profile = eligibility_profile_collection.find_one({'_id': eligibility_profile_id})
        new_eligibility_profile['_id'] = str(new_eligibility_profile['_id'])
        return jsonify(new_eligibility_profile), 201

@eligibility_profile_bp.route('/', methods=['GET'])
def get_eligibility_profiles():
    eligibility_profiles = list(eligibility_profile_collection.find())
    for profile in eligibility_profiles:
        profile['_id'] = str(profile['_id'])
    return jsonify(eligibility_profiles), 200

@eligibility_profile_bp.route('/<eligibility_profile_id>', methods=['GET'])
def get_eligibility_profile(eligibility_profile_id):
    eligibility_profile = eligibility_profile_collection.find_one({'_id': ObjectId(eligibility_profile_id)})
    if eligibility_profile:
        eligibility_profile['_id'] = str(eligibility_profile['_id'])
        return jsonify(eligibility_profile), 200
    else:
        return jsonify({'error': 'Eligibility profile not found'}), 404

@eligibility_profile_bp.route('/<eligibility_profile_id>', methods=['PUT'])
def update_eligibility_profile(eligibility_profile_id):
    data = request.json
    result = eligibility_profile_collection.update_one({'_id': ObjectId(eligibility_profile_id)}, {'$set': data})
    if result.matched_count:
        updated_profile = eligibility_profile_collection.find_one({'_id': ObjectId(eligibility_profile_id)})
        updated_profile['_id'] = str(updated_profile['_id'])
        return jsonify(updated_profile), 200
    else:
        return jsonify({'error': 'Eligibility profile not found'}), 404

@eligibility_profile_bp.route('/<eligibility_profile_id>', methods=['DELETE'])
def delete_eligibility_profile(eligibility_profile_id):
    result = eligibility_profile_collection.delete_one({'_id': ObjectId(eligibility_profile_id)})
    if result.deleted_count:
        return jsonify({'message': 'Eligibility profile deleted successfully'}), 200
    else:
        return jsonify({'error': 'Eligibility profile not found'}), 404




