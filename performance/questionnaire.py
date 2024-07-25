from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime

app = Flask(__name__)

# MongoDB configuration
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client.PCL_Interns
collection = db.P_Questionnaires

@app.route('/add_questionnaire', methods=['POST'])
def add_questionnaire():
    data = request.get_json()
    
    # Insert new questionnaire template into the database
    new_template = {
        "questionnaire_template_id": data.get('questionnaire_template_id'),
        "name": data.get('name'),
        "description": data.get('description'),
        "questions": data.get('questions', []),
        "creation_date": datetime.datetime.strptime(data.get('creation_date'), "%Y-%m-%dT%H:%M:%S.%fZ")
    }

    result = collection.insert_one(new_template)
    return jsonify({"message": "Questionnaire template added", "id": str(result.inserted_id)}), 201

@app.route('/update_questionnaire', methods=['POST'])
def update_questionnaire():
    data = request.get_json()
    template_id = data.get('questionnaire_template_id')
    
    # Update questionnaire template in the database
    update_data = {
        "name": data.get('name'),
        "description": data.get('description'),
        "questions": data.get('questions', []),
        "creation_date": datetime.datetime.strptime(data.get('creation_date'), "%Y-%m-%dT%H:%M:%S.%fZ")
    }

    result = collection.update_one({"questionnaire_template_id": template_id}, {"$set": update_data})
    if result.matched_count > 0:
        return jsonify({"message": "Questionnaire template updated"}), 200
    else:
        return jsonify({"message": "Questionnaire template not found"}), 404

@app.route('/get_questionnaire', methods=['POST'])
def get_questionnaire():
    data = request.get_json()
    template_id = data.get('questionnaire_template_id')
    template = collection.find_one({"questionnaire_template_id": template_id})

    if template:
        template['_id'] = str(template['_id'])
        template['creation_date'] = template['creation_date'].isoformat() + 'Z'
        return jsonify(template)
    else:
        return jsonify({"message": "Questionnaire template not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
