import json
import requests
from requests.auth import HTTPBasicAuth
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
  # print(name)
  username = item["request"]["auth"]["basic"]["username"]
  password = item["request"]["auth"]["basic"]["password"]
  # print(username, password)

  url = item["request"]["url"]
  # print(type(url))

  # In the JSON file, we have all the "url" entries as dictionary except one
  if isinstance(url, dict):
    # print("Dictionary")
    url = url["raw"]

  # Eliminating the parameters to simply obtain the API endpoint
  url = url.split("?")[0]
  # print(url)

  # Specifying parameters
  params = {
    'expand': 'all',
    'limit': 500,
    'onlyData': 'true',
    'offset': 5000
  }

  # Catching the response
  response = requests.get(url, auth=HTTPBasicAuth(username, password), params=params)
  if response.status_code == 200:
    try:
      # Parse the response content as JSON
      res = response.json()
      # print(len(res["items"]))
      res = res["items"]
      # print(type(res))
    except ValueError:
      print("Error: The response is not in JSON format")
  else:
    print(f"Error: Received response with status code {response.status_code}")
  
  # Creating the collection
  try:
    # Create a connection to the MongoDB server (default localhost:27017)
    client = MongoClient("mongodb://dev1_user:dev1_pass@172.191.245.199:27017/dev1")

    db = client["dev1"]

    # Desired collection name
    collection_name = f"FI_{name}"

    # Check if the collection already exists
    # if collection_name in db.list_collection_names():
    #   print(f"Collection '{collection_name}' already exists.")
    # else:
    #   print(f"Collection '{collection_name}' does not exist, creating the collection.")
    
    # Access or create the collection
    collection = db[collection_name]

    # Step 3: Insert data into the MongoDB collection
    if isinstance(res, list):
      # Insert many documents if the data is a list
      if len(res)>0:
        result = collection.insert_many(res)
        print(f"Inserted {len(result.inserted_ids)} documents into {collection_name}.")
    else:
      # Insert a single document if the data is not a list
      result = collection.insert_one(res)
      print(f"Inserted document with id {result.inserted_id}.")
    
  except pymongo.errors.ConnectionError as e:
    print(f"Error connecting to MongoDB: {e}")