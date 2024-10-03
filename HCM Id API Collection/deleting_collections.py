import pymongo
import json
import pymongo

# Path to the JSON file (ensure the correct path)
file_path = 'RestAPI.postman_collection.json'

# Open and load the JSON file
with open(file_path, 'r') as json_file:
  data_fetched = json.load(json_file)

data_fetched = data_fetched["item"]

print("Number of APIs:", len(data_fetched))

# Going through all the endpoints
# for i in range(0,len(data_fetched)):
  # print("API index:", i)
  # item = data_fetched[i]

  # name = item["name"]

  # mongo_uri = "mongodb://dev1_user:dev1_pass@172.191.245.199:27017/dev1"

  # # Checking to MongoDB dev1 database
  # try:
  #   client = pymongo.MongoClient(mongo_uri)
  #   db = client['dev1']
  #   collection_name = f"HCM_Id_{name}"
  #   collection = db[collection_name]

  #   if collection_name in db.list_collection_names():
  #     # Collection exists, delete the collection
  #     db[collection_name].drop()
  #     print(f"Collection '{collection_name}' has been deleted successfully")
  #   else:
  #     print(f"Collection '{collection_name}' does not exist or is already deleted")

  # except Exception:
  #   print("*************************Error*************************")
  # finally:
  #   # Ensure the client is closed even if there was an error
  #   try:
  #     client.close()
  #     print("MongoDB connection closed")
  #   except:
  #     pass


# For individual collection
i = 50
print("API index:", i)
item = data_fetched[i]

name = item["name"]

mongo_uri = "mongodb://dev1_user:dev1_pass@172.191.245.199:27017/dev1"

# Checking to MongoDB dev1 database
try:
  client = pymongo.MongoClient(mongo_uri)
  db = client['dev1']
  collection_name = f"HCM_Id_{name}"
  collection = db[collection_name]

  if collection_name in db.list_collection_names():
    # Collection exists, delete the collection
    db[collection_name].drop()
    print(f"Collection '{collection_name}' has been deleted successfully")
  else:
    print(f"Collection '{collection_name}' does not exist or is already deleted")

except Exception:
  print("*************************Error*************************")
finally:
  # Ensure the client is closed even if there was an error
  try:
    client.close()
    print("MongoDB connection closed")
  except:
    pass