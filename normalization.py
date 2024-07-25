# import pymongo
# import numpy as np
# import pandas as pd
# from pymongo import MongoClient

# # MongoDB connection details
# MONGO_URI = "mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns"
# DATABASE_NAME = "PCL_Interns"
# COLLECTION_NAME = "performance_review"

# # Connect to MongoDB
# client = MongoClient(MONGO_URI)
# db = client[DATABASE_NAME]
# collection = db[COLLECTION_NAME]

# # Fetch data from MongoDB
# documents = list(collection.find())

# def normalize_and_rescale(ratings):
#     if not ratings:
#         return []
    
#     mean = np.mean(ratings)
#     std = np.std(ratings)
    
#     if std == 0:
#         # If standard deviation is zero, all ratings are the same
#         normalized_ratings = [0 for _ in ratings]
#     else:
#         normalized_ratings = [(x - mean) / std for x in ratings]
    
#     min_norm = min(normalized_ratings)
#     max_norm = max(normalized_ratings)
#     scaled_ratings = [5 * (x - min_norm) / (max_norm - min_norm) if max_norm != min_norm else 2.5 for x in normalized_ratings]  # Avoid division by zero
    
#     return scaled_ratings

# # Collect all ratings
# all_goal_ratings = []
# all_competency_ratings = []

# for doc in documents:
#     goal_ratings = [goal["manager_goal_rating"] for goal in doc.get("manager_assessment", {}).get("goals_evaluation", [])]
#     all_goal_ratings.extend(goal_ratings)
    
#     competency_ratings = [comp["manager_competency_rating"] for comp in doc.get("manager_assessment", {}).get("competencies_evaluation", [])]
#     all_competency_ratings.extend(competency_ratings)

# # Normalize and rescale all ratings together
# normalized_goal_ratings = normalize_and_rescale(all_goal_ratings)
# normalized_competency_ratings = normalize_and_rescale(all_competency_ratings)

# # Create a mapping from original ratings to normalized ratings
# goal_rating_mapping = {orig: norm for orig, norm in zip(all_goal_ratings, normalized_goal_ratings)}
# competency_rating_mapping = {orig: norm for orig, norm in zip(all_competency_ratings, normalized_competency_ratings)}

# # Collect data for the table
# data = []

# for doc in documents:
#     manager_name = doc.get("manager_name", "Unknown Manager")
#     for goal in doc.get("manager_assessment", {}).get("goals_evaluation", []):
#         original_rating = goal["manager_goal_rating"]
#         normalized_rating = goal_rating_mapping[original_rating]
#         goal["manager_goal_rating_normalize"] = normalized_rating
#         data.append({"Manager": manager_name, "Rating Type": "Goal", "Original Rating": original_rating, "Normalized Rating": normalized_rating})
        
#     for comp in doc.get("manager_assessment", {}).get("competencies_evaluation", []):
#         original_rating = comp["manager_competency_rating"]
#         normalized_rating = competency_rating_mapping[original_rating]
#         comp["manager_competency_rating_normalize"] = normalized_rating
#         data.append({"Manager": manager_name, "Rating Type": "Competency", "Original Rating": original_rating, "Normalized Rating": normalized_rating})

#     # Update the document in MongoDB
#     collection.update_one({"_id": doc["_id"]}, {"$set": doc})

# # Create DataFrame and display
# df = pd.DataFrame(data)
# print(df)

# print("Normalization and rescaling completed for all employees together.")









import pymongo
import numpy as np
import pandas as pd
from pymongo import MongoClient

# MongoDB connection details
MONGO_URI = "mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns"
DATABASE_NAME = "PCL_Interns"
COLLECTION_NAME = "performance_review"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Fetch data from MongoDB
documents = list(collection.find())

def normalize_and_rescale(ratings):
    if not ratings:
        return []
    
    mean = np.mean(ratings)
    std = np.std(ratings)
    
    if std == 0:
        # If standard deviation is zero, all ratings are the same
        normalized_ratings = [0 for _ in ratings]
    else:
        normalized_ratings = [(x - mean) / std for x in ratings]
    
    min_norm = min(normalized_ratings)
    max_norm = max(normalized_ratings)
    scaled_ratings = [5 * (x - min_norm) / (max_norm - min_norm) if max_norm != min_norm else 2.5 for x in normalized_ratings]  # Avoid division by zero
    
    return scaled_ratings

# Group ratings by manager
manager_goal_ratings = {}
manager_competency_ratings = {}

for doc in documents:
    manager_name = doc.get("manager_name", "Unknown Manager")
    if manager_name not in manager_goal_ratings:
        manager_goal_ratings[manager_name] = []
        manager_competency_ratings[manager_name] = []
    
    goal_ratings = [goal["manager_goal_rating"] for goal in doc.get("manager_assessment", {}).get("goals_evaluation", [])]
    manager_goal_ratings[manager_name].extend(goal_ratings)
    
    competency_ratings = [comp["manager_competency_rating"] for comp in doc.get("manager_assessment", {}).get("competencies_evaluation", [])]
    manager_competency_ratings[manager_name].extend(competency_ratings)

# Normalize and rescale ratings for each manager separately
normalized_goal_ratings = {}
normalized_competency_ratings = {}

for manager, ratings in manager_goal_ratings.items():
    normalized_goal_ratings[manager] = normalize_and_rescale(ratings)

for manager, ratings in manager_competency_ratings.items():
    normalized_competency_ratings[manager] = normalize_and_rescale(ratings)

# Create a mapping from original ratings to normalized ratings for each manager
goal_rating_mapping = {}
competency_rating_mapping = {}

for manager, ratings in manager_goal_ratings.items():
    goal_rating_mapping[manager] = {orig: norm for orig, norm in zip(ratings, normalized_goal_ratings[manager])}

for manager, ratings in manager_competency_ratings.items():
    competency_rating_mapping[manager] = {orig: norm for orig, norm in zip(ratings, normalized_competency_ratings[manager])}

# Collect data for the table
data = []

for doc in documents:
    manager_name = doc.get("manager_name", "Unknown Manager")
    for goal in doc.get("manager_assessment", {}).get("goals_evaluation", []):
        original_rating = goal["manager_goal_rating"]
        normalized_rating = goal_rating_mapping[manager_name][original_rating]
        goal["manager_goal_rating_normalize"] = normalized_rating
        data.append({"Manager": manager_name, "Rating Type": "Goal", "Original Rating": original_rating, "Normalized Rating": normalized_rating})
        
    for comp in doc.get("manager_assessment", {}).get("competencies_evaluation", []):
        original_rating = comp["manager_competency_rating"]
        normalized_rating = competency_rating_mapping[manager_name][original_rating]
        comp["manager_competency_rating_normalize"] = normalized_rating
        data.append({"Manager": manager_name, "Rating Type": "Competency", "Original Rating": original_rating, "Normalized Rating": normalized_rating})

    # Update the document in MongoDB
    collection.update_one({"_id": doc["_id"]}, {"$set": doc})

# Create DataFrame and display
df = pd.DataFrame(data)
print(df)

print("Normalization and rescaling completed for all employees together.")




