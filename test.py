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
    
    if operation == 'add':
        return add_items(collection, data)
    elif operation == 'search':
        return search_items(collection, data)
    elif operation == 'manage':
        return manage_items(collection, data)
    else:
        raise ValueError('Unsupported operation')


def get_collection_schema(collection):
    sample_document = collection.find_one()
    if not sample_document:
        return {}
    schema = {key: type(value).__name__ for key, value in sample_document.items()}
    return schema


def validate_data_schema(schema, data):
    for item in data:
        for key, value in item.items():
            if key not in schema:
                return False
            if schema[key] != type(value).__name__:
                return False
    return True


def add_items(collection, data):
    try:
        items = data.get('items', [])
        if not isinstance(items, list):
            items = [items]
        
        # Get the schema of the collection
        schema = get_collection_schema(collection)
        if  schema:
            if not validate_data_schema(schema, items):
                return {'error': 'Data schema does not match collection schema'}, 400
            
        # Validate the items against the schema


        result = collection.insert_many(items)
        inserted_ids = [str(item_id) for item_id in result.inserted_ids]
        return {'inserted_ids': inserted_ids}, 201
    except Exception as e:
        return {'error': str(e)}, 500
    
def search_items(collection, data):
    try:
        query = data.get('query', {})
        items = list(collection.find(query))
        for item in items:
            item['_id'] = str(item['_id'])
        return items, 200
    except Exception as e:
        return {'error': str(e)}, 500

def manage_items(collection, data):
    try:
        action = data.get('action')
        query = data.get('query', {})

        if action == 'get':
            items = list(collection.find(query))
            for item in items:
                item['_id'] = str(item['_id'])
            return items, 200

        elif action == 'update':
            update_data = data.get('update_data', {})
            if not update_data:
                return {'error': 'No update data provided'}, 400
            result = collection.update_many(query, {'$set': update_data})
            if result.matched_count == 0:
                return {'message': 'No items matched the query'}, 404
            updated_items = list(collection.find(query))
            for item in updated_items:
                item['_id'] = str(item['_id'])
            return updated_items, 200

        elif action == 'delete':
            result = collection.delete_many(query)
            if result.deleted_count == 0:
                return {'message': 'No items matched the query'}, 404
            return {'message': f'{result.deleted_count} items deleted'}, 200

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
        
            if not operation_config:
                return jsonify({'message': f'Permission denied for operation: {action}'}), 403
            
            collection = operation_config['collection']
            client = MongoClient(get_database_url())
            db = client['PCL_Interns']
            roles_collection = db['rolePermission']
            
            role_permissions = roles_collection.find_one({'role': current_user['role']})
            if not role_permissions or collection not in role_permissions.get('collections', []):
                return jsonify({'message': f'Permission denied for collection: {collection}'}), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return wrapper