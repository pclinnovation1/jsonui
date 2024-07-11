# from flask import Blueprint, request, jsonify
# from datetime import datetime
# from utils.email_reminder import predict_days_to_send, adjust_response_likelihood

# email_reminder_bp = Blueprint('email_reminder', __name__)

# @email_reminder_bp.route('/reminders', methods=['POST'])
# def send_reminders():
#     data = request.json
#     most_active_day = data.get('most_active_day')
#     response_likelihood = data.get('response_likelihood')
#     tone = data.get('tone')
#     current_date = datetime.now()
    
#     # Predict the number of days to wait
#     days_to_wait = predict_days_to_send(most_active_day, response_likelihood, tone, current_date)
    
#     # Example user compliance input (for testing purposes, assume 'yes')
#     user_complied_input = 'yes'
#     user_complied = user_complied_input == 'yes'
    
#     # Adjust response likelihood for a specific record (example with a default response likelihood)
#     original_response_likelihood = response_likelihood
#     new_response_likelihood = adjust_response_likelihood(original_response_likelihood, user_complied)
    
#     return jsonify({
#         "Predicted days to wait": days_to_wait,
#         "Original Response Likelihood": original_response_likelihood,
#         "New Response Likelihood": new_response_likelihood
#     }), 200
 
 
 
####
# from flask import Blueprint, request, jsonify, current_app, url_for
# from bson.objectid import ObjectId
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# import datetime

# transaction_bp = Blueprint('transaction', __name__)

# @transaction_bp.route('/api/transactions/reminders', methods=['POST'])
# def send_reminders():
#     data = request.json
#     transaction_id = data.get("transaction_id")
#     transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})

#     if not transaction:
#         return jsonify({"error": "Transaction not found"}), 404

#     for approval in transaction['approvals']:
#         if approval['status'] == 'pending':
#             approver_id = approval['approverId']
#             approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})

#             if not approver:
#                 continue

#             approver_emails = approver['email']
#             if not isinstance(approver_emails, list):
#                 approver_emails = [approver_emails]

#             for approver_email in approver_emails:
#                 send_email_reminder(approver_email, str(transaction['_id']), approver_id)
#                 approval['reminder_sent'] = True
#                 approval['reminder_sent_at'] = datetime.datetime.utcnow()
#                 approval['reminder_sent_to'] = approver_emails  # Store all emails

#             current_app.mongo.db.transactions.update_one(
#                 {"_id": ObjectId(transaction_id)},
#                 {"$set": {"approvals": transaction['approvals'], "updated_at": datetime.datetime.utcnow()}}
#             )
#             return jsonify({"message": "Reminder sent to the first pending approver"}), 200

#     return jsonify({"message": "No pending approvals found"}), 404

# def send_email_reminder(approver_email, transaction_id, approver_id):
#     from_email = "piyushbirkh@gmail.com"
#     password = "teaz yfbj jcie twrt"  # Use an app password if 2FA is enabled

#     to_email = approver_email
#     subject = "Approval Reminder"
#     approve_url = url_for('transaction.update_approval_status', transaction_id=transaction_id, status='approved', approver_id=approver_id, _external=True)
#     reject_url = url_for('transaction.update_approval_status', transaction_id=transaction_id, status='rejected', approver_id=approver_id, _external=True)
#     changes_url = url_for('transaction.update_approval_status', transaction_id=transaction_id, status='changes_requested', approver_id=approver_id, _external=True)

#     body = f"""
#     <html>
#     <body>
#         <p>You have a pending approval request.</p>
#         <p>Transaction ID: {transaction_id}</p>
#         <p>Please approve or reject the request using the buttons below:</p>
#         <p>
#             <a href="{approve_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: green; color: white; text-decoration: none;">Approve</a>
#             <a href="{reject_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: red; color: white; text-decoration: none;">Reject</a>
#             <a href="{changes_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: orange; color: white; text-decoration: none;">Request Changes</a>
#         </p>
#     </body>
#     </html>
#     """

#     msg = MIMEMultipart()
#     msg['From'] = from_email
#     msg['To'] = to_email
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'html'))

#     with smtplib.SMTP('smtp.gmail.com', 587) as server:
#         server.starttls()
#         server.login(from_email, password)
#         server.send_message(msg)

# @transaction_bp.route('/api/transactions/<transaction_id>/update_status/<status>', methods=['GET'])
# def update_approval_status(transaction_id, status):
#     transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})

#     if not transaction:
#         return jsonify({"error": "Transaction not found"}), 404

#     approver_id = request.args.get("approver_id")
#     if not approver_id:
#         return jsonify({"error": "Approver ID not provided"}), 400

#     for approval in transaction['approvals']:
#         if approval['approverId'] == approver_id:
#             approval['status'] = status
#             approval['timestamp'] = datetime.datetime.utcnow()
#             break

