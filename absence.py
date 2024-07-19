# from pymongo import MongoClient, errors

# try:
#     # Connect to MongoDB
#     client = MongoClient("mongodb://localhost:27017/")
#     print("Connected to MongoDB successfully!")

#     # Access the database (create it if it doesn't exist)
#     db = client.company

#     # Access the collection (create it if it doesn't exist)
#     absence_collection = db.absence

#     # Sample absence document
#     absence_document = {
#         "Employee_ID": "12345",
#         "Employee_Name": "John Doe",
#         "Leave_Type": "Annual Vacation",
#         "Start_Date": "2024-12-01",
#         "End_Date": "2024-12-10",
#         "Duration": 10,
#         "Reason_for_Absence": "Vacation",
#         "Status": "Pending",
#         "Manager_ID": "67890",
#         "Manager_Name": "Jane Smith"
#     }

#     # Insert the document into the collection
#     result = absence_collection.insert_one(absence_document)
#     print(f"Inserted document ID: {result.inserted_id}")

#     # Fetch and display the documents to verify insertion
#     for absence in absence_collection.find():
#         print(absence)

# except errors.ConnectionFailure as e:
#     print(f"Could not connect to MongoDB: {e}")

# except errors.PyMongoError as e:
#     print(f"An error occurred with PyMongo: {e}")

# except Exception as e:
#     print(f"An unexpected error occurred: {e}")


from pymongo import MongoClient

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['company2']

# Sample data
classrooms = [
    { "classroom_name": "Demo Classroom 1" },
    { "classroom_name": "Demo Classroom 2" },
    { "classroom_name": "Sample Classroom" },
    { "classroom_name": "Test Classroom" },
    { "classroom_name": "Training Room" },
    {"classroom_name": "Python"},
    {"classroom_name": "Python Lab"},
    {"classroom_name": "Java Lab"}
]

# Insert data into the 'classrooms' collection
db.classrooms.insert_many(classrooms)

print("Data inserted successfully")
