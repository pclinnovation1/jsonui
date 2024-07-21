
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import config

review_period_bp = Blueprint('review_period_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
review_period_collection = db[config.REVIEW_PERIOD_COLLECTION_NAME]

@review_period_bp.route('/', methods=['POST'])
def create_review_period():
    data = request.json

    if isinstance(data, list):
        inserted_ids = review_period_collection.insert_many(data).inserted_ids
        new_review_periods = [review_period_collection.find_one({'_id': _id}) for _id in inserted_ids]
        for review_period in new_review_periods:
            review_period['_id'] = str(review_period['_id'])
        return jsonify(new_review_periods), 201
    else:
        review_period_id = review_period_collection.insert_one(data).inserted_id
        new_review_period = review_period_collection.find_one({'_id': review_period_id})
        new_review_period['_id'] = str(new_review_period['_id'])
        return jsonify(new_review_period), 201

@review_period_bp.route('/', methods=['GET'])
def get_review_periods():
    review_periods = list(review_period_collection.find())
    for review_period in review_periods:
        review_period['_id'] = str(review_period['_id'])
    return jsonify(review_periods), 200

@review_period_bp.route('/<review_period_id>', methods=['GET'])
def get_review_period(review_period_id):
    review_period = review_period_collection.find_one({'_id': ObjectId(review_period_id)})
    if review_period:
        review_period['_id'] = str(review_period['_id'])
        return jsonify(review_period), 200
    else:
        return jsonify({'error': 'Review period not found'}), 404

@review_period_bp.route('/<review_period_id>', methods=['PUT'])
def update_review_period(review_period_id):
    data = request.json
    result = review_period_collection.update_one({'_id': ObjectId(review_period_id)}, {'$set': data})
    if result.matched_count:
        updated_review_period = review_period_collection.find_one({'_id': ObjectId(review_period_id)})
        updated_review_period['_id'] = str(updated_review_period['_id'])
        return jsonify(updated_review_period), 200
    else:
        return jsonify({'error': 'Review period not found'}), 404

@review_period_bp.route('/<review_period_id>', methods=['DELETE'])
def delete_review_period(review_period_id):
    result = review_period_collection.delete_one({'_id': ObjectId(review_period_id)})
    if result.deleted_count:
        return jsonify({'message': 'Review period deleted successfully'}), 200
    else:
        return jsonify({'error': 'Review period not found'}), 404
