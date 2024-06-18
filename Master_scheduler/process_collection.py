import json
from pymongo import MongoClient

data=[{
  "processes": [
    {
      "Process ID": "12346",
      "Name": "Payroll Calculation",
      "Metadata Name": "PayrollProcess",
      "Status": "Running",
      "Submitted By": "payroll_user",
      "Submission Notes": "Monthly payroll calculation",
      "Start Time": "2024-06-18T23:00:00Z",
      "Scheduled Time": "2024-06-18T23:00:00Z",
      "Submission Time": "2024-06-18T10:00:00Z",
      "Completion Time": "",
      "All Parameters": {
        "Argument1": "",
        "Argument2": "",
        "Argument3": "",
        "Argument4": "",
        "Argument5": "",
        "Argument6": "",
        "Argument7": "",
        "Argument8": "",
        "Argument9": "",
        "Argument10": "",
        "Argument11": "",
        "Argument12": "",
        "Argument13": "",
        "Argument14": "",
        "Argument15": "",
        "Argument16": "",
        "Argument17": "",
        "Argument18": "",
        "Argument19": "",
        "Argument20": ""
      }
    }
  ]
}]

client = MongoClient("mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns")  # Change the connection string as needed
db = client["PCL_Interns"]  # Replace with your database name
collection = db["Process_Details"]  # Replace with your collection name

# Insert the data into the collection
collection.insert_many(data)

print("Data inserted successfully.")
