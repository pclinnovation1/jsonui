import openai
import pymongo
from pymongo import MongoClient
import json
from bson import ObjectId

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

# Debugging: Print type and content of verification_prompts
print(f"Type of verification_prompts: {type(verification_prompts)}")
print(f"Content of verification_prompts: {verification_prompts}")

# Function to make suggestions using OpenAI
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

# Function to verify if a given text is relevant to the goal name
def verify_relevance(goal_name, text, text_type):
    if not isinstance(verification_prompts, dict) or text_type not in verification_prompts:
        raise ValueError("Verification prompt is not defined correctly.")
    prompt_text = verification_prompts[text_type].replace("{goal_name}", goal_name).replace("{text}", text).replace("{description}", text).replace("{target_value}", text).replace("{task_name}", text)
    response = make_suggestions(prompt_text)
    return 'yes' in response.lower()

# Function to gather input for a field with suggestions
def gather_input(field_name, suggestion_prompt):
    suggestion = make_suggestions(suggestion_prompt)
    print(f"Suggestion for {field_name}: {suggestion}")
    return input(f"Please provide the {field_name}: ")

# Function to check if the goal is SMART
def is_smart(goal):
    issues = []
    print("Checking if the goal is SMART")
    
    # Check Specific (Description)
    if not goal['basic_info'].get('description'):
        issues.append("Description is missing or not specific enough.")
    elif not verify_relevance(goal['basic_info']['goal_name'], goal['basic_info']['description'], 'description'):
        issues.append("Description is not relevant or specific to the goal name.")
    
    # Check Measurable (Measurements)
    measurement_fields = ['target_value', 'measurement_name']
    for field in measurement_fields:
        if not goal['measurements'].get(field) or goal['measurements'][field] == 'None':
            issues.append(f"Measurement {field} details are missing or not specific.")
        elif not verify_relevance(goal['basic_info']['goal_name'], goal['measurements'][field], 'measurement_target_value'):
            issues.append(f"Measurement {field} is not relevant or specific to the goal name.")
    
    # Check Achievable (Tasks)
    task_fields = ['name', 'completion_percentage']
    for field in task_fields:
        if not goal['tasks'].get(field) or goal['tasks'][field] == 'None':
            issues.append(f"Task {field} details are missing or not specific.")
        elif not verify_relevance(goal['basic_info']['goal_name'], goal['tasks'][field], 'task_name'):
            issues.append(f"Task {field} is not relevant or specific to the goal name.")
    
    # Check Relevant (Category)
    if not goal['basic_info'].get('category'):
        issues.append("Relevance category is missing.")
    
    # Check Time-bound (Dates)
    if not goal['basic_info'].get('start_date') or not goal['basic_info'].get('target_completion_date'):
        issues.append("Time frame details are missing.")
    
    return issues

# Function to convert ObjectId to string for JSON serialization
def convert_object_id(goal):
    if '_id' in goal:
        goal['_id'] = str(goal['_id'])
    return goal

# Prompt for Goal Name
goal_name = input("Enter the Goal Name: ")
print(f"Goal Name entered: {goal_name}")

# Retrieve goal from MongoDB
print(f"Searching for goal with name: {goal_name}")
goal = collection.find_one({"basic_info.goal_name": goal_name})
print(goal)

if goal:
    print(f"Goal found: {goal}")
    goal_details = goal
    issues = is_smart(goal_details)
    if issues:
        print(f"Goal '{goal_details['basic_info']['goal_name']}' is not SMART for the following reasons:")
        for issue in issues:
            print(f" - {issue}")
            if 'Description' in issue:
                user_input = gather_input("Description", f"Suggest a description for the goal '{goal_details['basic_info']['goal_name']}'.")
                goal_details['basic_info']['description'] = user_input
            elif 'Measurement' in issue:
                user_input = gather_input("Target Value", f"Suggest a target value for the goal '{goal_details['basic_info']['goal_name']}'.")
                goal_details['measurements']['target_value'] = user_input
                user_input = gather_input("Measurement Name", f"Suggest a measurement name for the goal '{goal_details['basic_info']['goal_name']}'.")
                goal_details['measurements']['measurement_name'] = user_input
            elif 'Task' in issue:
                user_input = gather_input("Task Name", f"Suggest a task name for the goal '{goal_details['basic_info']['goal_name']}'.")
                goal_details['tasks']['name'] = user_input
                user_input = gather_input("Completion Percentage", f"Suggest a completion percentage for the task '{goal_details['tasks']['name']}'.")
                goal_details['tasks']['completion_percentage'] = user_input
            elif 'Relevance category' in issue:
                user_input = gather_input("Category", f"Suggest a category for the goal '{goal_details['basic_info']['goal_name']}'.")
                goal_details['basic_info']['category'] = user_input
            elif 'Time frame details' in issue:
                user_input = gather_input("Target Completion Date", f"Suggest a target completion date for the goal '{goal_details['basic_info']['goal_name']}'.")
                goal_details['basic_info']['target_completion_date'] = user_input

        # Print the updated SMART goal
        goal_details = convert_object_id(goal_details)
        print("\nUpdated SMART Goal:")
        print(json.dumps(goal_details, indent=4))

        # Optional: Store the updated goal back to MongoDB
        print("Updating goal in MongoDB")
        updated_goal_details = goal_details.copy()
        del updated_goal_details['_id']
        collection.update_one(
            {"basic_info.goal_name": goal_name},
            {"$set": updated_goal_details}
        )

    else:
        print(f"Goal '{goal_details['basic_info']['goal_name']}' is already SMART.")
else:
    print(f"Goal '{goal_name}' not found in the database.")

print("Goal processing completed.")
