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
    dbname = 'dev1'
    return f'mongodb://{username}:{password}@{host}:{port}/{dbname}'

def call_generic_function(operation_config, data, allowed_employees):
    collection_name = operation_config['collection']
    operation = operation_config['operation']
    dbname = 'dev1'
    MONGODB_URI = get_database_url()
    client = MongoClient(MONGODB_URI)
    db = client[dbname]
    collection = db[collection_name]

    private_fields = data.get('private_fields', [])
    
    if operation == 'add':
        return add_items(collection, data)
    elif operation == 'search':
        return search_items(collection, data, private_fields, allowed_employees)
    elif operation == 'manage':
        return manage_items(collection, data, private_fields, allowed_employees)
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

def search_items(collection, data, private_fields, allowed_employees):
    try:
      
        query = data.get('query', {})
        print(private_fields)
        # Ensure the query only fetches allowed employees
        if 'person_name' in query:
            if query['person_name'] not in allowed_employees:
                return {'error': 'Not authorized to view this employee\'s data'}, 403
        else:
            query['person_name'] = {'$in': allowed_employees}

       
        projection = {field: 0 for field in private_fields}
        items = list(collection.find(query, projection))
        for item in items:
            item['_id'] = str(item['_id'])
        return items, 200
    except Exception as e:
        return {'error': str(e)}, 500
def manage_items(collection, data, private_fields, allowed_employees):
    try:
        action = data.get('action')
        query = data.get('query', {})
        
        # Ensure the query only fetches allowed employees
        
      
        if 'person_name' in query:
            if query['person_name'] not in allowed_employees:
                return {'error': 'Not authorized to manage this employee\'s data'}, 403
        else:
            query['person_name'] = {'$in': allowed_employees}
      
        if action == 'get':
            projection = {field: 0 for field in private_fields}
            items = list(collection.find(query, projection))
            for item in items:
                item['_id'] = str(item['_id'])
            return items, 200

        elif action == 'update':
            update_data = data.get('update_data', {})
            if not update_data:
                return {'error': 'No update data provided'}, 400

            # Ensure update_data does not contain fields that are private
            for field in private_fields:
                if field in update_data:
                    del update_data[field]

            result = collection.update_many(query, {'$set': update_data})
            if result.matched_count == 0:
                return {'message': 'No items matched the query'}, 404

            projection = {field: 0 for field in private_fields}
            updated_items = list(collection.find(query, projection))
            for item in updated_items:
                item['_id'] = str(item['_id'])
            return updated_items, 200

        elif action == 'delete':
            result = collection.delete_many(query)
            if result.deleted_count == 0:
                return {'message': 'No items matched the query'}, 404

            projection = {field: 0 for field in private_fields}
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
    db = client['dev1']
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
    db = client['dev1']
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
        db = client['dev1']
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

def get_managed_employees(manager_name):
    client = MongoClient(get_database_url())
    db = client['dev1']
    employees_collection = db['HRM_employee_details']
    
    managed_employees = list(employees_collection.find({'manager_name': manager_name}))
    managed_employee_names = [employee['person_name'] for employee in managed_employees]
   
    managers_managed_by_current_manager = list(employees_collection.find({'manager_name': manager_name, 'working_as_manager': 'Yes'}))
    for manager in managers_managed_by_current_manager:
        additional_managed_employee_names = get_managed_employees(manager['person_name'])
        managed_employee_names.extend(additional_managed_employee_names)
  
    return managed_employee_names

def collection_permission_required(config):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            current_user = kwargs.get('current_user')
            data = request.get_json()
            action = data.get('function')
            operation_config = config.get(action)
            print(current_user['role'])
            print(current_user['username'])
            # update_role_permissions_with_managed_employees(current_user['username'])
        
            if not operation_config:
                return jsonify({'message': f'Permission denied for operation: {action}'}), 403
            
            collection = operation_config['collection']
            client = MongoClient(get_database_url())
            db = client['dev1']
            roles_collection = db['rolePermission']
            
            role_permissions = roles_collection.find_one({'role': current_user['role']})
            if not role_permissions:
                return jsonify({'message': f'Permission denied for user: {current_user["username"]}'}), 403
            
            allowed_employees = get_managed_employees(current_user['username'])
           
            print(allowed_employees)
            # Check if the user is allowed to access the collection
            collection_info = {'Allowed': allowed_employees, 'fields': role_permissions.get('fields', [])}
            data['private_fields'] = collection_info.get('fields', [])
           

            return f(*args, allowed_employees=allowed_employees, **kwargs)
        
        return decorated
    return wrapper
