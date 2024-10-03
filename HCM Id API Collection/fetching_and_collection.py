import json
import requests
from requests.auth import HTTPBasicAuth
import pymongo

# Path to the JSON file (ensure the correct path)
file_path = 'RestAPI.postman_collection.json'

# Open and load the JSON file
with open(file_path, 'r') as json_file:
  data_fetched = json.load(json_file)

data_fetched = data_fetched["item"]

print("Number of APIs:", len(data_fetched))

# Specifying parameters
params = {
  "limit": 500,
  "offset": 6000,
  "onlyData": "true",
  "expand": "all"
}

# Going through all the endpoints
# for i in range(0,len(data_fetched)):
  # if i==45:
  #   continue
  # print("API index:", i)
  # item = data_fetched[i]

  # name = item["name"]

  # # Fetching and filtering the URL
  # url = item["request"]["url"]

  # if isinstance(url,dict):
  #   url = url["raw"]
  
  # url = url.split("?")[0]

  # # Specifying authorization
  # auth = item["request"]["auth"]["basic"]

  # # Send the GET request with basic auth and parameters and getting the JSON response
  # response = requests.get(url, params=params, auth=HTTPBasicAuth(auth["username"], auth["password"]))
  # if response.status_code == 200:
  #   # Parse the JSON response
  #   result = response.json()
  #   result = result["items"]
  #   print("Response Data Obtained")

  #   print("Length of data to be exported:", len(result))

  #   if(len(result)>0):

  #     mongo_uri = "mongodb://dev1_user:dev1_pass@172.191.245.199:27017/dev1"

  #     # Sending the data to MongoDB dev1 database
  #     try:
  #       client = pymongo.MongoClient(mongo_uri)
  #       db = client['dev1']
  #       collection_name = f"HCM_Id_{name}"
  #       collection = db[collection_name]

  #       # Data exporting and error handling
  #       try:
  #         exported_data = collection.insert_many(result)
  #         print(f"{len(result)} entries of data inserted into {collection_name}")
  #       except Exception:
  #         print("*************************Error*************************")
        
  #     # Error Handling
  #     except Exception:
  #       print("*************************Error*************************")

  #     finally:
  #       # Ensure the client is closed even if there was an error
  #       try:
  #         client.close()
  #         print("MongoDB connection closed")
  #       except:
  #         pass
  #   else:
  #     print("No entries in data, so no data needs to be exported")

  # else:
  #   print(f"Fetching request failed with status code {response.status_code}")


# Code for Individual endpoint
i = 50
print("API index:", i)
item = data_fetched[i]

name = item["name"]

# Fetching and filtering the URL
url = item["request"]["url"]

if isinstance(url,dict):
  url = url["raw"]

url = url.split("?")[0]

# Specifying authorization
auth = item["request"]["auth"]["basic"]

# Send the GET request with basic auth and parameters and getting the JSON response
response = requests.get(url, params=params, auth=HTTPBasicAuth(auth["username"], auth["password"]))
if response.status_code == 200:
  # Parse the JSON response
  result = response.json()
  result = result["items"]
  print("Response Data Obtained")

  print("Length of data to be exported:", len(result))

  if(len(result)>0):

    mongo_uri = "mongodb://dev1_user:dev1_pass@172.191.245.199:27017/dev1"

    # Sending the data to MongoDB dev1 database
    try:
      client = pymongo.MongoClient(mongo_uri)
      db = client['dev1']
      collection_name = f"HCM_Id_{name}"
      collection = db[collection_name]

      # Data exporting and error handling
      try:
        exported_data = collection.insert_many(result)
        print(f"{len(result)} entries of data inserted into {collection_name}")
      except Exception:
        print("*************************Error*************************")
      
    # Error Handling
    except Exception:
      print("*************************Error*************************")

    finally:
      # Ensure the client is closed even if there was an error
      try:
        client.close()
        print("MongoDB connection closed")
      except:
        pass
  else:
    print("No entries in data, so no data needs to be exported")

else:
  print(f"Fetching request failed with status code {response.status_code}")