
# terminal anser generated code
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from pymongo import MongoClient

# MongoDB connection details
MONGO_URI = "mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns"
DATABASE_NAME = "PCL_Interns"
COLLECTION_NAME = "Employee_rating"

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Fetch data from MongoDB
data = list(collection.find())

# Transform the data into a pandas DataFrame
employee_data = []
performance_data = []
career_data = []

for record in data:
    employee_data.append({
        'Employee ID': record['Employee ID'],
        'Name': record['Name'],
        'Department': record['Department'],
        'Role/Job Title': record['Role/Job Title'],
        'Manager/Supervisor': record['Manager/Supervisor']
    })
    
    performance_data.append({
        'Employee ID': record['Employee ID'],
        'Self-Assessment': record['Performance Data']['Self-Assessment'],
        'Peer Reviews': record['Performance Data']['Peer Reviews'],
        'Manager Evaluations': record['Performance Data']['Manager Evaluations'],
        'Customer Feedback': record['Performance Data']['Customer Feedback'],
        '360-Degree Feedback': record['Performance Data']['360-Degree Feedback']
    })
    
    career_data.append({
        'Employee ID': record['Employee ID'],
        'Previous Performance Ratings': record['Career Data']['Previous Performance Ratings'],
        'Career Progression': record['Career Data']['Career Progression'],
        'Training and Development': record['Career Data']['Training and Development']
    })

employee_df = pd.DataFrame(employee_data)
performance_df = pd.DataFrame(performance_data)
career_df = pd.DataFrame(career_data)

# Combine all data into a single DataFrame
combined_df = employee_df.merge(performance_df, on='Employee ID').merge(career_df, on='Employee ID')

# Normalize the performance data
scaler = MinMaxScaler()
performance_columns = ['Self-Assessment', 'Peer Reviews', 'Manager Evaluations', 'Customer Feedback', '360-Degree Feedback', 'Previous Performance Ratings']
combined_df[performance_columns] = scaler.fit_transform(combined_df[performance_columns])

# Clustering based on historical performance data
historical_columns = ['Previous Performance Ratings', 'Career Progression', 'Training and Development']
kmeans = KMeans(n_clusters=3, random_state=42)
combined_df['Cluster'] = kmeans.fit_predict(combined_df[historical_columns])

# Define a function to automatically calibrate performance ratings
def calibrate_performance(row):
    # Weightings for each component (these can be adjusted)
    weights = {
        'Self-Assessment': 0.10,
        'Peer Reviews': 0.15,
        'Manager Evaluations': 0.15,
        'Customer Feedback': 0.10,
        '360-Degree Feedback': 0.20,
        'Previous Performance Ratings': 0.30
    }
    
    # Calculate the weighted average rating
    performance_score = (
        row['Self-Assessment'] * weights['Self-Assessment'] +
        row['Peer Reviews'] * weights['Peer Reviews'] +
        row['Manager Evaluations'] * weights['Manager Evaluations'] +
        row['Customer Feedback'] * weights['Customer Feedback'] +
        row['360-Degree Feedback'] * weights['360-Degree Feedback'] +
        row['Previous Performance Ratings'] * weights['Previous Performance Ratings']
    )
    
    return round(performance_score, 2)

# Apply the calibration function to the combined DataFrame
combined_df['Calibrated Performance Rating'] = combined_df.apply(calibrate_performance, axis=1)

# Function to assign descriptive performance ratings
def performance_description(rating):
    if rating >= 4:
        return 'Exceeds Expectations'
    elif rating >= 3:
        return 'Meets Expectations'
    elif rating >= 2:
        return 'Below Expectations'
    else:
        return 'Needs Improvement'

combined_df['Performance Description'] = combined_df['Calibrated Performance Rating'].apply(performance_description)

# Display the final calibrated performance ratings with additional columns
print(combined_df[['Employee ID', 'Name', 'Department', 'Cluster', 'Calibrated Performance Rating', 'Performance Description']])














# # csv anser generated code
# import pandas as pd
# import numpy as np
# from sklearn.preprocessing import MinMaxScaler
# from sklearn.cluster import KMeans
# from pymongo import MongoClient

# # MongoDB connection details
# MONGO_URI = "mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns"
# DATABASE_NAME = "PCL_Interns"
# COLLECTION_NAME = "Employee_rating"

