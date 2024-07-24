from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime

app = Flask(__name__)

# MongoDB configuration
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client.PCL_Interns
collection = db.P_CheckInTemplates
eligibility_profiles = db.P_EligibilityProfiles

def check_eligibility_profiles(profiles):
    # Check if each profile exists in the eligibility_profiles collection
    for profile in profiles:
        if not eligibility_profiles.find_one({"create_participant_profile.eligibility_profile_definition.name": profile}):
            return False, profile
    return True, None

@app.route('/add_check_in_template', methods=['POST'])
def add_template():
    data = request.get_json()
    
    # Check eligibility profiles
    profiles = data.get('eligibility_profiles')
    is_valid, invalid_profile = check_eligibility_profiles(profiles)
    if not is_valid:
        return jsonify({"message": f"Eligibility profile '{invalid_profile}' not found"}), 400

    # Insert new template into the database
    new_template = {
        "template_type": data.get('template_type'),
        "name": data.get('name'),
        "comments": data.get('comments'),
        "status": data.get('status'),
        "from_date": datetime.datetime.strptime(data.get('from_date'), "%Y-%m-%dT%H:%M:%S.%fZ"),
        "to_date": datetime.datetime.strptime(data.get('to_date'), "%Y-%m-%dT%H:%M:%S.%fZ"),
        "review_period": data.get('review_period'),
        "include_in_performance_document": data.get('include_in_performance_document'),
        "check_in_content": data.get('check_in_content'),
        "eligibility_profiles": profiles
    }

    result = collection.insert_one(new_template)
    return jsonify({"message": "Template added", "id": str(result.inserted_id)}), 201

@app.route('/update_check_in_template', methods=['POST'])
def update_template():
    data = request.get_json()

    # Check eligibility profiles
    profiles = data.get('eligibility_profiles')
    is_valid, invalid_profile = check_eligibility_profiles(profiles)
    if not is_valid:
        return jsonify({"message": f"Eligibility profile '{invalid_profile}' not found"}), 400
    
    # Update template in the database
    updated_template = {
        "template_type": data.get('template_type'),
        "comments": data.get('comments'),
        "status": data.get('status'),
        "from_date": datetime.datetime.strptime(data.get('from_date'), "%Y-%m-%dT%H:%M:%S.%fZ"),
        "to_date": datetime.datetime.strptime(data.get('to_date'), "%Y-%m-%dT%H:%M:%S.%fZ"),
        "review_period": data.get('review_period'),
        "include_in_performance_document": data.get('include_in_performance_document'),
        "check_in_content": data.get('check_in_content'),
        "eligibility_profiles": profiles
    }

    result = collection.update_one({"name": data.get('name')}, {"$set": updated_template})
    if result.matched_count > 0:
        return jsonify({"message": "Template updated"}), 200
    else:
        return jsonify({"message": "Template not found"}), 404

@app.route('/get_check_in_template', methods=['POST'])
def get_template():
    data = request.get_json()
    name = data.get('name')
    template = collection.find_one({"name": name})

    if template:
        template['_id'] = str(template['_id'])
        template['from_date'] = template['from_date'].isoformat() + 'Z'
        template['to_date'] = template['to_date'].isoformat() + 'Z'
        return jsonify(template)
    else:
        return jsonify({"message": "Template not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
