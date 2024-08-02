
import json
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from leaveapplications import setup_routes
from test import call_generic_function, register_user, login_user, token_required, collection_permission_required

app = Flask(__name__)
setup_routes(app)
load_dotenv()

# Load the configuration file
with open('/Users/vishalmeena/Downloads/Code_wrap_Latest 4 copy/test/operations_config.json', 'r') as config_file:
    config = json.load(config_file)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/items/wrapper', methods=['POST'])
@token_required
@collection_permission_required(config)
def execute_action(current_user, allowed_employees):
    try:
        data = request.json
        action = data.get('function')
        operation_config = config.get(action)
        if not operation_config:
            return jsonify({'error': f"Operation '{action}' not supported"}), 400
        result = call_generic_function(operation_config, data, allowed_employees)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    # Validate the required fields
    required_fields = ['username', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    result, status = register_user(data)
    return jsonify(result), status

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    # Validate the required fields
    required_fields = ['username', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    result, status = login_user(data, app.config['SECRET_KEY'])
    return jsonify(result), status

if __name__ == '__main__':
    app.run(debug=True, port=3001)
