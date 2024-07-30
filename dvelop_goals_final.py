import openai
import pandas as pd
from pymongo import MongoClient
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Set your OpenAI API key
# openai.api_key = ''

# MongoDB connection details
MONGODB_URI = "mongodb://dev1_user:dev1_pass@172.191.245.199:27017/dev1"
DATABASE_NAME = "dev1"

# Function to generate goals using OpenAI API
def generate_goals(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates goals based on input."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        n=5,
        stop=None,
        temperature=0.7
    )
    return [choice['message']['content'].strip() for choice in response.choices]

# Function to fetch goals from a specified goal plan from MongoDB
def fetch_goals_from_goal_plan(goal_plan_name, db):
    goal_plan = db.PGM_goal_plan.find_one({"details.goal_plan_name": goal_plan_name})
    if not goal_plan:
        return []
    return [goal for goal in goal_plan["goals"]]

# Function to read the prompt template from a file
def read_prompt_template(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Function to recommend personalized goals based on input prompt
def recommend_personalized_goals(goal_plan_name, department, db):
    goal_plan_goals = fetch_goals_from_goal_plan(goal_plan_name, db)
    if not goal_plan_goals:
        return {"error": f"Goal plan '{goal_plan_name}' not found."}

    # Read the prompt template
    prompt_template = read_prompt_template("prompt.txt")

    # Create the prompt
    prompt = prompt_template.format(goal_plan_name=goal_plan_name, goal_list=", ".join(goal_plan_goals), department=department)
    
    generated_goals = generate_goals(prompt)[:5]  # Limit to 5 goals

    goals_json = []
    for i, goal in enumerate(generated_goals):
        goal_sections = goal.split("Subpoints/Targets:")
        goal_main = goal_sections[0].strip()
        subpoints = goal_sections[1].strip() if len(goal_sections) > 1 else ""
        subpoints_list = [subpoint.strip() for subpoint in subpoints.split("\n") if subpoint.strip()]

        goal_main_sections = goal_main.split("\n")
        goal_name = goal_main_sections[0].replace("Goal Name: ", "").strip()
        description = goal_main_sections[1].replace("Description: ", "").strip() if len(goal_main_sections) > 1 else ""

        goals_json.append({
            "goal": f"Goal {i+1}",
            "goal_name": goal_name,
            "description": description,
            "subpoints": subpoints_list
        })

    return {
        "goal_plan": goal_plan_name,
        "department": department,
        "goal_plan_goals": goal_plan_goals,
        "recommended_goals": goals_json
    }

@app.route('/recommend_goals', methods=['POST'])
def recommend_goals():
    data = request.json
    goal_plan_name = data.get('goal_plan_name')
    department = data.get('department')

    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]

    response = recommend_personalized_goals(goal_plan_name, department, db)
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
