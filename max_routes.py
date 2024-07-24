from flask import Blueprint, request, jsonify
from datetime import datetime
import sys
import os

# Add the parent directory of dev1 to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '/Users/vishalmeena/Downloads/Code_wrap_Latest 4 copy/dev1')))


from configuration.max_routes_config import config
from algorithms.general_algo import get_database, data_validation_against_schema
from fuzzywuzzy import fuzz

max_routes_bp = Blueprint('routes_blueprint', __name__)

def location_name_exists(location_name):
    """Check if the location_name exists in the LRN_Location collection."""
    print("gone in this function")
    db = get_database()
    location_collection = db['LRN_location']
    return location_collection.find_one({'name': location_name}) is not None
def attribute_exists(collection, attribute, value):
    """Check if the attribute exists in the specified collection."""
    return collection.find_one({attribute: value}) is not None

def find_similar_documents(collection_name, title_field, title_value):
    try:
        # Fetch all documents from the specified collection
        db = get_database()
        collection = db[collection_name]
        documents = list(collection.find({}, {title_field: 1}))
    except Exception as e:
        print(f"Error fetching documents from collection '{collection_name}': {e}")
        return []

    # Trim the input title value
    title_value = title_value.strip()

    # Use fuzzy matching to find all potential matches
    matches = []
    for document in documents:
        if title_field in document and isinstance(document[title_field], str):
            score = fuzz.token_sort_ratio(title_value.lower(), document[title_field].strip().lower())
            if score >= 40:  # Adjust threshold as needed
                matches.append({"document": document, "score": score})

    # Sort matches by score in descending order
    matches.sort(key=lambda x: x["score"], reverse=True)

    # Filter out matches where there are significant unmatched parts
    filtered_matches = []
    for match in matches:
        unmatched_ratio = 100 - match["score"]
        if unmatched_ratio <= 60:  # Adjust the threshold for unmatched parts as needed
            filtered_matches.append(match)

    return filtered_matches

def add_items(collection, data, extra_info=[]):
    try:
        items = data.get('items', [])
        for item in items:
            for field in extra_info:
                field_name = field['field_name']
                field_value = field['field_value']

                # Handle special fields for datetime
                if field_name.split('.')[-1] in ['created_at', 'creation_date']:
                    field_value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if '.' in field_name:  # Handle nested fields
                    keys = field_name.split('.')
                    temp = item
                    for key in keys[:-1]:
                        if key not in temp:
                            temp[key] = {}
                        temp = temp[key]
                    temp[keys[-1]] = field_value
                else:
                    item[field_name] = field_value

        if collection.name == "LRN_classroom":
            if 'name' in item and attribute_exists(collection, 'name', item['name']):
                return {'error': f"Entry with name '{item['name']}' already exists"}, 400
            for item in items:
                if 'location_name' in item and not location_name_exists(item['location_name']):
                    return {'error': f"Location '{item['location_name']}' does not exist in LRN_Location collection"}, 400

        if not data_validation_against_schema(collection, items):
            return {'error': 'Data schema does not match collection schema'}, 400
        
        result = collection.insert_many(items)
        inserted_ids = [str(item_id) for item_id in result.inserted_ids]
        return {'inserted_ids': inserted_ids}, 201
    except Exception as e:
        return {'error': str(e)}, 500


def search_items(collection, data, extra_info={}):
    try:
        if not data:
            query = {}
        else:
            query = data
        # query = data.get('query', {})
        additional_query_fields = extra_info.get("additional_query_fields", [])
        exclude_fields = extra_info.get("exclude_fields", [])

        # Add additional query fields
        for field in additional_query_fields:
            query[field['field_name']] = field['field_value']

        # Create projection to exclude fields
        projection = {field: 0 for field in exclude_fields}

        items = list(collection.find(query, projection))
        
        for item in items:
            if '_id' in item:
                item['_id'] = str(item['_id'])
        return items, 200
    except Exception as e:
        return {'error': str(e)}, 500
    

# def update_items(collection, data, extra_info={}):
#     try:
#         query = data.get('query', {})
#         update_data = data.get('update', {})
#         if not update_data:
#             return {'error': 'No update data provided'}, 400  
        
#         additional_query_fields = extra_info.get("additional_query_fields", [])
#         field_in_query = extra_info.get("field_in_query", [])
#         field_not_in_update_data = extra_info.get("field_not_in_update_data", [])
#         additional_update_fields = extra_info.get("additional_update_fields", [])
              
#         for field in extra_info:
#             field_name = field['field_name']
#             field_value = field['field_value']

