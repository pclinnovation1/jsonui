import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import config

# Define the Blueprint
peer_feedback_bp = Blueprint('peer_feedback_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
assigned_performance_collection = db['P_assigned_performance']
employee_details_collection = db['s_employee_details_2']

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

# API route to notify assigned peers
@peer_feedback_bp.route('/notify_peers', methods=['POST'])
def notify_peers():
    data = request.json
    performance_document_name = data.get('performance_document_name')
    employee_name = data.get('employee_name')

    print(f"Received data: {data}")

    if not performance_document_name or not employee_name:
        return jsonify({"error": "Missing required parameters"}), 400

    # Find the performance document for the employee
    performance_document = assigned_performance_collection.find_one(
        {"performance_document_name": performance_document_name, "employee_name": employee_name}
    )

    if not performance_document:
        return jsonify({"error": f"Performance document not found for employee: {employee_name}"}), 404

    assigned_peers = performance_document.get('assigned_peers', [])
    participant_feedback = performance_document.get('participant_feedback', {})

    if not assigned_peers:
        return jsonify({"error": "No peers assigned to notify"}), 400

    if not participant_feedback:
        return jsonify({"error": "No participant feedback template found in the performance document"}), 400

    # Prepare the feedback questions
    questions = participant_feedback.get('questions', [])
    feedback_questions = "\n\n".join([f"{q['question_name']}: {q['question_description']}" for q in questions])

    # Email subject and body
    subject = f"Peer Feedback Request for {employee_name}"
    body_template = f"""
    Dear {{peer_name}},

    You have been selected to provide feedback for your colleague, {employee_name}.

    Below are the questions you need to answer:

    {feedback_questions}

    Please fill out the feedback form at your earliest convenience.

    Thank you,
    Your HR Team
    """

    # Notify each assigned peer via email
    for peer_name in assigned_peers:
        print(f"Looking up details for peer: {peer_name}")

        first_name, last_name = peer_name.split(' ', 1)
        peer_details = employee_details_collection.find_one({
            "first_name": {"$regex": f"^{first_name}$", "$options": "i"},
            "last_name": {"$regex": f"^{last_name}$", "$options": "i"}
        })

        if not peer_details or 'email' not in peer_details:
            print(f"Peer {peer_name} does not have an email address or was not found in the system.")
            continue

        peer_email = peer_details['email']
        peer_name_formatted = f"{peer_details['first_name']} {peer_details['last_name']}"
        body = body_template.format(peer_name=peer_name_formatted)

        print(f"Sending email to {peer_email}")
        send_email(peer_email, subject, body)

    return jsonify({"message": "Emails sent to assigned peers"}), 200
