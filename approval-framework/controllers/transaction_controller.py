# from flask import Blueprint, request, jsonify, current_app, url_for, render_template_string
# from bson.objectid import ObjectId
# from utils.condition_evaluator import evaluate_condition
# from datetime import datetime
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# transaction_bp = Blueprint('transaction_bp', __name__)

# @transaction_bp.route('/', methods=['POST'])
# def create_transaction():
#     data = request.get_json()
#     print("Received data:", data)

#     process_id = data.get('processId')
#     transaction_fields = data.get('transaction_fields', {})
#     field_types = data.get('fieldType', [])
#     field_values = transaction_fields.get('value', [])
#     print(process_id)
#     print(transaction_fields)
#     print(field_types)
#     print(field_values)

#     transaction = {
#         'processId': process_id,
#         # 'amount': transaction_fields.get('amount'),
#         'fieldType': field_types,
#         'status': 'pending',
#         'createdAt': datetime.utcnow(),
#         'updatedAt': datetime.utcnow(),
#         'approvals': [],
#         'approval_actions': []
#     }

#     approval_rules = current_app.mongo.db.approval_rules.find_one({"processId": process_id})
#     print("Approval Rules:", approval_rules)

#     if not approval_rules:
#         print("No approval rules found for the given process ID")
#         return jsonify({"error": "No approval rules found for the given process ID"}), 404

#     approvers_set = set()  # To track distinct approvers

#     for rule in approval_rules['rules']:
#         condition = rule['condition']
#         print("Evaluating condition:", condition)

#         if evaluate_condition(field_types, field_values, condition):
#             print("Condition matched:", condition)
#             for approver_id in rule['approvers']:
#                 if approver_id not in approvers_set:
#                     approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})
#                     if approver:
#                         approval_entry = {
#                             'approverId': approver_id,
#                             'status': 'pending',
#                             'email_approver': approver['email']
#                         }
#                         transaction['approvals'].append(approval_entry)
#                         approvers_set.add(approver_id)
#                         print("Approval entry added:", approval_entry)
#         else:
#             print("Condition did not match:", condition)

#     transaction_id = current_app.mongo.db.transactions.insert_one(transaction).inserted_id
#     transaction['_id'] = str(transaction_id)  # Convert ObjectId to string

#     print("Final transaction:", transaction)
#     return jsonify({"message": "Transaction created", "transaction": transaction}), 201


# @transaction_bp.route('/reminders', methods=['POST'])
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
#                 approval['reminder_sent_at'] = datetime.utcnow()
#                 approval['reminder_sent_to'] = approver_emails  # Store all emails

#             current_app.mongo.db.transactions.update_one(
#                 {"_id": ObjectId(transaction_id)},
#                 {"$set": {"approvals": transaction['approvals'], "updated_at": datetime.utcnow()}}
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
#     change_approver_url = url_for('transaction_bp.change_approver_form', transaction_id=transaction_id, _external=True)

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
#         <p>
#             <a href="{change_approver_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: blue; color: white; text-decoration: none;">Change Approver</a>
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

# @transaction_bp.route('/<transaction_id>/update_status/<status>', methods=['GET'])
# def update_approval_status(transaction_id, status):
#     transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})

#     if not transaction:
#         return jsonify({"error": "Transaction not found"}), 404

#     approver_id = request.args.get("approver_id")
#     if not approver_id:
#         return jsonify({"error": "Approver ID not provided"}), 400

#     approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})
#     if not approver:
#         return jsonify({"error": "Approver not found"}), 404

#     approver_email = approver['email'][0] if isinstance(approver['email'], list) else approver['email']
#     change_request = request.args.get("change_request", "NA")

#     approval_action = {
#         'approved_by': approver_email,
#         'actions_taken': change_request,
#         'approval_action': status,
#         'timestamp': datetime.utcnow()
#     }
#     transaction['approval_actions'].append(approval_action)

#     for approval in transaction['approvals']:
#         if approval['approverId'] == approver_id:
#             approval['status'] = status

#     current_app.mongo.db.transactions.update_one(
#         {"_id": ObjectId(transaction_id)},
#         {"$set": {
#             "approvals": transaction['approvals'],
#             "approval_actions": transaction['approval_actions'],
#             "updated_at": datetime.utcnow()
#         }}
#     )

