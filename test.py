
from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import bcrypt
import jwt
import datetime
from functools import wraps

load_dotenv()

app = Flask(__name__)

def get_database_url():
    username = os.getenv('MONGODB_USERNAME')
    password = os.getenv('MONGODB_PASSWORD')
    host = os.getenv('MONGODB_HOST', 'localhost')
    port = os.getenv('MONGODB_PORT', '27017')
    dbname = 'PCL_Interns'
    return f'mongodb://{username}:{password}@{host}:{port}/{dbname}'

def call_generic_function(operation_config, data):
    collection_name = operation_config['collection']
    operation = operation_config['operation']
    dbname = 'PCL_Interns'
    MONGODB_URI = get_database_url()
    client = MongoClient(MONGODB_URI)
    db = client[dbname]
    collection = db[collection_name]
    
    allowed_fields = data.get('allowed_fields', [])
    
    if operation == 'add':
        return add_items(collection, data)
    elif operation == 'search':
        return search_items(collection, data, allowed_fields)
    elif operation == 'manage':
        return manage_items(collection, data, allowed_fields)
    else:
        raise ValueError('Unsupported operation')

def get_collection_schema(collection):
    sample_document = collection.find_one()
    if not sample_document:
        return {}
    schema = {}
    for key, value in sample_document.items():
        if isinstance(value, dict):
            schema[key] = {k: type(v).__name__ for k, v in value.items()}
        else:
            schema[key] = type(value).__name__
    return schema

