import os
import pandas as pd
from pymongo import MongoClient

# Read the Excel file
excel_file_path = 'C:/Users/Oracle/Downloads/managers_collection_.xlsx'
df = pd.read_excel(excel_file_path)

# Convert DataFrame to dictionary
data_dict = df.to_dict("records")

# Establish a connection to MongoDB
#client = 'mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns'  # Replace with your MongoDB connection string
connection_string = 'mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns'
client = MongoClient(connection_string)  # Replace 'your_password' with the actual password

# Select the database and collection
db = client['PCL_Interns']
collection = db['managers']

# Insert data into the collection
collection.insert_many(data_dict)

print("Data inserted successfully!")

