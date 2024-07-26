import openai
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from joblib import dump, load
import ast
import os
from tqdm import tqdm
from pymongo import MongoClient

# Set your OpenAI API key
openai.api_key = 'sk-proj-QwkkbzdKsPOdz9LoD6vmT3BlbkFJCo9zDEtqHWk4KrmavDBD'

# MongoDB connection details
MONGODB_URI = "mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns"
DATABASE_NAME = "PCL_Interns"

# File paths
data_file_path = "generated_employee_data.xlsx"
model_file_path = "goal_embeddings_model.joblib"

# Function to generate embeddings using OpenAI API
def get_embedding(text):
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    return response['data'][0]['embedding']

# Function to batch process embeddings
def get_embeddings_in_batches(texts, batch_size=20):
    embeddings = []
    for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
        batch_texts = texts[i:i + batch_size]
        response = openai.Embedding.create(input=batch_texts, model="text-embedding-ada-002")
        embeddings.extend([res['embedding'] for res in response['data']])
    return embeddings

# Function to load data
def load_data(file_path):
    return pd.read_excel(file_path)

# Function to process data and generate embeddings if needed
def process_data(data):
    # Convert string representation of lists to actual lists
    data["past_goals"] = data["past_goals"].apply(ast.literal_eval)

    # Extract goals and departments
    goals = []
    departments = []

    for index, row in data.iterrows():
        for goal in row["past_goals"]:
            goals.append(goal["goal_name"])
            departments.append(row["department"])

    # Create a DataFrame for goals and departments
    goal_data = pd.DataFrame({"department": departments, "goal_name": goals})

    # Generate embeddings for all goal names if model file does not exist
    if not os.path.exists(model_file_path):
        goal_data["embedding"] = get_embeddings_in_batches(goal_data["goal_name"].tolist())
        # Save the embeddings model
        dump(goal_data, model_file_path)
    else:
        # Load the existing embeddings model
        goal_data = load(model_file_path)

    return goal_data

# Function to calculate cosine similarity between goal embeddings
def calculate_similarity(goal_data):
    goal_embeddings = np.array(goal_data["embedding"].tolist())
    return cosine_similarity(goal_embeddings, goal_embeddings)

# Create a dictionary to map departments to their respective goal indices
def create_department_goal_indices(goal_data):
    department_to_goal_indices = {}
    for department in goal_data["department"].unique():
        department_to_goal_indices[department] = goal_data[goal_data["department"] == department].index.tolist()
    return department_to_goal_indices

# Function to fetch goals from a specified goal plan from MongoDB
def fetch_goals_from_goal_plan(goal_plan_name, db):
    goal_plan = db.GOL_GoalPlans.find_one({"details.goal_plan_name": goal_plan_name})
    if not goal_plan:
        return []
    return [goal["goal_name"] for goal in goal_plan["goals"]]

# Function to fetch detailed goals from GOL_PerformanceGoals from MongoDB
def fetch_detailed_goals(goal_names, db):
    detailed_goals = []
    for goal_name in goal_names:
        goal_info = db.GOL_PerformanceGoals.find_one({"Goals.Basic Info.Goal Name": goal_name})
        if goal_info:
            detailed_goals.append(goal_info)
    return detailed_goals

# Function to recommend goals for a given department or employee based on a goal plan
def recommend_goals_based_on_plan(employee_id_or_department, goal_plan_name, data, goal_data, cosine_similarities, department_to_goal_indices, db, top_n=5):
    if employee_id_or_department.isdigit():
        employee_id = int(employee_id_or_department)
        employee_row = data[data["employee_id"] == employee_id]
        if employee_row.empty:
            print(f"Employee ID {employee_id} not found.")
            return []
        department = employee_row.iloc[0]["department"]
        completed_goals = set(goal["goal_name"] for goal in employee_row.iloc[0]["past_goals"])
    else:
        department = employee_id_or_department
        completed_goals = set()

    goal_plan_goals = fetch_goals_from_goal_plan(goal_plan_name, db)
    if not goal_plan_goals:
        print(f"Goal plan '{goal_plan_name}' not found.")
        return []

    detailed_goals = fetch_detailed_goals(goal_plan_goals, db)

    print(f"Goals from goal plan '{goal_plan_name}': {goal_plan_goals}")
    print(f"Available goal names in goal_data: {goal_data['goal_name'].unique()}")

    # Add detailed goals to goal_data if not present
    for goal in detailed_goals:
        goal_name = goal["Goals"]["Basic Info"]["Goal Name"]
        if goal_name not in goal_data["goal_name"].values:
            goal_data = goal_data.append({"department": department, "goal_name": goal_name, "embedding": get_embedding(goal_name)}, ignore_index=True)

    # Recalculate the cosine similarities
    cosine_similarities = calculate_similarity(goal_data)
    department_to_goal_indices = create_department_goal_indices(goal_data)

    normalized_goal_names = goal_data["goal_name"].str.strip().str.lower()
    goal_plan_indices = []
    for goal in goal_plan_goals:
        goal_normalized = goal.strip().lower()
        if goal_normalized in normalized_goal_names.values:
            goal_index = normalized_goal_names[normalized_goal_names == goal_normalized].index[0]
            goal_plan_indices.append(goal_index)

    similar_goals = cosine_similarities[goal_plan_indices].mean(axis=0)
    similar_goal_indices = similar_goals.argsort()[-top_n*2:][::-1]  # Fetch more to ensure unique recommendations
    recommended_goals = goal_data.iloc[similar_goal_indices]["goal_name"].unique()

    print(f"Recommended goals before filtering: {recommended_goals}")

    # Filter out goals that the employee has already completed
    recommended_goals = [goal for goal in recommended_goals if goal not in completed_goals and goal in goal_plan_goals]

    print(f"Recommended goals after filtering: {recommended_goals}")

    # Adding subgoals based on department
    additional_goals = recommend_additional_goals(department)
    recommended_goals = list(recommended_goals) + additional_goals

    return recommended_goals[:top_n]

# Function to recommend additional subgoals based on department
def recommend_additional_goals(department):
    department_subgoals = {
        "Sales": ["Increase Social Media Engagement", "Improve Customer Feedback"],
        "Marketing": ["Optimize SEO Strategies", "Enhance Content Marketing"],
        "IT": ["Enhance Cybersecurity Measures", "Improve Network Infrastructure"],
        "HR": ["Improve Employee Retention", "Enhance Training Programs"]
    }
    return department_subgoals.get(department, [])

# Main function
def main():
    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]

    data = load_data(data_file_path)
    goal_data = process_data(data)
    cosine_similarities = calculate_similarity(goal_data)
    department_to_goal_indices = create_department_goal_indices(goal_data)
    
    user_choice = input("Do you want to use Employee Number or Department? (Enter 'number' or 'department'): ").strip().lower()
    
    if user_choice == "number":
        employee_number = input("Enter Employee Number: ").strip()
        goal_plan_name = input("Enter Goal Plan Name: ").strip()
        recommended_goals = recommend_goals_based_on_plan(employee_number, goal_plan_name, data, goal_data, cosine_similarities, department_to_goal_indices, db)
    elif user_choice == "department":
        department = input("Enter Department: ").strip()
        goal_plan_name = input("Enter Goal Plan Name: ").strip()
        recommended_goals = recommend_goals_based_on_plan(department, goal_plan_name, data, goal_data, cosine_similarities, department_to_goal_indices, db)
    else:
        print("Invalid choice. Please enter 'number' or 'department'.")
        return
    
    print(f"Recommended Goals: {recommended_goals}")

if __name__ == "__main__":
    main()