#     return jsonify({"message": "Approval status updated", "transaction": str(transaction['_id'])}), 200

# @transaction_bp.route('/<transaction_id>/request_changes_form', methods=['GET'])
# def request_changes_form(transaction_id):
#     approver_id = request.args.get("approver_id")
    
#     return f"""
#     <html>
#     <body>
#         <form action="/api/transactions/{transaction_id}/request_changes" method="post">
#             <p>Approver ID: {approver_id}</p>
#             <input type="hidden" name="approver_id" value="{approver_id}">
#             <textarea name="change_request" rows="4" cols="50" placeholder="Enter your change request here..."></textarea>
#             <button type="submit">Submit Change Request</button>
#         </form>
#     </body>
#     </html>
#     """

# @transaction_bp.route('/<transaction_id>/request_changes', methods=['POST'])
# def request_changes(transaction_id):
#     approver_id = request.form.get("approver_id")
#     change_request = request.form.get("change_request")

#     if not approver_id or not change_request:
#         return jsonify({"error": "Approver ID and change request are required"}), 400

#     transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})

#     if not transaction:
#         return jsonify({"error": "Transaction not found"}), 404

#     approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})
#     if not approver:
#         return jsonify({"error": "Approver not found"}), 404

#     approver_email = approver['email'][0] if isinstance(approver['email'], list) else approver['email']

#     approval_action = {
#         'approved_by': approver_email,
#         'actions_taken': change_request,
#         'approval_action': 'changes_requested',
#         'timestamp': datetime.utcnow()
#     }
#     transaction['approval_actions'].append(approval_action)

#     for approval in transaction['approvals']:
#         if approval['approverId'] == approver_id:
#             approval['status'] = 'changes_requested'

#     current_app.mongo.db.transactions.update_one(
#         {"_id": ObjectId(transaction_id)},
#         {"$set": {
#             "approvals": transaction['approvals'],
#             "approval_actions": transaction['approval_actions'],
#             "updated_at": datetime.utcnow()
#         }}
#     )

#     return jsonify({"message": "Change request submitted", "transaction": str(transaction['_id'])}), 200

# @transaction_bp.route('/<transaction_id>/change_approver_form', methods=['GET'])
# def change_approver_form(transaction_id):
#     approvers = current_app.mongo.db.approvers.find()
#     options = ''.join([f'<option value="{approver["email"]}">{approver["email"]}</option>' for approver in approvers])

#     form_html = f"""
#     <html>
#     <body>
#         <form action="/api/transactions/{transaction_id}/change_approver" method="post">
#             <p>Select new approver email:</p>
#             <select name="new_approver_email">
#                 {options}
#             </select>
#             <button type="submit">Change Approver</button>
#         </form>
#     </body>
#     </html>
#     """
#     return render_template_string(form_html)

# @transaction_bp.route('/<transaction_id>/change_approver', methods=['POST'])
# def change_approver(transaction_id):
#     new_approver_email = request.form.get("new_approver_email")

#     if not new_approver_email:
#         return jsonify({"error": "New approver email is required"}), 400

#     transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})

#     if not transaction:
#         return jsonify({"error": "Transaction not found"}), 404

#     new_approver = current_app.mongo.db.approvers.find_one({"email": new_approver_email})

#     if not new_approver:
#         return jsonify({"error": "New approver not found"}), 404

#     new_approver_id = new_approver['approverId']

#     approval_entry = {
#         'approverId': new_approver_id,
#         'status': 'pending',
#         'email_approver': [new_approver_email],
#     }
#     transaction['approvals'].append(approval_entry)

#     current_app.mongo.db.transactions.update_one(
#         {"_id": ObjectId(transaction_id)},
#         {"$set": {"approvals": transaction['approvals'], "updated_at": datetime.utcnow()}}
#     )

#     send_email_reminder(new_approver_email, transaction_id, new_approver_id, "Change Department", "Process to change Department")

#     return jsonify({"message": "New approver assigned and reminder sent", "transaction": str(transaction['_id'])}), 200




























































































# from flask import Blueprint, request, jsonify, current_app, url_for, render_template_string
# from bson.objectid import ObjectId
# from utils.condition_evaluator import evaluate_condition
# from datetime import datetime
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# transaction_bp = Blueprint('transaction_bp', __name__)

