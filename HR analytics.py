from flask import Flask, jsonify
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# MongoDB configuration
MONGO_URI = "mongodb://dev1_user:dev1_pass@172.191.245.199:27017/dev1"
DB_NAME = "dev1"
COLLECTION_NAME = "oras_employee_data"

def fetch_all_data_from_oras_employee_data():
    try:
        # Create a MongoClient to the running MongoDB instance
        client = MongoClient(MONGO_URI)
        
        # Access the specified database
        db = client[DB_NAME]
        
        # Access the oras_employee_data collection
        collection = db[COLLECTION_NAME]
        
        # Fetch all documents in the collection
        documents = collection.find()
        
        # Convert documents to a list and serialize ObjectId to string
        documents_list = []
        for document in documents:
            document['_id'] = str(document['_id'])
            documents_list.append(document)
        
        # Close the connection
        client.close()
        
        return documents_list
    except Exception as e:
        raise Exception(f"Error accessing the collection: {str(e)}")

@app.route('/fetch-oras-employee-data', methods=['POST'])
def fetch_oras_employee_data():
    try:
        # Fetch data from MongoDB
        documents = fetch_all_data_from_oras_employee_data()
        
        # Return the fetched documents as JSON
        return jsonify(documents), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