#             if field_name.split('.')[-1] in ['updated_at']:
#                 field_value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#             if '.' in field_name:  # Handle nested fields
#                 keys = field_name.split('.')
#                 temp = update_data
#                 for key in keys[:-1]:
#                     if key not in temp:
#                         temp[key] = {}
#                     temp = temp[key]
#                 temp[keys[-1]] = field_value
#             else:
#                 update_data[field_name] = field_value
#         result = collection.update_many(query, {'$set': update_data})
#         if result.matched_count == 0:
#             return {'message': 'No items matched the query'}, 404
#         updated_items = list(collection.find(query))
#         for item in updated_items:
#             item['_id'] = str(item['_id'])
#         return updated_items, 200
#     except Exception as e:
#         return {'error': str(e)}, 500

def update_items(collection, data, extra_info={}):
    try:
        query = data.get('query', {})
        update_data = data.get('update_data', {})
        
        if not update_data:
            return {'error': 'No update data provided'}, 400  

        # Process extra_info
        additional_query_fields = extra_info.get("additional_query_fields", [])
        field_in_query = extra_info.get("field_in_query", [])
        field_not_in_update_data = extra_info.get("field_not_in_update_data", [])
        additional_update_fields = extra_info.get("additional_update_fields", [])
        field_for_find_similar_documents = extra_info.get("field_for_find_similar_documents", [])

        # Ensure there is at least one common field between query and field_in_query
        if not any(key in field_in_query for key in query.keys()):
            return {'error': 'No common fields between query and allowed fields', 'allowed_fields': field_in_query}, 400

        # Ensure no restricted fields are in the update data
        for field in field_not_in_update_data:
            if field in update_data:
                return {'error': f'Field {field} cannot be modified'}, 400
            
        # Add additional query fields
        for field in additional_query_fields:
            query[field['field_name']] = field['field_value']

        # Add additional update fields to the update data
        for field in additional_update_fields:
            field_name = field['field_name']
            field_value = field['field_value']
            
            if field_name.split('.')[-1] in ['updated_at']:
                field_value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            update_data[field_name] = field_value
        
        
        print("Query:" , query)
        print("Update Data:", update_data)
        # Attempt to find exact matches
        exact_matches = list(collection.find(query))
        if exact_matches:
            # Perform update on exact matches
            result = collection.update_many(query, {'$set': update_data})
            updated_items = list(collection.find(query))
            for item in updated_items:
                item['_id'] = str(item['_id'])
            return updated_items, 200

        # If no exact match, find similar documents
        similar_documents = []
        collection_name = collection.name
        for key in field_for_find_similar_documents:
            if key in query and isinstance(query[key], str):
                similar_docs = find_similar_documents(collection_name, key, query[key])
                if similar_docs:
                    similar_documents.extend(similar_docs)
        
        if similar_documents:
            return {'message': 'No exact match found. Here are similar documents:', 'similar_documents': similar_documents}, 404
        else:
            return {'error': 'No exact or similar documents found'}, 404
    except Exception as e:
        return {'error': str(e)}, 500
    

def delete_items(collection, data):
    try:
        query = data.get('query', {})
        result = collection.delete_many(query)
        if result.deleted_count == 0:
            return {'message': 'No items matched the query'}, 404
        return {'message': 'Items deleted successfully'}, 200
    except Exception as e:
        return {'error': str(e)}, 500


def handle_request(full_path, action, data):
    operation_config = config.get(full_path)
    if not operation_config:
        return {"error": "Invalid operation"}, 400
    collection_name = operation_config['collection']
    if action not in operation_config['supported_actions']:
        return {"error": "Invalid action"}, 400
    
    db = get_database()
    collection = db[collection_name]
  
    if action in ['add', 'create']:
        extra_info = operation_config.get(action, [])
        result, status = add_items(collection, data, extra_info)
    elif action in ['search', 'view', 'export']:
        extra_info = operation_config.get(action, {})
        result, status = search_items(collection, data, extra_info)
    elif action in ['manage', 'update', 'edit']:
        extra_info = operation_config.get(action, {})
        result, status = update_items(collection, data, extra_info)
    elif action == 'delete':
        result, status = delete_items(collection, data)
    else:
        return jsonify({"error": "Unsupported operation"}), 400
    return jsonify(result), status


@max_routes_bp.route('/<path1>/<action>', methods=['POST'])
def handle_route_1(path1, action):
    try:
        data = request.json
        full_path = path1
        response = handle_request(full_path, action, data)
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@max_routes_bp.route('/<path1>/<path2>/<action>', methods=['POST'])
def handle_route_2(path1, path2, action):
    try:
        data = request.json
        full_path = f"{path1}/{path2}"
        response = handle_request(full_path, action, data)
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@max_routes_bp.route('/<path1>/<path2>/<path3>/<action>', methods=['POST'])
def handle_route_3(path1, path2, path3, action):
    try:
        data = request.json
        full_path = f"{path1}/{path2}/{path3}"
        response = handle_request(full_path, action, data)
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500
