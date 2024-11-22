

from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import config

review_period_bp = Blueprint('review_period_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
review_period_collection = db[config.REVIEW_PERIOD_COLLECTION_NAME]

# Helper function to convert keys to lowercase and replace spaces with underscores
def lowercase_keys(data):
    if isinstance(data, dict):
        return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [lowercase_keys(item) for item in data]
    else:
        return data

# Helper function to parse date fields
def parse_dates(data):
    for key, value in data.items():
        if isinstance(value, str):
            try:
                data[key] = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                continue
    return data

# Route to create a new review period
@review_period_bp.route('/create', methods=['POST'])
def create_review_period():
    data = request.json
    data = lowercase_keys(data)  # Convert keys to lowercase and replace spaces with underscores
    data = parse_dates(data)  # Parse date fields

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = data.get("updated_by", "Unknown")  # Capture updated_by from the request data

    data["updated_date"] = current_time  # Set updated_date
    data["updated_by"] = updated_by  # Set updated_by

    if isinstance(data, list):
        for item in data:
            item["updated_date"] = current_time
            item["updated_by"] = updated_by
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

# Route to get all review periods
@review_period_bp.route('/view', methods=['GET'])
def get_review_periods():
    review_periods = list(review_period_collection.find())
    for review_period in review_periods:
        review_period['_id'] = str(review_period['_id'])
    return jsonify(review_periods), 200

# Route to get a specific review period by name
@review_period_bp.route('/view/<review_period_name>', methods=['GET'])
def get_review_period(review_period_name):
    review_period = review_period_collection.find_one({'name': review_period_name})
    if review_period:
        review_period['_id'] = str(review_period['_id'])
        return jsonify(review_period), 200
    else:
        return jsonify({'error': 'Review period not found'}), 404

# Route to update a specific review period by name
@review_period_bp.route('/update/<review_period_name>', methods=['POST'])
def update_review_period(review_period_name):
    data = request.json
    data = lowercase_keys(data)  # Convert keys to lowercase and replace spaces with underscores
    data = parse_dates(data)  # Parse date fields

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = data.get("updated_by", "Unknown")  # Capture updated_by from the request data

    data["updated_date"] = current_time  # Update the updated_date field with the current date and time
    data["updated_by"] = updated_by  # Update the updated_by field

    result = review_period_collection.update_one({'name': review_period_name}, {'$set': data})
    if result.matched_count:
        updated_review_period = review_period_collection.find_one({'name': review_period_name})
        updated_review_period['_id'] = str(updated_review_period['_id'])
        return jsonify(updated_review_period), 200
    else:
        return jsonify({'error': 'Review period not found'}), 404

# Route to delete a specific review period by name
@review_period_bp.route('/delete/<review_period_name>', methods=['POST'])
def delete_review_period(review_period_name):
    result = review_period_collection.delete_one({'name': review_period_name})
    if result.deleted_count:
        return jsonify({'message': 'Review period deleted successfully'}), 200
    else:
        return jsonify({'error': 'Review period not found'}), 404