def validate_data_schema(schema, data):
    def validate(schema, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key not in schema:
                    return False
                if isinstance(value, dict):
                    if not validate(schema[key], value):
                        return False
                elif schema[key] != type(value).__name__:
                    return False
        return True

    return all(validate(schema, item) for item in data)

def add_items(collection, data):
    try:
        items = data.get('items', [])
        if not isinstance(items, list):
            items = [items]
        
        # Get the schema of the collection
        schema = get_collection_schema(collection)
        if schema:
            if not validate_data_schema(schema, items):
                return {'error': 'Data schema does not match collection schema'}, 400
            
        result = collection.insert_many(items)
        inserted_ids = [str(item_id) for item_id in result.inserted_ids]
        return {'inserted_ids': inserted_ids}, 201
    except Exception as e:
        return {'error': str(e)}, 500

def search_items(collection, data, allowed_fields):
    try:
        query = data.get('query', {})
        
        # Create a projection to exclude allowed fields for the user
        projection = {field: 0 for field in allowed_fields}
        
        # Perform the search query
        items = list(collection.find(query, projection))
        
        # Convert ObjectId to string for JSON serialization
        for item in items:
            item['_id'] = str(item['_id'])
        
        return items, 200
    except Exception as e:
        return {'error': str(e)}, 500

def manage_items(collection, data, allowed_fields):
    try:
        action = data.get('action')
        query = data.get('query', {})
        
        if action == 'get':
            projection = {field: 0 for field in allowed_fields}
            items = list(collection.find(query, projection))
            for item in items:
                item['_id'] = str(item['_id'])
            return items, 200

        elif action == 'update':
            update_data = data.get('update_data', {})
            if not update_data:
                return {'error': 'No update data provided'}, 400
            
            for field in allowed_fields:
                if field in update_data:
                    del update_data[field]

            result = collection.update_many(query, {'$set': update_data})
            if result.matched_count == 0:
                return {'message': 'No items matched the query'}, 404
        
            # Fetch the updated items without private fields
            projection = {field: 0 for field in allowed_fields}
            updated_items = list(collection.find(query, projection))
            for item in updated_items:
                item['_id'] = str(item['_id'])
            return updated_items, 200

        elif action == 'delete':
            result = collection.delete_many(query)
            if result.deleted_count == 0:
                return {'message': 'No items matched the query'}, 404
            
            # Return the remaining items without private fields
            projection = {field: 0 for field in allowed_fields}
            remaining_items = list(collection.find(query, projection))
            for item in remaining_items:
                item['_id'] = str(item['_id'])
            return {'message': f'{result.deleted_count} items deleted', 'remaining_items': remaining_items}, 200

        else:
            return {'error': 'Invalid action specified'}, 400

    except Exception as e:
        return {'error': str(e)}, 500

def register_user(data):
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    client = MongoClient(get_database_url())
    db = client['PCL_Interns']
    users_collection = db['users']
    user = {
        'username': data['username'],
        'password': hashed_password,
        'role': data.get('role', 'user')  # Default role is 'user'
    }
    
    users_collection.insert_one(user)
    return {'message': 'User registered successfully'}, 201

def login_user(data, secret_key):
    client = MongoClient(get_database_url())
    db = client['PCL_Interns']
    users_collection = db['users']
    user = users_collection.find_one({'username': data['username']})
    
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
        token = jwt.encode({
            'username': user['username'],
            'role': user['role'],
            'permissions': user.get('permissions', []),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, secret_key, algorithm="HS256")
        
        return {'token': token}, 200
    
    return {'message': 'Invalid credentials'}, 401

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        client = MongoClient(get_database_url())
        db = client['PCL_Interns']
        users_collection = db['users']
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            current_user = users_collection.find_one({'username': data['username']})
            if not current_user:
                return jsonify({'message': 'Token is invalid!'}), 401
            kwargs['current_user'] = current_user
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(*args, **kwargs)
    
    return decorated

def permission_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if current_user['role'] not in roles:
                return jsonify({'message': 'Permission denied!'}), 403
            return f(*args, **kwargs)
        return decorated
    return wrapper

def collection_permission_required(config):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = kwargs.get('current_user')
            data = request.get_json()
            action = data.get('function', [])
            operation_config = config.get(action)
            employee_name = data.get('employee_name')
            
            if not operation_config:
                return jsonify({'message': f'Permission denied for operation: {action}'}), 403
            
            collection = operation_config['collection']
            client = MongoClient(get_database_url())
            db = client['PCL_Interns']
            roles_collection = db['rolePermission']
            
            role_permissions = roles_collection.find_one({'role': current_user['role']})
            if not role_permissions or collection not in [col['collectionname'] for col in role_permissions.get('collections', [])]:
                return jsonify({'message': f'Permission denied for collection: {collection}'}), 403
            
            # Check if the user is allowed to access the collection
            collection_info = next((col for col in role_permissions['collections'] if col['collectionname'] == collection), None)
            if not collection_info:
                return jsonify({'message': f'Permission denied for collection: {collection}'}), 403
            
            allowed_list = collection_info.get('Allowed', [])
            allowed_user_info = next((user_info for user_info in allowed_list if user_info['user'] == employee_name or user_info['user'] == 'ALL'), None)
            if not allowed_user_info:
                return jsonify({'message': 'Employee name is required and must be in the allowed list'}), 403
            
            # Check fields
            data['allowed_fields'] = allowed_user_info.get('fields', [])
            
            return f(*args, **kwargs)
        
        return decorated
    return wrapper






# from flask import Flask, request, jsonify
# from pymongo import MongoClient
# from dotenv import load_dotenv
# import os
# import bcrypt
# import jwt
# import datetime
# from functools import wraps

# load_dotenv()

# app = Flask(__name__)

# def get_database_url():
#     username = os.getenv('MONGODB_USERNAME')
#     password = os.getenv('MONGODB_PASSWORD')
#     host = os.getenv('MONGODB_HOST', 'localhost')
#     port = os.getenv('MONGODB_PORT', '27017')
#     dbname = 'PCL_Interns'
#     return f'mongodb://{username}:{password}@{host}:{port}/{dbname}'

# def call_generic_function(operation_config, data):
#     collection_name = operation_config['collection']
#     operation = operation_config['operation']
#     dbname = 'PCL_Interns'
#     MONGODB_URI = get_database_url()
#     client = MongoClient(MONGODB_URI)
#     db = client[dbname]
#     collection = db[collection_name]
    
#     allowed_fields = data.get('allowed_fields', [])
    
#     if operation == 'add':
#         return add_items(collection, data)
#     elif operation == 'search':
#         return search_items(collection, data, allowed_fields)
#     elif operation == 'manage':
#         return manage_items(collection, data, allowed_fields)
#     else:
#         raise ValueError('Unsupported operation')

# def get_collection_schema(collection):
#     sample_document = collection.find_one()
#     if not sample_document:
#         return {}
#     schema = {}
#     for key, value in sample_document.items():
#         if isinstance(value, dict):
#             schema[key] = {k: type(v).__name__ for k, v in value.items()}
#         else:
#             schema[key] = type(value).__name__
#     return schema

# def validate_data_schema(schema, data):
#     def validate(schema, data):
#         if isinstance(data, dict):
#             for key, value in data.items():
#                 if key not in schema:
#                     return False
#                 if isinstance(value, dict):
#                     if not validate(schema[key], value):
#                         return False
#                 elif schema[key] != type(value).__name__:
#                     return False
#         return True

#     return all(validate(schema, item) for item in data)

# def add_items(collection, data):
#     try:
#         items = data.get('items', [])
#         if not isinstance(items, list):
#             items = [items]
        
#         # Get the schema of the collection
#         schema = get_collection_schema(collection)
#         if schema:
#             if not validate_data_schema(schema, items):
#                 return {'error': 'Data schema does not match collection schema'}, 400
            
#         result = collection.insert_many(items)
#         inserted_ids = [str(item_id) for item_id in result.inserted_ids]
#         return {'inserted_ids': inserted_ids}, 201
#     except Exception as e:
#         return {'error': str(e)}, 500

# def search_items(collection, data, allowed_fields):
#     try:
#         query = data.get('query', {})
#         projection = {field: 0 for field in allowed_fields}
#         items = list(collection.find(query, projection))
#         for item in items:
#             item['_id'] = str(item['_id'])
#         return items, 200
#     except Exception as e:
#         return {'error': str(e)}, 500
    



# def manage_items(collection, data, allowed_fields):
#     try:
#         action = data.get('action')
#         query = data.get('query', {})
        
#         if action == 'get':
#             projection = {field: 0 for field in allowed_fields}
#             items = list(collection.find(query, projection))
#             for item in items:
#                 item['_id'] = str(item['_id'])
#             return items, 200

#         elif action == 'update':
#             update_data = data.get('update_data', {})
#             if not update_data:
#                 return {'error': 'No update data provided'}, 400
            

#             for field in allowed_fields:
#                 if field in update_data:
#                     del update_data[field]

#             print(update_data)        
#             result = collection.update_many(query, {'$set': update_data})
#             if result.matched_count == 0:
#                 return {'message': 'No items matched the query'}, 404
        
#             # Fetch the updated items without private fields
#             # print(allowed_fields)
#             projection = {field: 0 for field in allowed_fields}
#             updated_items = list(collection.find(query, projection))
#             for item in updated_items:
#                 item['_id'] = str(item['_id'])
#             return updated_items, 200

#         elif action == 'delete':
#             result = collection.delete_many(query)
#             if result.deleted_count == 0:
#                 return {'message': 'No items matched the query'}, 404
            
#             # Return the remaining items without private fields
#             projection = {field: 0 for field in allowed_fields}
#             remaining_items = list(collection.find(query, projection))
#             for item in remaining_items:
#                 item['_id'] = str(item['_id'])
#             return {'message': f'{result.deleted_count} items deleted', 'remaining_items': remaining_items}, 200

#         else:
#             return {'error': 'Invalid action specified'}, 400

#     except Exception as e:
#         return {'error': str(e)}, 500

# def register_user(data):
#     hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
#     client = MongoClient(get_database_url())
#     db = client['PCL_Interns']
#     users_collection = db['users']
#     user = {
#         'username': data['username'],
#         'password': hashed_password,
#         'role': data.get('role', 'user')  # Default role is 'user'
#     }
    
#     users_collection.insert_one(user)
#     return {'message': 'User registered successfully'}, 201

# def login_user(data, secret_key):
#     client = MongoClient(get_database_url())
#     db = client['PCL_Interns']
#     users_collection = db['users']
#     user = users_collection.find_one({'username': data['username']})
    
#     if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password']):
#         token = jwt.encode({
#             'username': user['username'],
#             'role': user['role'],
#             'permissions': user.get('permissions', []),
#             'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
#         }, secret_key, algorithm="HS256")
        
#         return {'token': token}, 200
    
#     return {'message': 'Invalid credentials'}, 401

# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         client = MongoClient(get_database_url())
#         db = client['PCL_Interns']
#         users_collection = db['users']
#         token = None
#         if 'x-access-token' in request.headers:
#             token = request.headers['x-access-token']
        
#         if not token:
#             return jsonify({'message': 'Token is missing!'}), 401
        
#         try:
#             data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
#             current_user = users_collection.find_one({'username': data['username']})
#             if not current_user:
#                 return jsonify({'message': 'Token is invalid!'}), 401
#             kwargs['current_user'] = current_user
#         except jwt.ExpiredSignatureError:
#             return jsonify({'message': 'Token has expired!'}), 401
#         except jwt.InvalidTokenError:
#             return jsonify({'message': 'Token is invalid!'}), 401

#         return f(*args, **kwargs)
    
#     return decorated

# def permission_required(*roles):
#     def wrapper(f):
#         @wraps(f)
#         def decorated(*args, **kwargs):
#             current_user = kwargs.get('current_user')
#             if current_user['role'] not in roles:
#                 return jsonify({'message': 'Permission denied!'}), 403
#             return f(*args, **kwargs)
#         return decorated
#     return wrapper

# def collection_permission_required(config):
#     def wrapper(f):
#         @wraps(f)
#         def decorated(*args, **kwargs):
#             current_user = kwargs.get('current_user')
#             data = request.get_json()
#             action = data.get('function', [])
#             operation_config = config.get(action)
#             employee_name = data.get('employee_name')
            
#             if not operation_config:
#                 return jsonify({'message': f'Permission denied for operation: {action}'}), 403
            
#             collection = operation_config['collection']
#             client = MongoClient(get_database_url())
#             db = client['PCL_Interns']
#             roles_collection = db['rolePermission']
            
#             role_permissions = roles_collection.find_one({'role': current_user['role']})
#             if not role_permissions or collection not in [col['collectionname'] for col in role_permissions.get('collections', [])]:
#                 return jsonify({'message': f'Permission denied for collection: {collection}'}), 403
            
#             # Check if the user is allowed to access the collection
#             collection_info = next((col for col in role_permissions['collections'] if col['collectionname'] == collection), None)
#             if not collection_info:
#                 return jsonify({'message': f'Permission denied for collection: {collection}'}), 403
            
#             allowed_list = collection_info.get('Allowed', [])
#             if allowed_list[0] != 'ALL':
#                 if not employee_name or employee_name not in allowed_list:
#                     return jsonify({'message': 'Employee name is required and must be in the allowed list'}), 403
            
#             # Check fields
#             data['allowed_fields'] = collection_info.get('fields', [])
            
#             return f(*args, **kwargs)
        
#         return decorated
#     return wrapper