#     current_app.mongo.db.transactions.update_one(
#         {"_id": ObjectId(transaction_id)},
#         {"$set": {"approvals": transaction['approvals'], "updated_at": datetime.datetime.utcnow()}}
#     )

#     return jsonify({"message": "Approval status updated", "transaction": str(transaction['_id'])}), 200















#####
# from flask import Blueprint, request, jsonify, current_app, url_for
# from bson.objectid import ObjectId
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# import datetime

# email_reminder_bp = Blueprint('email_reminder', __name__)

# @email_reminder_bp.route('/api/transactions/reminders', methods=['POST'])
# def send_reminders():
#     data = request.json
#     transaction_id = data.get("transaction_id")
#     transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})

#     if not transaction:
#         return jsonify({"error": "Transaction not found"}), 404

#     for approval in transaction['approvals']:
#         if approval['status'] == 'pending':
#             approver_id = approval['approverId']
#             approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})

#             if not approver:
#                 continue

#             approver_emails = approver['email']
#             if not isinstance(approver_emails, list):
#                 approver_emails = [approver_emails]

#             process = current_app.mongo.db.processes.find_one({"processId": transaction['processId']})
#             process_name = process['name'] if process else 'N/A'
#             process_description = process['description'] if process else 'N/A'

#             for approver_email in approver_emails:
#                 send_email_reminder(approver_email, str(transaction['_id']), approver_id, process_name, process_description)
#                 approval['reminder_sent'] = True
#                 approval['reminder_sent_at'] = datetime.datetime.utcnow()
#                 approval['reminder_sent_to'] = approver_emails  # Store all emails

#             current_app.mongo.db.transactions.update_one(
#                 {"_id": ObjectId(transaction_id)},
#                 {"$set": {"approvals": transaction['approvals'], "updated_at": datetime.datetime.utcnow()}}
#             )
#             return jsonify({"message": "Reminder sent to the first pending approver"}), 200

#     return jsonify({"message": "No pending approvals found"}), 404

# def send_email_reminder(approver_email, transaction_id, approver_id, process_name, process_description):
#     from_email = "piyushbirkh@gmail.com"
#     password = "teaz yfbj jcie twrt"  # Use an app password if 2FA is enabled

#     to_email = approver_email
#     subject = "Approval Reminder"
#     approve_url = url_for('transaction.update_approval_status', transaction_id=transaction_id, status='approved', approver_id=approver_id, _external=True)
#     reject_url = url_for('transaction.update_approval_status', transaction_id=transaction_id, status='rejected', approver_id=approver_id, _external=True)
#     changes_url = url_for('transaction.request_changes_form', transaction_id=transaction_id, approver_id=approver_id, _external=True)

#     body = f"""
#     <html>
#     <body>
#         <p>You have a pending approval request.</p>
#         <p>Transaction ID: {transaction_id}</p>
#         <p>Process Name: {process_name}</p>
#         <p>Process Description: {process_description}</p>
#         <p>Please approve or reject the request using the buttons below:</p>
#         <p>
#             <a href="{approve_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: green; color: white; text-decoration: none;">Approve</a>
#             <a href="{reject_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: red; color: white; text-decoration: none;">Reject</a>
#             <a href="{changes_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: orange; color: white; text-decoration: none;">Request Changes</a>
#         </p>
#     </body>
#     </html>
#     """

#     msg = MIMEMultipart()
#     msg['From'] = from_email
#     msg['To'] = to_email
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'html'))

#     with smtplib.SMTP('smtp.gmail.com', 587) as server:
#         server.starttls()
#         server.login(from_email, password)
#         server.send_message(msg)





















#####
# from flask import Blueprint, request, jsonify, current_app, url_for
# from bson.objectid import ObjectId
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# import datetime

# email_reminder_bp = Blueprint('email_reminder', __name__)

# @email_reminder_bp.route('/api/transactions/reminders', methods=['POST'])
# def send_reminders():
#     data = request.json
#     transaction_id = data.get("transaction_id")
#     transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})

#     if not transaction:
#         return jsonify({"error": "Transaction not found"}), 404

#     for approval in transaction['approvals']:
#         if approval['status'] == 'pending':
#             approver_id = approval['approverId']
#             approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})

#             if not approver:
#                 continue

#             approver_emails = approver['email']
#             if not isinstance(approver_emails, list):
#                 approver_emails = [approver_emails]

#             process = current_app.mongo.db.processes.find_one({"processId": transaction['processId']})
#             process_name = process['name'] if process else 'N/A'
#             process_description = process['description'] if process else 'N/A'