# @transaction_bp.route('/', methods=['POST'])
# def create_transaction():
#     data = request.get_json()
#     print("Received data:", data)

#     process_id = data.get('processId')
#     transaction_fields = data.get('transaction_fields', {})
#     field_types = data.get('fieldType', [])
#     field_values = transaction_fields.get('value', [])
#     print(process_id)
#     print(transaction_fields)
#     print(field_types)
#     print(field_values)

#     transaction = {
#         'processId': process_id,
#         'fieldType': field_types,
#         'status': 'pending',
#         'createdAt': datetime.utcnow(),
#         'updatedAt': datetime.utcnow(),
#         'approvals': [],
#         'approval_actions': []
#     }

#     approval_rules = current_app.mongo.db.approval_rules.find_one({"processId": process_id})
#     print("Approval Rules:", approval_rules)

#     if not approval_rules:
#         print("No approval rules found for the given process ID")
#         return jsonify({"error": "No approval rules found for the given process ID"}), 404

#     approvers_set = set()  # To track distinct approvers

#     for rule in approval_rules['rules']:
#         condition = rule['condition']
#         print("Evaluating condition:", condition)

#         if evaluate_condition(field_types, field_values, condition):
#             print("Condition matched:", condition)
#             for approver_id in rule['approvers']:
#                 if approver_id not in approvers_set:
#                     approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})
#                     if approver:
#                         approval_entry = {
#                             'approverId': approver_id,
#                             'status': 'pending',
#                             'email_approver': approver['email']
#                         }
#                         transaction['approvals'].append(approval_entry)
#                         approvers_set.add(approver_id)
#                         print("Approval entry added:", approval_entry)
#         else:
#             print("Condition did not match:", condition)

#     transaction_id = current_app.mongo.db.transactions.insert_one(transaction).inserted_id
#     transaction['_id'] = str(transaction_id)  # Convert ObjectId to string

#     print("Final transaction:", transaction)
#     return jsonify({"message": "Transaction created", "transaction": transaction}), 201


# @transaction_bp.route('/reminders', methods=['POST'])
# def send_reminders():
#     data = request.json
#     process_name = data.get("processName")

#     if not process_name:
#         return jsonify({"error": "Process name not provided"}), 400

#     process = current_app.mongo.db.processes.find_one({"name": process_name})

#     if not process:
#         return jsonify({"error": "Process not found"}), 404

#     process_id = process['processId']
#     pending_transactions = current_app.mongo.db.transactions.find({"processId": process_id, "status": "pending"})

#     if pending_transactions.count() == 0:
#         return jsonify({"message": "No pending transactions found for the given process"}), 404

#     for transaction in pending_transactions:
#         for approval in transaction['approvals']:
#             if approval['status'] == 'pending':
#                 approver_id = approval['approverId']
#                 approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})

#                 if not approver:
#                     continue

#                 approver_emails = approver['email']
#                 if not isinstance(approver_emails, list):
#                     approver_emails = [approver_emails]

#                 process_name = process['name']
#                 process_description = process['description']

#                 for approver_email in approver_emails:
#                     send_email_reminder(approver_email, str(transaction['_id']), approver_id, process_name, process_description)
#                     approval['reminder_sent'] = True
#                     approval['reminder_sent_at'] = datetime.utcnow()
#                     approval['reminder_sent_to'] = approver_emails  # Store all emails

#                 current_app.mongo.db.transactions.update_one(
#                     {"_id": ObjectId(transaction['_id'])},
#                     {"$set": {"approvals": transaction['approvals'], "updated_at": datetime.utcnow()}}
#                 )
#                 return jsonify({"message": "Reminder sent to the first pending approver in all transactions"}), 200

#     return jsonify({"message": "No pending approvals found"}), 404

# def send_email_reminder(approver_email, transaction_id, approver_id, process_name, process_description):
#     from_email = "piyushbirkh@gmail.com"
#     password = "teaz yfbj jcie twrt"  # Use an app password if 2FA is enabled

