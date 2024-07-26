import openai
import pymongo
from pymongo import MongoClient
import json  # Importing the json module

# Set up OpenAI API key
openai.api_key = 'sk-proj-QwkkbzdKsPOdz9LoD6vmT3BlbkFJCo9zDEtqHWk4KrmavDBD'

# MongoDB connection details
mongo_uri = "mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns"
client = MongoClient(mongo_uri)
db = client['PCL_Interns']
collection = db['GOL_PerformanceGoals']

# Function to make suggestions using OpenAI
def make_suggestions(prompt_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_text}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

# Function to gather input for a field with suggestions
def gather_input(field_name, suggestion_prompt):
    suggestion = make_suggestions(suggestion_prompt)
    print(f"Suggestion for {field_name}: {suggestion}")
    return input(f"Please provide the {field_name}: ")

# Function to check if the goal is SMART
def is_smart(goal):
    issues = []
    # Check Specific
    if not goal.get('Description') or goal['Description'] == 'sdfghjkgdfg12345678':
        issues.append("Description is missing or not specific enough.")
    # Check Measurable
    if not goal.get('Measurements') or not goal['Measurements'].get('Target Value') or goal['Measurements']['Target Value'] == 'None':
        issues.append("Measurement details are missing or not specific.")
    # Check Achievable
    if not goal.get('Tasks') or not goal['Tasks'].get('Completion Percentage') or goal['Tasks']['Completion Percentage'] == '0':
        issues.append("Tasks or completion criteria are missing or unclear.")
    # Check Relevant
    if not goal.get('Category') or goal['Category'] == '12345678':
        issues.append("Relevance category is missing.")
    # Check Time-bound
    if not goal.get('Start Date') or not goal.get('Target Completion Date') or goal['Target Completion Date'] == '345678':
        issues.append("Time frame details are missing.")
    return issues

# Prompt for Goal Name
goal_name = input("Enter the Goal Name: ")
print(goal_name)

# Retrieve goal from MongoDB
goal = collection.find_one({"Goals.Basic Info.Goal Name": goal_name})

if goal:
    goal_details = goal['Goals']
    issues = is_smart(goal_details)
    if issues:
        print(f"Goal '{goal_details['Basic Info']['Goal Name']}' is not SMART for the following reasons:")
        for issue in issues:
            print(f" - {issue}")
            if 'Description' in issue:
                user_input = gather_input("Description", "Suggest a description for the goal to increase social media presence.")
                goal_details['Basic Info']['Description'] = user_input
            elif 'Measurement details' in issue:
                user_input = gather_input("Target Value", "What target value should be set for the increase in social media presence?")
                goal_details['Measurements']['Target Value'] = user_input
            elif 'Tasks' in issue:
                user_input = gather_input("Completion Percentage", "What is the current completion percentage for the task?")
                goal_details['Tasks']['Completion Percentage'] = user_input
            elif 'Relevance category' in issue:
                user_input = gather_input("Category", "What category does the goal to increase social media presence fall into?")
                goal_details['Basic Info']['Category'] = user_input
            elif 'Time frame details' in issue:
                user_input = gather_input("Target Completion Date", "Suggest a target completion date for a goal aimed at increasing social media presence.")
                goal_details['Basic Info']['Target Completion Date'] = user_input

        # Print the updated SMART goal
        print("\nUpdated SMART Goal:")
        print(json.dumps(goal_details, indent=4))

        # Optional: Store the updated goal back to MongoDB
        collection.update_one(
            {"Goals.Basic Info.Goal Name": goal_name},
            {"$set": {"Goals": goal_details}}
        )

    else:
        print(f"Goal '{goal_details['Basic Info']['Goal Name']}' is already SMART.")
else:
    print(f"Goal '{goal_name}' not found in the database.")

print("Goal processing completed.")
