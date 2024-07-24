from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client['PCL_Interns']
collection = db['P_PerformanceRoles']

@app.route('/add_role', methods=['POST'])
def add_role():
    data = request.get_json()

    # Insert new role into the database
    new_role = {
        "name": data.get('name'),
        "description": data.get('description'),
        "role_type": data.get('role_type'),
        "allow_role_to_view_worker_manager_and_participant_ratings_comments_and_questionnaires": data.get('allow_role_to_view_worker_manager_and_participant_ratings_comments_and_questionnaires'),
        "status": data.get('status'),
        "in_use": data.get('in_use'),
        "from_date": data.get('from_date'),
        "to_date": data.get('to_date')
    }

    result = collection.insert_one(new_role)
    return jsonify({"msg": "Role added successfully", "id": str(result.inserted_id)}), 201

@app.route('/update_role', methods=['POST'])
def update_role():
    data = request.get_json()

    # Update role in the database
    updated_role = {
        "description": data.get('description'),
        "role_type": data.get('role_type'),
        "allow_role_to_view_worker_manager_and_participant_ratings_comments_and_questionnaires": data.get('allow_role_to_view_worker_manager_and_participant_ratings_comments_and_questionnaires'),
        "status": data.get('status'),
        "in_use": data.get('in_use'),
        "from_date": data.get('from_date'),
        "to_date": data.get('to_date')
    }

    result = collection.update_one({"name": data.get('name')}, {"$set": updated_role})
    if result.matched_count > 0:
        return jsonify({"msg": "Role updated successfully"}), 200
    else:
        return jsonify({"msg": "Role not found"}), 404

@app.route('/get_roles', methods=['POST'])
def get_roles():
    data = request.get_json()

    query = {}
    if data.get('name'):
        query['name'] = data.get('name')
    if data.get('status'):
        query['status'] = data.get('status')

    roles = list(collection.find(query))
    for role in roles:
        role['_id'] = str(role['_id'])  # Convert ObjectId to string

    return jsonify(roles), 200

if __name__ == '__main__':
    app.run(debug=True)