#     to_email = approver_email
#     subject = "Approval Reminder"
#     approve_url = url_for('transaction_bp.update_approval_status', transaction_id=transaction_id, status='approved', approver_id=approver_id, _external=True)
#     reject_url = url_for('transaction_bp.update_approval_status', transaction_id=transaction_id, status='rejected', approver_id=approver_id, _external=True)
#     changes_url = url_for('transaction_bp.request_changes_form', transaction_id=transaction_id, approver_id=approver_id, _external=True)
#     change_approver_url = url_for('transaction_bp.change_approver_form', transaction_id=transaction_id, _external=True)

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
#         <p>
#             <a href="{change_approver_url}" style="display: inline-block; padding: 10px 20px; margin: 5px; background-color: blue; color: white; text-decoration: none;">Change Approver</a>
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

# @transaction_bp.route('/<transaction_id>/update_status/<status>', methods=['GET'])
# def update_approval_status(transaction_id, status):
#     transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})

#     if not transaction:
#         return jsonify({"error": "Transaction not found"}), 404

#     approver_id = request.args.get("approver_id")
#     if not approver_id:
#         return jsonify({"error": "Approver ID not provided"}), 400

#     approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})
#     if not approver:
#         return jsonify({"error": "Approver not found"}), 404

#     approver_email = approver['email'][0] if isinstance(approver['email'], list) else approver['email']
#     change_request = request.args.get("change_request", "NA")

#     approval_action = {
#         'approved_by': approver_email,
#         'actions_taken': change_request,
#         'approval_action': status,
#         'timestamp': datetime.utcnow()
#     }
#     transaction['approval_actions'].append(approval_action)

#     for approval in transaction['approvals']:
#         if approval['approverId'] == approver_id:
#             approval['status'] = status

#     current_app.mongo.db.transactions.update_one(
#         {"_id": ObjectId(transaction_id)},
#         {"$set": {
#             "approvals": transaction['approvals'],
#             "approval_actions": transaction['approval_actions'],
#             "updated_at": datetime.utcnow()
#         }}
#     )

#     return jsonify({"message": "Approval status updated", "transaction": str(transaction['_id'])}), 200

# @transaction_bp.route('/<transaction_id>/request_changes_form', methods=['GET'])
# def request_changes_form(transaction_id):
#     approver_id = request.args.get("approver_id")
    
#     return f"""
#     <html>
#     <body>
#         <form action="/api/transactions/{transaction_id}/request_changes" method="post">
#             <p>Approver ID: {approver_id}</p>
#             <input type="hidden" name="approver_id" value="{approver_id}">
#             <textarea name="change_request" rows="4" cols="50" placeholder="Enter your change request here..."></textarea>
#             <button type="submit">Submit Change Request</button>
#         </form>
#     </body>
#     </html>
#     """

# @transaction_bp.route('/<transaction_id>/request_changes', methods=['POST'])
# def request_changes(transaction_id):
#     approver_id = request.form.get("approver_id")
#     change_request = request.form.get("change_request")

#     if not approver_id or not change_request:
#         return jsonify({"error": "Approver ID and change request are required"}), 400

#     transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})

#     if not transaction:
#         return jsonify({"error": "Transaction not found"}), 404

#     approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})
#     if not approver:
#         return jsonify({"error": "Approver not found"}), 404

#     approver_email = approver['email'][0] if isinstance(approver['email'], list) else approver['email']

#     approval_action = {
#         'approved_by': approver_email,
#         'actions_taken': change_request,
#         'approval_action': 'changes_requested',
#         'timestamp': datetime.utcnow()
#     }
#     transaction['approval_actions'].append(approval_action)

#     for approval in transaction['approvals']:
#         if approval['approverId'] == approver_id:
#             approval['status'] = 'changes_requested'

#     current_app.mongo.db.transactions.update_one(
#         {"_id": ObjectId(transaction_id)},
#         {"$set": {
#             "approvals": transaction['approvals'],
#             "approval_actions": transaction['approval_actions'],
#             "updated_at": datetime.utcnow()
#         }}
#     )

#     return jsonify({"message": "Change request submitted", "transaction": str(transaction['_id'])}), 200

# @transaction_bp.route('/<transaction_id>/change_approver_form', methods=['GET'])
# def change_approver_form(transaction_id):
#     approvers = current_app.mongo.db.approvers.find()
#     options = ''.join([f'<option value="{approver["email"]}">{approver["email"]}</option>' for approver in approvers])

#     form_html = f"""
#     <html>
#     <body>
#         <form action="/api/transactions/{transaction_id}/change_approver" method="post">
#             <p>Select new approver email:</p>
#             <select name="new_approver_email">
#                 {options}
#             </select>
#             <button type="submit">Change Approver</button>
#         </form>
#     </body>
#     </html>
#     """
#     return render_template_string(form_html)