#             for approver_email in approver_emails:
#                 send_email_reminder(approver_email, str(transaction['_id']), approver_id, process_name, process_description)
#                 approval['reminder_sent'] = True
#                 approval['reminder_sent_at'] = datetime.datetime.utcnow()
#                 approval['reminder_sent_to'] = approver_emails  # Store all emails

#             current_app.mongo.db.transactions.update_one(
#                 {"_id": ObjectId(transaction_id)},
#                 {"$set": {"approvals": transaction['approvals'], "updated_at": datetime.datetime.utcnow()}}
#             )
#             return jsonify({"message": "Reminder sent to the first pending approver"}), 200

#     return jsonify({"message": "No pending approvals found"}), 404

# def send_email_reminder(approver_email, transaction_id, approver_id, process_name, process_description):
#     from_email = "piyushbirkh@gmail.com"
#     password = "teaz yfbj jcie twrt"  # Use an app password if 2FA is enabled

#     to_email = approver_email
#     subject = "Approval Reminder"
#     approve_url = url_for('transaction_bp.update_approval_status', transaction_id=transaction_id, status='approved', approver_id=approver_id, _external=True)
#     reject_url = url_for('transaction_bp.update_approval_status', transaction_id=transaction_id, status='rejected', approver_id=approver_id, _external=True)
#     changes_url = url_for('transaction_bp.request_changes_form', transaction_id=transaction_id, approver_id=approver_id, _external=True)

#     body = f"""
#     <html>
#     <body>
#         <p>You have a pending approval request.</p>
#         <p>Transaction ID: {transaction_id}</p>
#         <p>Process Name: {process_name}</p>
#         <p>Process Description: {process_description}</p>
#         <p>Please approve or reject the request using the buttons below:</p>
#         <p>
#             <a href="{approve_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: green; color: white; text-decoration: none;">Approve</a>
#             <a href="{reject_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: red; color: white; text-decoration: none;">Reject</a>
#             <a href="{changes_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: orange; color: white; text-decoration: none;">Request Changes</a>
#         </p>
#     </body>
#     </html>
#     """

#     msg = MIMEMultipart()
#     msg['From'] = from_email
#     msg['To'] = to_email
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'html'))

#     with smtplib.SMTP('smtp.gmail.com', 587) as server:
#         server.starttls()
#         server.login(from_email, password)
#         server.send_message(msg)












######
from flask import Blueprint, request, jsonify, current_app, url_for
from bson.objectid import ObjectId
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime

email_reminder_bp = Blueprint('email_reminder_bp', __name__)

@email_reminder_bp.route('/api/transactions/reminders', methods=['POST'])
def send_reminders():
    data = request.json
    transaction_id = data.get("transaction_id")
    transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})

    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    for approval in transaction['approvals']:
        if approval['status'] == 'pending':
            approver_id = approval['approverId']
            approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})

            if not approver:
                continue

            approver_emails = approver['email']
            if not isinstance(approver_emails, list):
                approver_emails = [approver_emails]

            process = current_app.mongo.db.processes.find_one({"processId": transaction['processId']})
            process_name = process['name'] if process else 'N/A'
            process_description = process['description'] if process else 'N/A'

            for approver_email in approver_emails:
                send_email_reminder(approver_email, str(transaction['_id']), approver_id, process_name, process_description)
                approval['reminder_sent'] = True
                approval['reminder_sent_at'] = datetime.datetime.utcnow()
                approval['reminder_sent_to'] = approver_emails  # Store all emails

            current_app.mongo.db.transactions.update_one(
                {"_id": ObjectId(transaction_id)},
                {"$set": {"approvals": transaction['approvals'], "updated_at": datetime.datetime.utcnow()}}
            )
            return jsonify({"message": "Reminder sent to the first pending approver"}), 200

    return jsonify({"message": "No pending approvals found"}), 404

def send_email_reminder(approver_email, transaction_id, approver_id, process_name, process_description):
    from_email = "piyushbirkh@gmail.com"
    password = "teaz yfbj jcie twrt"  # Use an app password if 2FA is enabled

    to_email = approver_email
    subject = "Approval Reminder"
    approve_url = url_for('transaction_bp.update_approval_status', transaction_id=transaction_id, status='approved', approver_id=approver_id, _external=True)
    reject_url = url_for('transaction_bp.update_approval_status', transaction_id=transaction_id, status='rejected', approver_id=approver_id, _external=True)
    changes_url = url_for('transaction_bp.request_changes_form', transaction_id=transaction_id, approver_id=approver_id, _external=True)
    change_approver_url = url_for('transaction_bp.change_approver_form', transaction_id=transaction_id, _external=True)

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
            <a href="{changes_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: orange; color: white; text-decoration: none;">Request Changes</a>
        </p>
        <p>
            <a href="{change_approver_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: blue; color: white; text-decoration: none;">Change Approver</a>
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
