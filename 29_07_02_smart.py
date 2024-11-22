from flask import Flask, request, jsonify
import openai
import pymongo
from pymongo import MongoClient
import json
from bson import ObjectId

app = Flask(__name__)

# Set up OpenAI API key
# openai.api_key = ''

# MongoDB connection details
mongo_uri = "mongodb://dev1_user:dev1_pass@172.191.245.199:27017/dev1"
client = MongoClient(mongo_uri)
db = client['dev1']
collection = db['PGM_goal']

print("Connected to MongoDB")

# Load detailed prompt and verification prompt from JSON file
with open('prompt.json', 'r') as f:
    prompt_data = json.load(f)
    detailed_prompt = prompt_data
    verification_prompts = prompt_data.get("verification_prompt", {})

print("Loaded prompt file")

def make_suggestions(prompt_text):
    print(f"Making suggestions for prompt: {prompt_text}")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_text}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

def verify_relevance(goal_name, text, text_type):
    if not isinstance(verification_prompts, dict) or text_type not in verification_prompts:
        raise ValueError("Verification prompt is not defined correctly.")
    prompt_text = verification_prompts[text_type].replace("{goal_name}", goal_name).replace("{description}", text).replace("{target_value}", text).replace("{task_name}", text)
    response = make_suggestions(prompt_text)
    return 'yes' in response.lower()

def gather_input(field_name, suggestion_prompt):
    suggestion = make_suggestions(suggestion_prompt)
    print(f"Suggestion for {field_name}: {suggestion}")
    return suggestion

def is_smart(goal):
    issues = []
    suggestions = {}
    print("Checking if the goal is SMART")
    
    # Check Specific (Description)
    if not goal['basic_info'].get('description'):
        issues.append("Description is missing or not specific enough.")
        suggestions['description'] = gather_input("Description", f"Suggest a description for the goal '{goal['basic_info']['goal_name']}'.")
    elif not verify_relevance(goal['basic_info']['goal_name'], goal['basic_info']['description'], 'description'):
        issues.append("Description is not relevant or specific to the goal name.")
        suggestions['description'] = gather_input("Description", f"Suggest a description for the goal '{goal['basic_info']['goal_name']}'.")
    
    # Check Measurable (Measurements)
    measurement_fields = ['target_value', 'measurement_name']
    for field in measurement_fields:
        if not goal['measurements'].get(field) or goal['measurements'][field] == 'None':
            issues.append(f"Measurement {field} details are missing or not specific.")
            suggestions[field] = gather_input(field, f"Suggest a {field} for the goal '{goal['basic_info']['goal_name']}'.")
        elif not verify_relevance(goal['basic_info']['goal_name'], goal['measurements'][field], 'measurement_target_value'):
            issues.append(f"Measurement {field} is not relevant or specific to the goal name.")
            suggestions[field] = gather_input(field, f"Suggest a {field} for the goal '{goal['basic_info']['goal_name']}'.")
    
    # Check Achievable (Tasks)
    task_fields = ['name', 'completion_percentage']
    for field in task_fields:
        if not goal['tasks'].get(field) or goal['tasks'][field] == 'None':
            issues.append(f"Task {field} details are missing or not specific.")
            suggestions[field] = gather_input(field, f"Suggest a task {field} for the goal '{goal['basic_info']['goal_name']}'.")
        elif not verify_relevance(goal['basic_info']['goal_name'], goal['tasks'][field], 'task_name'):
            issues.append(f"Task {field} is not relevant or specific to the goal name.")
            suggestions[field] = gather_input(field, f"Suggest a task {field} for the goal '{goal['basic_info']['goal_name']}'.")
    
    # Check Relevant (Category)
    if not goal['basic_info'].get('category'):
        issues.append("Relevance category is missing.")
        suggestions['category'] = gather_input("Category", f"Suggest a category for the goal '{goal['basic_info']['goal_name']}'.")
    
    # Check Time-bound (Dates)
    if not goal['basic_info'].get('start_date') or not goal['basic_info'].get('target_completion_date'):
        issues.append("Time frame details are missing.")
        suggestions['time_frame'] = gather_input("Time Frame", f"Suggest a time frame for the goal '{goal['basic_info']['goal_name']}'.")

    return issues, suggestions

def convert_object_id(goal):
    if '_id' in goal:
        goal['_id'] = str(goal['_id'])
    return goal

@app.route('/check_smart', methods=['POST'])
def check_smart():
    data = request.json
    goal_name = data.get('goal_name')
    goal = collection.find_one({"basic_info.goal_name": goal_name})
    
    if goal:
        goal_details = goal
        issues, suggestions = is_smart(goal_details)
        if issues:
            return jsonify({"goal_name": goal_name, "issues": issues, "suggestions": suggestions, "status": "not SMART"})
        else:
            return jsonify({"goal_name": goal_name, "status": "SMART"})
    else:
        return jsonify({"error": "Goal not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