# @transaction_bp.route('/<transaction_id>/change_approver', methods=['POST'])
# def change_approver(transaction_id):
#     new_approver_email = request.form.get("new_approver_email")

#     if not new_approver_email:
#         return jsonify({"error": "New approver email is required"}), 400

#     transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})

#     if not transaction:
#         return jsonify({"error": "Transaction not found"}), 404

#     new_approver = current_app.mongo.db.approvers.find_one({"email": new_approver_email})

#     if not new_approver:
#         return jsonify({"error": "New approver not found"}), 404

#     new_approver_id = new_approver['approverId']

#     approval_entry = {
#         'approverId': new_approver_id,
#         'status': 'pending',
#         'email_approver': [new_approver_email],
#     }
#     transaction['approvals'].append(approval_entry)

#     current_app.mongo.db.transactions.update_one(
#         {"_id": ObjectId(transaction_id)},
#         {"$set": {"approvals": transaction['approvals'], "updated_at": datetime.utcnow()}}
#     )

#     send_email_reminder(new_approver_email, transaction_id, new_approver_id, "Change Department", "Process to change Department")

#     return jsonify({"message": "New approver assigned and reminder sent", "transaction": str(transaction['_id'])}), 200




















































































from flask import Blueprint, request, jsonify, current_app, url_for, render_template_string
from bson.objectid import ObjectId
from utils.condition_evaluator import evaluate_condition
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

transaction_bp = Blueprint('transaction_bp', __name__)

@transaction_bp.route('/', methods=['POST'])
def create_transaction():
    data = request.get_json()
    print("Received data:", data)

    process_id = data.get('processId')
    transaction_fields = data.get('transaction_fields', {})
    field_types = data.get('fieldType', [])
    field_values = transaction_fields.get('value', [])
    print(process_id)
    print(transaction_fields)
    print(field_types)
    print(field_values)

    transaction = {
        'processId': process_id,
        'fieldType': field_types,
        'status': 'pending',
        'createdAt': datetime.utcnow(),
        'updatedAt': datetime.utcnow(),
        'approvals': [],
        'approval_actions': []
    }

    approval_rules = current_app.mongo.db.approval_rules.find_one({"processId": process_id})
    print("Approval Rules:", approval_rules)

    if not approval_rules:
        print("No approval rules found for the given process ID")
        return jsonify({"error": "No approval rules found for the given process ID"}), 404

    approvers_set = set()  # To track distinct approvers

    for rule in approval_rules['rules']:
        condition = rule['condition']
        print("Evaluating condition:", condition)

        if evaluate_condition(field_types, field_values, condition):
            print("Condition matched:", condition)
            for approver_id in rule['approvers']:
                if approver_id not in approvers_set:
                    approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})
                    if approver:
                        approval_entry = {
                            'approverId': approver_id,
                            'status': 'pending',
                            'email_approver': approver['email']
                        }
                        transaction['approvals'].append(approval_entry)
                        approvers_set.add(approver_id)
                        print("Approval entry added:", approval_entry)
        else:
            print("Condition did not match:", condition)

    transaction_id = current_app.mongo.db.transactions.insert_one(transaction).inserted_id
    transaction['_id'] = str(transaction_id)  # Convert ObjectId to string

    print("Final transaction:", transaction)
    return jsonify({"message": "Transaction created", "transaction": transaction}), 201

@transaction_bp.route('/reminders', methods=['POST'])
def send_reminders():
    data = request.json
    process_name = data.get("processName")

    if not process_name:
        return jsonify({"error": "Process name not provided"}), 400

    process = current_app.mongo.db.processes.find_one({"name": process_name})

    if not process:
        return jsonify({"error": "Process not found"}), 404

    process_id = process['processId']
    pending_transactions = current_app.mongo.db.transactions.find({"processId": process_id, "status": "pending"})

    pending_count = pending_transactions.count()
    if pending_count == 0:
        return jsonify({"message": "No pending transactions found for the given process"}), 404

    for transaction in pending_transactions:
        for approval in transaction['approvals']:
            if approval['status'] == 'pending':
                approver_id = approval['approverId']
                approver_emails = approval['email_approver']
                
                if not isinstance(approver_emails, list):
                    approver_emails = [approver_emails]

                process_name = process['name']
                process_description = process['description']

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


