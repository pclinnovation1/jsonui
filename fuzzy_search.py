# from flask import Flask, request, jsonify
# from pymongo import MongoClient
# from fuzzywuzzy import fuzz
# from bson import ObjectId
# import json

# app = Flask(__name__)

# # MongoDB setup
# client = MongoClient('mongodb://localhost:27017/')
# db = client['company2']

# # Custom JSON encoder for ObjectId
# class JSONEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, ObjectId):
#             return str(obj)
#         return json.JSONEncoder.default(self, obj)

# app.json_encoder = JSONEncoder

# def convert_objectid(data):
#     if isinstance(data, list):
#         return [convert_objectid(item) for item in data]
#     elif isinstance(data, dict):
#         return {key: convert_objectid(value) for key, value in data.items()}
#     elif isinstance(data, ObjectId):
#         return str(data)
#     else:
#         return data

# @app.route('/search_classroom', methods=['POST'])
# def search_classroom():
#     data = request.get_json()
#     classroom_name = data.get("classroom_name")

#     if not classroom_name:
#         return jsonify({"error": "Invalid input data"}), 400

#     # Trim the input classroom name
#     classroom_name = classroom_name.strip()

#     # Fetch all classrooms from the collection
#     classrooms = list(db['classrooms'].find({}, {"classroom_name": 1}))

#     # Use fuzzy matching to find all potential matches
#     matches = []
#     for classroom in classrooms:
#         score = fuzz.ratio(classroom_name.lower(), classroom["classroom_name"].strip().lower())
#         if score >= 80:  # Define a threshold for the fuzzy match
#             matches.append({"classroom": convert_objectid(classroom), "score": score})

    # if len(matches) == 1:
    #     return jsonify({"message": "Classroom found", "classroom": matches[0]["classroom"], "score": matches[0]["score"]}), 200
    # elif len(matches) > 1:
    #     return jsonify({"message": "Multiple classrooms found", "matches": matches}), 200
    # else:
    #     return jsonify({"error": "No matching classroom found"}), 404

# if __name__ == '__main__':
#     app.run(debug=True)


# from flask import Flask, request, jsonify
# from fuzzywuzzy import fuzz
# from pymongo import MongoClient
# from bson import ObjectId
# import json

# app = Flask(__name__)

# # MongoDB setup
# client = MongoClient('mongodb://localhost:27017/')
# db = client['company2']

# # Custom JSON encoder for ObjectId
# class JSONEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, ObjectId):
#             return str(obj)
#         return json.JSONEncoder.default(self, obj)

# app.json_encoder = JSONEncoder

# def convert_objectid(data):
#     if isinstance(data, list):
#         return [convert_objectid(item) for item in data]
#     elif isinstance(data, dict):
#         return {key: convert_objectid(value) for key, value in data.items()}
#     elif isinstance(data, ObjectId):
#         return str(data)
#     else:
#         return data

# def find_similar_classrooms(classroom_name):
#     # Fetch all classrooms from the collection
#     classrooms = list(db['classrooms'].find({}, {"classroom_name": 1}))

#     # Use fuzzy matching to find all potential matches
#     matches = []
#     for classroom in classrooms:
#         score = fuzz.ratio(classroom_name.lower(), classroom["classroom_name"].strip().lower())
#         if score >= 30:  # Adjust threshold as needed
#             matches.append({"classroom": convert_objectid(classroom), "score": score})

#     # Sort matches by score in descending order
#     matches.sort(key=lambda x: x["score"], reverse=True)

#     # Check if there are multiple scores of 100
#     highest_score = matches[0]["score"] if matches else 0
#     highest_matches = [match for match in matches if match["score"] == highest_score]

#     if highest_score == 100 and len(highest_matches) > 1:
#         # Return only the highest score of 100
#         return [highest_matches[0]]
#     else:
#         # Return all matches above the threshold
#         return matches

# @app.route('/search_classroom', methods=['POST'])
# def search_classroom():
#     data = request.get_json()
#     classroom_name = data.get("classroom_name")

#     if not classroom_name:
#         return jsonify({"error": "Invalid input data"}), 400

#     # Trim the input classroom name
#     classroom_name = classroom_name.strip()

#     # Find similar classrooms
#     matches = find_similar_classrooms(classroom_name)

#     if matches:
#         best_match = matches[0]
#         if best_match["score"] == 100:
#             return jsonify({"message": "Classroom found", "classroom": best_match["classroom"], "score": best_match["score"]}), 200
#         elif len(matches) == 1:
#             return jsonify({"message": "Classroom found", "classroom": matches[0]["classroom"], "score": matches[0]["score"]}), 200
#         else:
#             return jsonify({"message": "Multiple classrooms found", "matches": matches}), 200
#     else:
#         return jsonify({"error": "No matching classrooms found"}), 404

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, request, jsonify
from fuzzywuzzy import fuzz
from pymongo import MongoClient
from bson import ObjectId
import json

app = Flask(__name__)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['company2']

# Custom JSON encoder for ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

app.json_encoder = JSONEncoder

def convert_objectid(data):
    if isinstance(data, list):
        return [convert_objectid(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_objectid(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

def find_similar_classrooms(classroom_name):
    # Fetch all classrooms from the collection
    classrooms = list(db['classrooms'].find({}, {"classroom_name": 1}))

    # Use fuzzy matching to find all potential matches
    matches = []
    for classroom in classrooms:
        score = fuzz.token_sort_ratio(classroom_name.lower(), classroom["classroom_name"].strip().lower())
        if score >= 40:  # Adjust threshold as needed
            matches.append({"classroom": convert_objectid(classroom), "score": score})

    # Sort matches by score in descending order
    matches.sort(key=lambda x: x["score"], reverse=True)

    # Filter out matches where there are significant unmatched parts
    filtered_matches = []
    for match in matches:
        unmatched_ratio = 100 - match["score"]
        if unmatched_ratio <= 60:  # Adjust the threshold for unmatched parts as needed
            filtered_matches.append(match)

    # Check if there are multiple scores of 100
    highest_score = filtered_matches[0]["score"] if filtered_matches else 0
    highest_matches = [match for match in filtered_matches if match["score"] == highest_score]

    if highest_score == 100 and len(highest_matches) > 1:
        # Return only the highest score of 100
        return [highest_matches[0]]
    else:
        # Return all matches above the threshold
        return filtered_matches

@app.route('/search_classroom', methods=['POST'])
def search_classroom():
    data = request.get_json()
    classroom_name = data.get("classroom_name")

    if not classroom_name:
        return jsonify({"error": "Invalid input data"}), 400

    # Trim the input classroom name
    classroom_name = classroom_name.strip()

    # Find similar classrooms
    matches = find_similar_classrooms(classroom_name)

    if matches:
        best_match = matches[0]
        if best_match["score"] == 100:
            return jsonify({"message": "Classroom found", "classroom": best_match["classroom"], "score": best_match["score"]}), 200
        elif len(matches) == 1:
            return jsonify({"message": "Classroom found", "classroom": matches[0]["classroom"], "score": matches[0]["score"]}), 200
        else:
            return jsonify({"message": "Multiple classrooms found", "matches": matches}), 200
    else:
        return jsonify({"error": "No matching classrooms found"}), 404

if __name__ == '__main__':
    app.run(debug=True)