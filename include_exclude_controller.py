from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import config

include_exclude_bp = Blueprint('include_exclude_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
include_exclude_collection = db[config.INCLUDE_EXCLUDE_COLLECTION_NAME]

@include_exclude_bp.route('/', methods=['POST'])
def create_include_exclude():
    data = request.json

    # Validate and insert the include/exclude data into MongoDB
    include_exclude_id = include_exclude_collection.insert_one(data).inserted_id
    new_include_exclude = include_exclude_collection.find_one({'_id': include_exclude_id})
    new_include_exclude['_id'] = str(new_include_exclude['_id'])

    # Return the newly created include/exclude document
    return jsonify(new_include_exclude), 201

@include_exclude_bp.route('/', methods=['GET'])
def get_include_excludes():
    # Retrieve all include/exclude documents from the database
    include_excludes = list(include_exclude_collection.find())
    for include_exclude in include_excludes:
        include_exclude['_id'] = str(include_exclude['_id'])
    return jsonify(include_excludes), 200

@include_exclude_bp.route('/<include_exclude_id>', methods=['GET'])
def get_include_exclude(include_exclude_id):
    # Retrieve a specific include/exclude document by ID
    include_exclude = include_exclude_collection.find_one({'_id': ObjectId(include_exclude_id)})
    if include_exclude:
        include_exclude['_id'] = str(include_exclude['_id'])
        return jsonify(include_exclude), 200
    else:
        return jsonify({'error': 'Include/Exclude document not found'}), 404

@include_exclude_bp.route('/<include_exclude_id>', methods=['PUT'])
def update_include_exclude(include_exclude_id):
    data = request.json
    result = include_exclude_collection.update_one({'_id': ObjectId(include_exclude_id)}, {'$set': data})
    if result.matched_count:
        updated_include_exclude = include_exclude_collection.find_one({'_id': ObjectId(include_exclude_id)})
        updated_include_exclude['_id'] = str(updated_include_exclude['_id'])
        return jsonify(updated_include_exclude), 200
    else:
        return jsonify({'error': 'Include/Exclude document not found'}), 404

@include_exclude_bp.route('/<include_exclude_id>', methods=['DELETE'])
def delete_include_exclude(include_exclude_id):
    result = include_exclude_collection.delete_one({'_id': ObjectId(include_exclude_id)})
    if result.deleted_count:
        return jsonify({'message': 'Include/Exclude document deleted successfully'}), 200
    else:
        return jsonify({'error': 'Include/Exclude document not found'}), 404