# # Connect to MongoDB
# client = MongoClient(MONGO_URI)
# db = client[DATABASE_NAME]
# collection = db[COLLECTION_NAME]

# # Fetch data from MongoDB
# data = list(collection.find())

# # Transform the data into a pandas DataFrame
# employee_data = []
# performance_data = []
# career_data = []

# for record in data:
#     employee_data.append({
#         'Employee ID': record['Employee ID'],
#         'Name': record['Name'],
#         'Department': record['Department'],
#         'Role/Job Title': record['Role/Job Title'],
#         'Manager/Supervisor': record['Manager/Supervisor']
#     })
    
#     performance_data.append({
#         'Employee ID': record['Employee ID'],
#         'Self-Assessment': record['Performance Data']['Self-Assessment'],
#         'Peer Reviews': record['Performance Data']['Peer Reviews'],
#         'Manager Evaluations': record['Performance Data']['Manager Evaluations'],
#         'Customer Feedback': record['Performance Data']['Customer Feedback'],
#         '360-Degree Feedback': record['Performance Data']['360-Degree Feedback']
#     })
    
#     career_data.append({
#         'Employee ID': record['Employee ID'],
#         'Previous Performance Ratings': record['Career Data']['Previous Performance Ratings'],
#         'Career Progression': record['Career Data']['Career Progression'],
#         'Training and Development': record['Career Data']['Training and Development']
#     })

# employee_df = pd.DataFrame(employee_data)
# performance_df = pd.DataFrame(performance_data)
# career_df = pd.DataFrame(career_data)

# # Combine all data into a single DataFrame
# combined_df = employee_df.merge(performance_df, on='Employee ID').merge(career_df, on='Employee ID')

# # Normalize the performance data
# scaler = MinMaxScaler()
# performance_columns = ['Self-Assessment', 'Peer Reviews', 'Manager Evaluations', 'Customer Feedback', '360-Degree Feedback', 'Previous Performance Ratings']
# combined_df[performance_columns] = scaler.fit_transform(combined_df[performance_columns])

# # Clustering based on historical performance data
# historical_columns = ['Previous Performance Ratings', 'Career Progression', 'Training and Development']
# kmeans = KMeans(n_clusters=3, random_state=42)
# combined_df['Cluster'] = kmeans.fit_predict(combined_df[historical_columns])

# # Define a function to automatically calibrate performance ratings
# def calibrate_performance(row):
#     # Weightings for each component (these can be adjusted)
#     weights = {
#         'Self-Assessment': 0.10,
#         'Peer Reviews': 0.15,
#         'Manager Evaluations': 0.15,
#         'Customer Feedback': 0.10,
#         '360-Degree Feedback': 0.20,
#         'Previous Performance Ratings': 0.30
#     }
    
#     # Calculate the weighted average rating
#     performance_score = (
#         row['Self-Assessment'] * weights['Self-Assessment'] +
#         row['Peer Reviews'] * weights['Peer Reviews'] +
#         row['Manager Evaluations'] * weights['Manager Evaluations'] +
#         row['Customer Feedback'] * weights['Customer Feedback'] +
#         row['360-Degree Feedback'] * weights['360-Degree Feedback'] +
#         row['Previous Performance Ratings'] * weights['Previous Performance Ratings']
#     )
    
#     return round(performance_score, 2)

# # Apply the calibration function to the combined DataFrame
# combined_df['Calibrated Performance Rating'] = combined_df.apply(calibrate_performance, axis=1)

# # Function to assign descriptive performance ratings
# def performance_description(rating):
#     if rating >= 4:
#         return 'Exceeds Expectations'
#     elif rating >= 3:
#         return 'Meets Expectations'
#     elif rating >= 2:
#         return 'Below Expectations'
#     else:
#         return 'Needs Improvement'

# combined_df['Performance Description'] = combined_df['Calibrated Performance Rating'].apply(performance_description)

# # Write the final calibrated performance ratings to a file
# output_df = combined_df[['Employee ID', 'Name', 'Department', 'Cluster', 'Calibrated Performance Rating', 'Performance Description']]
# output_df.to_csv('calibrated_performance_ratings.csv', index=False)

# # Display a message indicating where the output has been saved
# print("Output has been written to calibrated_performance_ratings.csv")
