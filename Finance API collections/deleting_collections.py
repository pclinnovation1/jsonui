import json
import pymongo
from pymongo import MongoClient

# Open and read the JSON file
with open('FinancialAPI.postman_collection.json', 'r') as file:
  data = json.load(file)

data = data["item"]
print("Number of APIs:", len(data))

for i in range(0,110):
  print(i+1)
  item = data[i]
  name = item["name"]
  print(name)
  
  try:
    client = MongoClient("mongodb://dev1_user:dev1_pass@172.191.245.199:27017/dev1")

    db = client["dev1"]

    # Desired collection name
    collection_name = f"FI_{name}"

    collection = db[collection_name]

    # Delete the collection
    if collection_name in db.list_collection_names():
      db[collection_name].drop()
      print(f"Collection '{collection_name}' has been deleted.")
    else:
      print(f"Collection '{collection_name}' does not exist, nothing to delete.")
  except pymongo.errors.ConnectionError as e:
    print(f"Error connecting to MongoDB: {e}")