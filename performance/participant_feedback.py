from flask import Flask, request, jsonify
from pymongo import MongoClient
import datetime

app = Flask(__name__)

# MongoDB configuration
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client.PCL_Interns
template_collection = db.P_FeedbackTemplates
request_collection = db.P_ParticipantFeedback

@app.route('/send_feedback_request', methods=['POST'])
def send_feedback_request():
    data = request.get_json()
    
    template_name = data.get('template_name')
    template = template_collection.find_one({"name": template_name})
    
    if not template:
        return jsonify({"message": "Template not found"}), 404
    
    questions = template['questionnaire']
    receivers = {}
    for receiver in data['receiver_names']:
        receivers[receiver] = {
            "status": "pending",
            "responses": {q: "N/A" for q in questions}
        }
    
    feedback_request = {
        "request_name": data.get('request_name'),
        "template_name": template_name,
        "sender_name": data.get('sender_name'),
        "status": "pending",
        "sent_at": datetime.datetime.utcnow(),
        "updated_at": datetime.datetime.utcnow(),
        "completed_at": None,
        "questions": questions,
        "receiver_names": receivers
    }
    
    result = request_collection.insert_one(feedback_request)
    return jsonify({"message": "Feedback request sent", "id": str(result.inserted_id)}), 201

@app.route('/update_feedback_request', methods=['POST'])
def update_feedback_request():
    data = request.get_json()
    request_name = data.get('request_name')
    receiver_name = data.get('receiver_name')
    question_name = data.get('question_name')
    response = data.get('response')
    
    # Find the feedback request
    feedback_request = request_collection.find_one({"request_name": request_name})
    
    if not feedback_request:
        return jsonify({"message": "Feedback request not found"}), 404
    
    # Ensure the responses key exists
    if "responses" not in feedback_request["receiver_names"][receiver_name]:
        return jsonify({"message": f"Responses not found for receiver '{receiver_name}'"}), 404
    
    # Update the specific question's response for the receiver
    result = request_collection.update_one(
        {"request_name": request_name, f"receiver_names.{receiver_name}.responses.{question_name}": "N/A"},
        {"$set": {
            f"receiver_names.{receiver_name}.responses.{question_name}": response,
            "updated_at": datetime.datetime.utcnow()
        }}
    )
    
    if result.modified_count > 0:
        # Reload the feedback request to get the updated data
        feedback_request = request_collection.find_one({"request_name": request_name})

        # Check if all questions are answered for the receiver
        all_answered = all(
            answer != "N/A"
            for answer in feedback_request["receiver_names"][receiver_name]["responses"].values()
        )
        receiver_status = "completed" if all_answered else "in progress"
        
        request_collection.update_one(
            {"request_name": request_name},
            {"$set": {
                f"receiver_names.{receiver_name}.status": receiver_status,
                "updated_at": datetime.datetime.utcnow()
            }}
        )
        
        # Reload the feedback request to get the updated data
        feedback_request = request_collection.find_one({"request_name": request_name})

        # Check the overall status
        receiver_statuses = [feedback_request["receiver_names"][name]["status"] for name in feedback_request["receiver_names"]]
        if all(status == "completed" for status in receiver_statuses):
            overall_status = "completed"
        elif any(status in ["in progress", "completed"] for status in receiver_statuses):
            overall_status = "in progress"
        else:
            overall_status = "pending"
        
        request_collection.update_one(
            {"request_name": request_name},
            {"$set": {
                "status": overall_status,
                "updated_at": datetime.datetime.utcnow()
            }}
        )
        
        return jsonify({"message": "Response updated successfully"}), 200
    else:
        return jsonify({"message": f"Question '{question_name}' not found for receiver '{receiver_name}'"}), 404

if __name__ == '__main__':
    app.run(debug=True)
