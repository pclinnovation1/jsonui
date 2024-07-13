# transaction_controller.py
from flask import Blueprint, request, jsonify, current_app, url_for
from bson.objectid import ObjectId
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

transaction_bp = Blueprint('transaction_bp', __name__)

@transaction_bp.route('/transactions', methods=['POST'])
def create_transaction():
    data = request.get_json()
    print("Received data:", data)

    process_name = data.get('processName')
    amount = data.get('amount')
    employee_id = data.get('employeeId')
    employee_name = data.get('employeeName')
    
    if not process_name or not amount or not employee_id or not employee_name:
        return jsonify({"error": "processName, amount, employeeId, and employeeName are required"}), 400

    process = current_app.mongo.db.processes.find_one({"name": process_name})
    if not process:
        return jsonify({"error": "Process not found for the given process name"}), 404

    process_id = process['processId']
    process_description = process.get('description', 'No description provided')

    transaction = {
        'transactionId': str(ObjectId()),
        'processName': process_name,
        'processId': process_id,
        'amount': amount,
        'employeeId': employee_id,
        'employeeName': employee_name,
        'processDescription': process_description,
        'status': 'pending',
        'currentLevel': 1,
        'createdAt': datetime.utcnow(),
        'updatedAt': datetime.utcnow(),
        'approvals': [],
        'approval_actions': []
    }

    approval_rules = current_app.mongo.db.approval_rules.find_one({"processName": process_name})
    if not approval_rules:
        return jsonify({"error": "Approval rule not found for the given process name"}), 404

    # Initialize approvals based on all levels in the approval rules
    for rule in approval_rules['rules']:
        approver_id = rule['approverId']
        print(f"Looking for approver with ID: {approver_id}")
        approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})
        if approver:
            approval_entry = {
                'approverId': approver_id,
                'status': 'pending',
                'email_approver': approver['email']
            }
            transaction['approvals'].append(approval_entry)
        else:
            print(f"Approver with ID {approver_id} not found")

    transaction_id = current_app.mongo.db.transactions.insert_one(transaction).inserted_id
    transaction['_id'] = str(transaction_id)  # Convert ObjectId to string

    return jsonify({"message": "Transaction created", "transaction": transaction}), 201

@transaction_bp.route('/<transaction_id>/approve_request/<status>', methods=['GET'])
def approve_request(transaction_id, status):
    approver_id = request.args.get("approver_id")
    actions_taken = request.args.get("actions_taken", "NA")  # Capture actions taken

    if not approver_id:
        return jsonify({"error": "Approver ID not provided"}), 400

    try:
        approver_id_obj = ObjectId(approver_id)
    except Exception as e:
        return jsonify({"error": f"Invalid approver ID format: {str(e)}"}), 400

    transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    approver = current_app.mongo.db.approvers.find_one({"_id": approver_id_obj})
    if not approver:
        return jsonify({"error": "Approver not found"}), 404

    approver_email = approver['email']

    approval_action = {
        'approved_by': approver_email,
        'actions_taken': actions_taken,
        'approval_action': status,
        'timestamp': datetime.utcnow()
    }
    transaction['approval_actions'].append(approval_action)

    for approval in transaction['approvals']:
        if approval['approverId'] == approver_id:
            approval['status'] = status

    current_app.mongo.db.transactions.update_one(
        {"_id": ObjectId(transaction_id)},
        {"$set": {
            "approvals": transaction['approvals'],
            "approval_actions": transaction['approval_actions'],
            "updated_at": datetime.utcnow()
        }}
    )

    return jsonify({"message": "Approval status updated", "transaction": str(transaction['_id'])}), 200

@transaction_bp.route('/reminders', methods=['POST'])
def send_reminders():
    data = request.json
    process_name = data.get("processName")
    process_description = data.get('description', 'No description provided')

    if not process_name:
        return jsonify({"error": "Process name not provided"}), 400

    pending_transactions = list(current_app.mongo.db.transactions.find({"processName": process_name, "status": "pending"}))
    pending_count = len(pending_transactions)

    if pending_count == 0:
        return jsonify({"message": "No pending transactions found for the given process"}), 404

    for transaction in pending_transactions:
        process_description=transaction['processDescription']
        for approval in transaction['approvals']:
            if approval['status'] == 'pending':
                approver_id = approval['approverId']
                approver_emails = approval['email_approver']

                
                if not isinstance(approver_emails, list):
                    approver_emails = [approver_emails]

                #process_description = "Description of the process"  # Assuming you want to include a description
                process_description = process_description

                for approver_email in approver_emails:
                    send_email_reminder(approver_email, str(transaction['_id']), approver_id, process_name, process_description)
                
                approval['reminder_sent'] = True
                approval['reminder_sent_at'] = datetime.utcnow()
                approval['reminder_sent_to'] = approver_emails  # Store all emails

                # Update the transaction with the reminder information for the first pending approver only
                current_app.mongo.db.transactions.update_one(
                    {"_id": ObjectId(transaction['_id'])},
                    {"$set": {"approvals": transaction['approvals'], "updated_at": datetime.utcnow()}}
                )
                break  # Stop after the first pending approver

    return jsonify({"message": f"Reminder sent to the first pending approver in all transactions", "pending_transactions_count": pending_count}), 200

def send_email_reminder(approver_email, transaction_id, approver_id, process_name, process_description):
    from_email = "piyushbirkh@gmail.com"
    password = "teaz yfbj jcie twrt"  # Use an app password if 2FA is enabled

    to_email = approver_email
    subject = "Approval Reminder"
    approve_url = url_for('transaction_bp.approve_request', transaction_id=transaction_id, status='approved', approver_id=approver_id, actions_taken="approved actions", _external=True)
    reject_url = url_for('transaction_bp.approve_request', transaction_id=transaction_id, status='rejected', approver_id=approver_id, actions_taken="rejected actions", _external=True)
    
    body = f"""
    <html>
    <body>
        <p>You have a pending approval request.</p>
        <p>Transaction ID: {transaction_id}</p>
        <p>Process Name: {process_name}</p>
        <p>Process Description: {process_description}</p>
        <p>Please approve or reject the request using the buttons below:</p>
        <p>
            <a href="{approve_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: green; color: white; text-decoration: none;">Approve</a>
            <a href="{reject_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: red; color: white; text-decoration: none;">Reject</a>
        </p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
