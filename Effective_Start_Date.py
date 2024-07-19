# from pymongo import MongoClient
# from datetime import datetime

# client = MongoClient('mongodb://localhost:27017/')
# db = client['company2']
# collection = db['EmployeeDetails_UK']

# # Function to update documents
# def update_documents():
#     for document in collection.find():
#         if 'Effective_End_Date' in document and isinstance(document['Effective_End_Date'], str):
#             date_str = document['Effective_End_Date']
#             # Convert string date to datetime object
#             effective_start_date = datetime.strptime(date_str, '%Y-%m-%d')
#             # Update the document
#             collection.update_one(
#                 {'_id': document['_id']},
#                 {'$set': {'Effective_End_Date': effective_start_date}}
#             )

# if __name__ == '__main__':
#     update_documents()


from pymongo import MongoClient

# MongoDB connection
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client['PCL_Interns']
collection = db['Calendar_Details']

# Sample data
# Sample data in Indian Standard Time (IST)
sample_data = [
    {
        "event_id": "1",
        "subject": "Team Meeting",
        "start_time": "2024-07-01T16:00:00+05:30",
        "end_time": "2024-07-01T17:00:00+05:30"
    },
    {
        "event_id": "2",
        "subject": "Project Kickoff",
        "start_time": "2024-07-01T18:00:00+05:30",
        "end_time": "2024-07-01T19:00:00+05:30"
    },
    {
        "event_id": "3",
        "subject": "Learning Session: AI Basics",
        "start_time": "2024-07-02T19:30:00+05:30",
        "end_time": "2024-07-02T20:30:00+05:30"
    },
    {
        "event_id": "4",
        "subject": "Client Presentation",
        "start_time": "2024-07-03T15:30:00+05:30",
        "end_time": "2024-07-03T16:30:00+05:30"
    },
    {
        "event_id": "5",
        "subject": "Workshop: Data Science",
        "start_time": "2024-07-04T18:00:00+05:30",
        "end_time": "2024-07-04T21:00:00+05:30"
    }
]
# Insert sample data into MongoDB
collection.insert_many(sample_data)

print("Sample data inserted successfully.")