@transaction_bp.route('/<transaction_id>/update_status/<status>', methods=['GET'])
def update_approval_status(transaction_id, status):
    transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})

    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    approver_id = request.args.get("approver_id")
    if not approver_id:
        return jsonify({"error": "Approver ID not provided"}), 400

    approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})
    if not approver:
        return jsonify({"error": "Approver not found"}), 404

    approver_email = approver['email'][0] if isinstance(approver['email'], list) else approver['email']
    change_request = request.args.get("change_request", "NA")

    approval_action = {
        'approved_by': approver_email,
        'actions_taken': change_request,
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

@transaction_bp.route('/<transaction_id>/request_changes_form', methods=['GET'])
def request_changes_form(transaction_id):
    approver_id = request.args.get("approver_id")
    
    return f"""
    <html>
    <body>
        <form action="/api/transactions/{transaction_id}/request_changes" method="post">
            <p>Approver ID: {approver_id}</p>
            <input type="hidden" name="approver_id" value="{approver_id}">
            <textarea name="change_request" rows="4" cols="50" placeholder="Enter your change request here..."></textarea>
            <button type="submit">Submit Change Request</button>
        </form>
    </body>
    </html>
    """

@transaction_bp.route('/<transaction_id>/request_changes', methods=['POST'])
def request_changes(transaction_id):
    approver_id = request.form.get("approver_id")
    change_request = request.form.get("change_request")

    if not approver_id or not change_request:
        return jsonify({"error": "Approver ID and change request are required"}), 400

    transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})

    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})
    if not approver:
        return jsonify({"error": "Approver not found"}), 404

    approver_email = approver['email'][0] if isinstance(approver['email'], list) else approver['email']

    approval_action = {
        'approved_by': approver_email,
        'actions_taken': change_request,
        'approval_action': 'changes_requested',
        'timestamp': datetime.utcnow()
    }
    transaction['approval_actions'].append(approval_action)

    for approval in transaction['approvals']:
        if approval['approverId'] == approver_id:
            approval['status'] = 'changes_requested'

    current_app.mongo.db.transactions.update_one(
        {"_id": ObjectId(transaction_id)},
        {"$set": {
            "approvals": transaction['approvals'],
            "approval_actions": transaction['approval_actions'],
            "updated_at": datetime.utcnow()
        }}
    )

    return jsonify({"message": "Change request submitted", "transaction": str(transaction['_id'])}), 200

@transaction_bp.route('/<transaction_id>/change_approver_form', methods=['GET'])
def change_approver_form(transaction_id):
    approvers = current_app.mongo.db.approvers.find()
    options = ''.join([f'<option value="{approver["email"]}">{approver["email"]}</option>' for approver in approvers])

    form_html = f"""
    <html>
    <body>
        <form action="/api/transactions/{transaction_id}/change_approver" method="post">
            <p>Select new approver email:</p>
            <select name="new_approver_email">
                {options}
            </select>
            <button type="submit">Change Approver</button>
        </form>
    </body>
    </html>
    """
    return render_template_string(form_html)

@transaction_bp.route('/<transaction_id>/change_approver', methods=['POST'])
def change_approver(transaction_id):
    new_approver_email = request.form.get("new_approver_email")

    if not new_approver_email:
        return jsonify({"error": "New approver email is required"}), 400

    transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})

    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    new_approver = current_app.mongo.db.approvers.find_one({"email": new_approver_email})

    if not new_approver:
        return jsonify({"error": "New approver not found"}), 404

    new_approver_id = new_approver['approverId']

    approval_entry = {
        'approverId': new_approver_id,
        'status': 'pending',
        'email_approver': [new_approver_email],
    }
    transaction['approvals'].append(approval_entry)

    current_app.mongo.db.transactions.update_one(
        {"_id": ObjectId(transaction_id)},
        {"$set": {"approvals": transaction['approvals'], "updated_at": datetime.utcnow()}}
    )

    send_email_reminder(new_approver_email, transaction_id, new_approver_id, "Change Department", "Process to change Department")

    return jsonify({"message": "New approver assigned and reminder sent", "transaction": str(transaction['_id'])}), 200































