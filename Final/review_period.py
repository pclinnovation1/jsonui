from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from datetime import datetime

# Blueprint setup for review period module
review_period_bp = Blueprint('review_period_bp', __name__)

# MongoDB connection URI and database name setup
MONGODB_URI = "mongodb://oras_user:oras_pass@172.191.245.199:27017/oras"
DATABASE_NAME = "oras"

# Set up MongoDB client and select the database
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

# MongoDB collection for review periods
review_period_collection = db["PGM_review_period"]

# Helper function to convert dictionary keys to lowercase and replace spaces with underscores
# Recursively processes nested dictionaries and lists
def lowercase_keys(data):
    if isinstance(data, dict):
        # Apply conversion to dictionary keys
        return {k.lower().replace(' ', '_'): lowercase_keys(v) for k, v in data.items()}
    elif isinstance(data, list):
        # Apply conversion to each item in the list
        return [lowercase_keys(item) for item in data]
    else:
         # Base case: return the data itself if it's neither a dict nor a list
        return data

# Helper function to parse date fields in a dictionary
# Converts string representations of dates to datetime objects where applicable
def parse_dates(data):
    for key, value in data.items():
        if isinstance(value, str):
            try:
                # Attempt to parse the string as a date in the format 'YYYY-MM-DD
                data[key] = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                # If parsing fails, leave the value unchanged
                continue
    return data

# Route to create a new review period
# This handles POST requests to store review period data in MongoDB
@review_period_bp.route('/create', methods=['POST'])
def create_review_period():
    data = lowercase_keys(request.json)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_by = data.get("updated_by", "Admin")  # Capture updated_by from the request data

    data["updated_at"] = current_time  # Set updated_date
    data["updated_by"] = updated_by  # Set updated_by

    # Insert the data into the MongoDB collection
    result = review_period_collection.insert_one(data)

    # Retrieve the inserted document to return in the response
    inserted_document = review_period_collection.find_one({"_id": result.inserted_id})

    # Convert MongoDB document to JSON serializable format
    inserted_document["_id"] = str(inserted_document["_id"])

    return jsonify(inserted_document), 201  # Return the inserted document as JSON with a 201 status code
