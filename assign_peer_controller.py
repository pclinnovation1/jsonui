import uuid
from flask import Blueprint, request, jsonify, url_for
from pymongo import MongoClient
import config
import os
import smtplib
from bson import ObjectId
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import render_template


# Define the Blueprint
assign_peer_bp = Blueprint('assign_peer_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
assigned_performance_collection = db['P_assigned_performance']

# Function to load email template from a file
def load_template(template_name):
    template_path = os.path.join('templates', template_name)
    with open(template_path, 'r') as template_file:
        return template_file.read()

# Function to send email
def send_email(to_address, subject, body):
    smtp_config = config.SMTP_CONFIG
    msg = MIMEMultipart()
    msg['From'] = smtp_config['username']
    msg['To'] = to_address
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
        server.starttls()
        server.login(smtp_config['username'], smtp_config['password'])
        text = msg.as_string()
        server.sendmail(smtp_config['username'], to_address, text)
        server.quit()
        print(f"Email sent to {to_address}")
    except Exception as e:
        print(f"Failed to send email to {to_address}: {e}")

# API route to assign peers to a performance document
@assign_peer_bp.route('/assign_peers', methods=['POST'])
def assign_peers():
    data = request.json
    performance_document_name = data.get('performance_document_name')
    employee_name = data.get('employee_name')
    assigned_peers = data.get('assigned_peers', [])

    print(f"Received data: {data}")

    if not performance_document_name or not employee_name or not assigned_peers:
        return jsonify({"error": "Missing required parameters"}), 400

    print(f"Searching for peers in the collection: {assigned_peers}")

    # Validate assigned peers with case-insensitive search
    valid_peers = []
    peer_emails = []
    for peer in assigned_peers:
        try:
            first_name, last_name = peer.split(' ', 1)
            print(f"Searching for peer: {peer} (First Name: {first_name}, Last Name: {last_name})")
        except ValueError as e:
            print(f"Error splitting peer name '{peer}': {e}")
            continue

        employee_record = db.s_employeedetails_2.find_one({
            "first_name": {"$regex": f"^{first_name}$", "$options": "i"},
            "last_name": {"$regex": f"^{last_name}$", "$options": "i"}
        })

        if employee_record:
            print(f"Peer {peer} found in the employee details collection.")
            valid_peers.append(peer)
            peer_emails.append(employee_record['email'])
        else:
            print(f"Peer {peer} does not exist in the employee details collection and will be ignored.")

    print(f"Valid peers found: {valid_peers}")

    if not valid_peers:
        return jsonify({"error": "No valid peers found to assign"}), 400

    # Find the performance document associated with the specific employee
    performance_document = assigned_performance_collection.find_one(
        {"performance_document_name": performance_document_name, "employee_name": employee_name}
    )

    if not performance_document:
        print(f"Performance document not found for employee: {employee_name} and document: {performance_document_name}")
        return jsonify({"error": "Performance document not found for the specified employee"}), 404

    print(f"Performance document found: {performance_document}")

    # Update the performance document with valid peers
    update_result = assigned_performance_collection.update_one(
        {"performance_document_name": performance_document_name, "employee_name": employee_name},
        {"$set": {"assigned_peers": valid_peers}}
    )

    if update_result.matched_count == 0:
        print(f"Failed to assign peers to employee: {employee_name}")
        return jsonify({"error": "Failed to assign peers"}), 500

    print(f"Peers assigned successfully to employee: {employee_name}")

    # Prepare the feedback questions
    participant_feedback = performance_document.get('participant_feedback', {})
    questions = participant_feedback.get('questions', [])
    feedback_questions = "\n\n".join([f"{q['question_name']}: {q['question_description']}" for q in questions])

    # Load email template
    body_template = load_template('peer_feedback_email.txt')

    # Email subject and body
    subject = f"Peer Feedback Request for {employee_name}"

    # Send email to each valid peer
    for peer_name, peer_email in zip(valid_peers, peer_emails):
        # Generate unique feedback form link
        feedback_form_id = uuid.uuid4().hex
        # feedback_form_link = url_for('submit_peer_feedback', form_id=feedback_form_id, _external=True)
        # feedback_form_link = url_for('assign_peer_bp.submit_peer_feedback', form_id=performance_document['_id'], _external=True)
        feedback_form_link = url_for('assign_peer_bp.submit_peer_feedback_unique', form_id=performance_document['_id'], _external=True, peer_name=peer_name)



        body = body_template.format(
            peer_name=peer_name,
            employee_name=employee_name,
            feedback_questions=feedback_questions,
            feedback_form_link=feedback_form_link
        )
        send_email(peer_email, subject, body)

    return jsonify({
        "message": "Peers assigned and notified successfully",
        "employee_name": employee_name,
        "assigned_peers": valid_peers
    }), 200


@assign_peer_bp.route('/peer/submit_peer_feedback/<form_id>', methods=['GET', 'POST'])
def submit_peer_feedback(form_id):
    if request.method == 'POST':
        # Retrieve the performance document again in POST request
        performance_document = assigned_performance_collection.find_one({"_id": ObjectId(form_id)})
        
        if not performance_document:
            return "Form not found", 404

        peer_name = request.form.get('peer_name')
        if not peer_name:
            return "Peer name is missing", 400
        
        # Retrieve submitted feedback data
        feedback = request.form.getlist('answers')
        
        # Store feedback in the assigned performance document
        assigned_performance_collection.update_one(
            {"_id": ObjectId(form_id)},
            {"$push": {"peer_reviews": {
                "peer_name": peer_name,
                "responses": [
                    {"question_name": q['question_name'], "question_description": q['question_description'], "answer": ans}
                    for q, ans in zip(performance_document['participant_feedback']['questions'], feedback)
                ]
            }}}
        )
        return "Thank you for submitting your feedback!"

    # Retrieve the form details and render the template with the questions
    performance_document = assigned_performance_collection.find_one({"_id": ObjectId(form_id)})
    if not performance_document:
        return "Form not found", 404

    participant_feedback = performance_document.get("participant_feedback", {})
    questions = participant_feedback.get("questions", [])
    employee_name = performance_document.get("employee_name", "")
    peer_name = request.args.get('peer_name')  # Pass the peer_name as a query parameter

    if not peer_name:
        return "Peer name is missing", 400

    # Peer name should be passed here when rendering the template
    return render_template('peer_feedback_form.html', questions=questions, employee_name=employee_name, form_id=form_id, peer_name=peer_name)


@assign_peer_bp.route('/submit_peer_feedback/<form_id>', methods=['GET', 'POST'], endpoint='submit_peer_feedback_unique')
def submit_peer_feedback(form_id):
    if request.method == 'POST':
        # Retrieve the performance document again in POST request
        performance_document = assigned_performance_collection.find_one({"_id": ObjectId(form_id)})
        
        if not performance_document:
            return "Form not found", 404

        peer_name = request.form.get('peer_name')
        if not peer_name:
            return "Peer name is missing", 400
        
        # Retrieve submitted feedback data
        feedback = request.form.getlist('answers')
        
        # Store feedback in the assigned performance document
        assigned_performance_collection.update_one(
            {"_id": ObjectId(form_id)},
            {"$push": {"peer_reviews": {
                "peer_name": peer_name,
                "responses": [
                    {"question_name": q['question_name'], "question_description": q['question_description'], "answer": ans}
                    for q, ans in zip(performance_document['participant_feedback']['questions'], feedback)
                ]
            }}}
        )
        return "Thank you for submitting your feedback!"

    # Retrieve the form details and render the template with the questions
    performance_document = assigned_performance_collection.find_one({"_id": ObjectId(form_id)})
    if not performance_document:
        return "Form not found", 404

    participant_feedback = performance_document.get("participant_feedback", {})
    questions = participant_feedback.get("questions", [])
    employee_name = performance_document.get("employee_name", "")
    peer_name = request.args.get('peer_name')  # Pass the peer_name as a query parameter

    if not peer_name:
        return "Peer name is missing", 400

    # Peer name should be passed here when rendering the template
    return render_template('peer_feedback_form.html', questions=questions, employee_name=employee_name, form_id=form_id, peer_name=peer_name)




