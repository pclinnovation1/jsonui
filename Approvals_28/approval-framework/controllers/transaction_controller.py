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















# from flask import Blueprint, request, jsonify, current_app, url_for
# from bson.objectid import ObjectId
# from utils.condition_evaluator import evaluate_condition
# from datetime import datetime

# transaction_bp = Blueprint('transaction', __name__)

# @transaction_bp.route('/transactions', methods=['POST'])
# def create_transaction():
#     data = request.get_json()
#     print("Received data:", data)
    
#     process_id = data.get('processId')
#     transaction_fields = data.get('transaction_fields', {})
#     field_type = data.get('fieldType')
#     field_value = transaction_fields.get(field_type) 

#     print("Process ID:", process_id)
#     print("Transaction Fields:", transaction_fields)
#     print("Field Type:", field_type)
#     print("Field Value:", field_value)

#     transaction = {
#         'processId': process_id,
#         'amount': transaction_fields.get('amount'),
#         'fieldType': field_type,
#         'status': 'pending',
#         'createdAt': datetime.utcnow(),
#         'updatedAt': datetime.utcnow(),
#         'approvals': []
#     }

#     approval_rules = current_app.mongo.db.approval_rules.find_one({"processId": process_id})
#     print("Approval Rules:", approval_rules)

#     if not approval_rules:
#         print("No approval rules found for the given process ID")
#         return jsonify({"error": "No approval rules found for the given process ID"}), 404

#     for rule in approval_rules['rules']:
#         condition_id = rule['conditionId']
#         print("Evaluating rule with condition ID:", condition_id)

#         condition = current_app.mongo.db.conditions.find_one({"conditionId": str(condition_id)})
#         print("Condition:", condition)

#         if condition and evaluate_condition(field_value, condition):
#             print("Condition matched:", condition)
#             for approver_id in rule['approvers']:
#                 approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})
#                 if approver:
#                     approval_entry = {
#                         'approverId': approver_id,
#                         'status': 'pending',
#                         'lastUpdatedAt': datetime.utcnow(),
#                         'email': approver['email']
#                     }
#                     transaction['approvals'].append(approval_entry)
#                     print("Approval entry added:", approval_entry)
#             break  # Stop after finding the first matching rule
#         else:
#             print("Condition did not match:", condition)

#     transaction_id = current_app.mongo.db.transactions.insert_one(transaction).inserted_id
#     transaction['_id'] = str(transaction_id)  # Convert ObjectId to string

#     print("Final transaction:", transaction)
#     return jsonify({"message": "Transaction created", "transaction": transaction}), 201

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
























# from flask import Blueprint, request, jsonify, current_app
# from bson.objectid import ObjectId
# from datetime import datetime
# from utils.condition_evaluator import evaluate_condition

# transaction_bp = Blueprint('transactions', __name__)

# @transaction_bp.route('/transactions', methods=['POST'])
# def create_transaction():
#     data = request.get_json()
#     process_id = data.get('processId')
#     transaction = {
#         "processId": process_id,
#         "amount": data.get('amount'),
#         "department": data.get('department'),
#         "cost_center": data.get('cost_center'),
#         "status": "pending",
#         "approvals": [],
#         "createdAt": datetime.utcnow(),
#         "updatedAt": datetime.utcnow()
#     }
#     transaction_id = current_app.mongo.db.transactions.insert_one(transaction).inserted_id

#     # Fetch approval rules for the given process
#     approval_rules = current_app.mongo.db.approval_rules.find_one({"processId": process_id})

#     if approval_rules:
#         for rule in approval_rules.get('rules', []):
#             condition_id = rule.get('condition')
#             condition = current_app.mongo.db.conditions.find_one({"_id": ObjectId(condition_id)})
            
#             if condition and evaluate_condition(transaction, condition):
#                 for approver_id in rule.get('approvers', []):
#                     transaction['approvals'].append({
#                         "approverId": approver_id,
#                         "status": "pending"
#                     })
#                 # Auto-approve if action is auto_approve
#                 if rule.get('action') == 'auto_approve':
#                     transaction['status'] = 'approved'
#                     for approval in transaction['approvals']:
#                         approval['status'] = 'approved'
#                 break  # Assume only one rule applies

#     # Update transaction with approvals
#     current_app.mongo.db.transactions.update_one(
#         {"_id": transaction_id},
#         {"$set": {"approvals": transaction['approvals'], "status": transaction['status']}}
#     )

#     return jsonify({"message": "Transaction created", "transaction": transaction}), 201









# # controllers/transaction_controller.py
# from flask import Blueprint, request, jsonify, current_app
# from bson.objectid import ObjectId
# from utils.condition_evaluator import evaluate_condition
# from datetime import datetime

# transaction_bp = Blueprint('transaction', __name__)

# @transaction_bp.route('/transactions', methods=['POST'])
# def create_transaction():
#     data = request.get_json()
#     print("Received data:", data)
    
#     process_id = data.get('processId')
#     transaction_fields = data.get('transaction_fields', {})
#     field_type = data.get('fieldType')
#     field_value = transaction_fields.get(field_type)

#     print("Process ID:", process_id)
#     print("Transaction Fields:", transaction_fields)
#     print("Field Type:", field_type)
#     print("Field Value:", field_value)

#     transaction = {
#         'processId': process_id,
#         'amount': transaction_fields.get('amount'),
#         'fieldType': field_type,
#         'status': 'pending',
#         'createdAt': datetime.utcnow(),
#         'updatedAt': datetime.utcnow(),
#         'approvals': []
#     }

#     approval_rules = current_app.mongo.db.approval_rules.find_one({"processId": process_id})
#     print("Approval Rules:", approval_rules)

#     if not approval_rules:
#         print("No approval rules found for the given process ID")
#         return jsonify({"error": "No approval rules found for the given process ID"}), 404

#     for rule in approval_rules['rules']:
#         condition_id = rule['conditionId']
#         print("Evaluating rule with condition ID:", condition_id)

#         condition = current_app.mongo.db.conditions.find_one({"conditionId": str(condition_id)})
#         print("Condition:", condition)

#         if condition and evaluate_condition(field_value, condition):
#             print("Condition matched:", condition)
#             transaction['approvals'].extend(rule['approvers'])
#             print("Approvals added:", rule['approvers'])
#             break  # Stop after finding the first matching rule
#         else:
#             print("Condition did not match:", condition)

#     transaction_id = current_app.mongo.db.transactions.insert_one(transaction).inserted_id
#     transaction['_id'] = str(transaction_id)  # Convert ObjectId to string

#     print("Final transaction:", transaction)

#     return jsonify({"message": "Transaction created", "transaction": transaction}), 201



























# from flask import Blueprint, request, jsonify, current_app, url_for
# from bson.objectid import ObjectId
# from utils.condition_evaluator import evaluate_condition
# from datetime import datetime
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# transaction_bp = Blueprint('transaction', __name__)

# @transaction_bp.route('/transactions', methods=['POST'])
# def create_transaction():
#     data = request.get_json()
#     print("Received data:", data)
    
#     process_id = data.get('processId')
#     transaction_fields = data.get('transaction_fields', {})
#     field_type = data.get('fieldType')
#     field_value = transaction_fields.get(field_type) 

#     print("Process ID:", process_id)
#     print("Transaction Fields:", transaction_fields)
#     print("Field Type:", field_type)
#     print("Field Value:", field_value)

#     transaction = {
#         'processId': process_id,
#         'amount': transaction_fields.get('amount'),
#         'fieldType': field_type,
#         'status': 'pending',
#         'createdAt': datetime.utcnow(),
#         'updatedAt': datetime.utcnow(),
#         'approvals': []
#     }

#     approval_rules = current_app.mongo.db.approval_rules.find_one({"processId": process_id})
#     print("Approval Rules:", approval_rules)

#     if not approval_rules:
#         print("No approval rules found for the given process ID")
#         return jsonify({"error": "No approval rules found for the given process ID"}), 404

#     for rule in approval_rules['rules']:
#         condition_id = rule['conditionId']
#         print("Evaluating rule with condition ID:", condition_id)

#         condition = current_app.mongo.db.conditions.find_one({"conditionId": str(condition_id)})
#         print("Condition:", condition)

#         if condition and evaluate_condition(field_value, condition):
#             print("Condition matched:", condition)
#             for approver_id in rule['approvers']:
#                 approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})
#                 if approver:
#                     approval_entry = {
#                         'approverId': approver_id,
#                         'status': 'pending',
#                        # 'lastUpdatedAt': datetime.utcnow(),
#                        # 'email': approver['email']
#                     }
#                     transaction['approvals'].append(approval_entry)
#                     print("Approval entry added:", approval_entry)
#             break  # Stop after finding the first matching rule
#         else:
#             print("Condition did not match:", condition)

#     transaction_id = current_app.mongo.db.transactions.insert_one(transaction).inserted_id
#     transaction['_id'] = str(transaction_id)  # Convert ObjectId to string

#     print("Final transaction:", transaction)
#     return jsonify({"message": "Transaction created", "transaction": transaction}), 201

# @transaction_bp.route('/transactions/reminders', methods=['POST'])
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
#                 approval['reminder_sent_at'] = datetime.utcnow()
#                 approval['reminder_sent_to'] = approver_emails  # Store all emails

#             current_app.mongo.db.transactions.update_one(
#                 {"_id": ObjectId(transaction_id)},
#                 {"$set": {"approvals": transaction['approvals'], "updated_at": datetime.utcnow()}}
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

# @transaction_bp.route('/transactions/<transaction_id>/update_status/<status>', methods=['GET'])
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
#             approval['timestamp'] = datetime.utcnow()
#             break

#     current_app.mongo.db.transactions.update_one(
#         {"_id": ObjectId(transaction_id)},
#         {"$set": {"approvals": transaction['approvals'], "updated_at": datetime.utcnow()}}
#     )

#     return jsonify({"message": "Approval status updated", "transaction": str(transaction['_id'])}), 200






















# from flask import Blueprint, request, jsonify, current_app, url_for
# from bson.objectid import ObjectId
# from utils.condition_evaluator import evaluate_condition
# from datetime import datetime
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# transaction_bp = Blueprint('transaction', __name__)

# @transaction_bp.route('/transactions', methods=['POST'])
# def create_transaction():
#     data = request.get_json()
#     print("Received data:", data)
    
#     process_id = data.get('processId')
#     transaction_fields = data.get('transaction_fields', {})
#     field_type = data.get('fieldType')
#     field_value = transaction_fields.get(field_type) 

#     print("Process ID:", process_id)
#     print("Transaction Fields:", transaction_fields)
#     print("Field Type:", field_type)
#     print("Field Value:", field_value)

#     transaction = {
#         'processId': process_id,
#         'amount': transaction_fields.get('amount'),
#         'fieldType': field_type,
#         'status': 'pending',
#         'createdAt': datetime.utcnow(),
#         'updatedAt': datetime.utcnow(),
#         'approvals': []
#     }

#     approval_rules = current_app.mongo.db.approval_rules.find_one({"processId": process_id})
#     print("Approval Rules:", approval_rules)

#     if not approval_rules:
#         print("No approval rules found for the given process ID")
#         return jsonify({"error": "No approval rules found for the given process ID"}), 404

#     for rule in approval_rules['rules']:
#         condition_id = rule['conditionId']
#         print("Evaluating rule with condition ID:", condition_id)

#         condition = current_app.mongo.db.conditions.find_one({"conditionId": str(condition_id)})
#         print("Condition:", condition)

#         if condition and evaluate_condition(field_value, condition):
#             print("Condition matched:", condition)
#             for approver_id in rule['approvers']:
#                 approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})
#                 if approver:
#                     approval_entry = {
#                         'approverId': approver_id,
#                         'status': 'pending',
#                        # 'lastUpdatedAt': datetime.utcnow(),
#                         #'email': approver['email']
#                     }
#                     transaction['approvals'].append(approval_entry)
#                     print("Approval entry added:", approval_entry)
#             break  # Stop after finding the first matching rule
#         else:
#             print("Condition did not match:", condition)

#     transaction_id = current_app.mongo.db.transactions.insert_one(transaction).inserted_id
#     transaction['_id'] = str(transaction_id)  # Convert ObjectId to string

#     print("Final transaction:", transaction)
#     return jsonify({"message": "Transaction created", "transaction": transaction}), 201

# @transaction_bp.route('/transactions/reminders', methods=['POST'])
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
#                 approval['reminder_sent_at'] = datetime.utcnow()
#                 approval['reminder_sent_to'] = approver_emails  # Store all emails

#             current_app.mongo.db.transactions.update_one(
#                 {"_id": ObjectId(transaction_id)},
#                 {"$set": {"approvals": transaction['approvals'], "updated_at": datetime.utcnow()}}
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

# @transaction_bp.route('/transactions/<transaction_id>/update_status/<status>', methods=['GET'])
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
#             approval['timestamp'] = datetime.utcnow()
#             break

#     # Check if all approvals are done
#     all_approved = all(approval['status'] == 'approved' for approval in transaction['approvals'])

#     update_data = {
#         "approvals": transaction['approvals'],
#         "updated_at": datetime.utcnow()
#     }
    
#     if all_approved:
#         update_data["status"] = "approved"

#     current_app.mongo.db.transactions.update_one(
#         {"_id": ObjectId(transaction_id)},
#         {"$set": update_data}
#     )

#     return jsonify({"message": "Approval status updated", "transaction": str(transaction['_id'])}), 200














from flask import Blueprint, request, jsonify, current_app, url_for
from bson.objectid import ObjectId
from utils.condition_evaluator import evaluate_condition
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/transactions', methods=['POST'])
def create_transaction():
    data = request.get_json()
    print("Received data:", data)
    
    process_id = data.get('processId')
    transaction_fields = data.get('transaction_fields', {})
    field_type = data.get('fieldType')
    field_value = transaction_fields.get(field_type) 

    print("Process ID:", process_id)
    print("Transaction Fields:", transaction_fields)
    print("Field Type:", field_type)
    print("Field Value:", field_value)

    transaction = {
        'processId': process_id,
        'amount': transaction_fields.get('amount'),
        'fieldType': field_type,
        'status': 'pending',
        'createdAt': datetime.utcnow(),
        'updatedAt': datetime.utcnow(),
        'approvals': []
    }

    approval_rules = current_app.mongo.db.approval_rules.find_one({"processId": process_id})
    print("Approval Rules:", approval_rules)

    if not approval_rules:
        print("No approval rules found for the given process ID")
        return jsonify({"error": "No approval rules found for the given process ID"}), 404

    for rule in approval_rules['rules']:
        condition_id = rule['conditionId']
        print("Evaluating rule with condition ID:", condition_id)

        condition = current_app.mongo.db.conditions.find_one({"conditionId": str(condition_id)})
        print("Condition:", condition)

        if condition and evaluate_condition(field_value, condition):
            print("Condition matched:", condition)
            for approver_id in rule['approvers']:
                approver = current_app.mongo.db.approvers.find_one({"approverId": approver_id})
                if approver:
                    approval_entry = {
                        'approverId': approver_id,
                        'status': 'pending',
                        #'lastUpdatedAt': datetime.utcnow(),
                        'Action Type': approver['Action Type']
                    }
                    transaction['approvals'].append(approval_entry)
                    print("Approval entry added:", approval_entry)
            break  # Stop after finding the first matching rule
        else:
            print("Condition did not match:", condition)

    transaction_id = current_app.mongo.db.transactions.insert_one(transaction).inserted_id
    transaction['_id'] = str(transaction_id)  # Convert ObjectId to string

    print("Final transaction:", transaction)
    return jsonify({"message": "Transaction created", "transaction": transaction}), 201

@transaction_bp.route('/transactions/reminders', methods=['POST'])
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
                approval['reminder_sent_at'] = datetime.utcnow()
                approval['reminder_sent_to'] = approver_emails  # Store all emails

            current_app.mongo.db.transactions.update_one(
                {"_id": ObjectId(transaction_id)},
                {"$set": {"approvals": transaction['approvals'], "updated_at": datetime.utcnow()}}
            )
            return jsonify({"message": "Reminder sent to the first pending approver"}), 200

    return jsonify({"message": "No pending approvals found"}), 404

def send_email_reminder(approver_email, transaction_id, approver_id, process_name, process_description):
    from_email = "piyushbirkh@gmail.com"
    password = "teaz yfbj jcie twrt"  # Use an app password if 2FA is enabled

    to_email = approver_email
    subject = "Approval Reminder"
    approve_url = url_for('transaction.update_approval_status', transaction_id=transaction_id, status='approved', approver_id=approver_id, _external=True)
    reject_url = url_for('transaction.update_approval_status', transaction_id=transaction_id, status='rejected', approver_id=approver_id, _external=True)
    changes_url = url_for('transaction.update_approval_status', transaction_id=transaction_id, status='changes_requested', approver_id=approver_id, _external=True)

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

@transaction_bp.route('/transactions/<transaction_id>/update_status/<status>', methods=['GET'])
def update_approval_status(transaction_id, status):
    transaction = current_app.mongo.db.transactions.find_one({"_id": ObjectId(transaction_id)})

    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    approver_id = request.args.get("approver_id")
    if not approver_id:
        return jsonify({"error": "Approver ID not provided"}), 400

    for approval in transaction['approvals']:
        if approval['approverId'] == approver_id:
            approval['status'] = status
            approval['timestamp'] = datetime.utcnow()
            break

    # Check if all approvals are done
    all_approved = all(approval['status'] == 'approved' for approval in transaction['approvals'])

    update_data = {
        "approvals": transaction['approvals'],
        "updated_at": datetime.utcnow()
    }
    
    if all_approved:
        update_data["status"] = "approved"

    current_app.mongo.db.transactions.update_one(
        {"_id": ObjectId(transaction_id)},
        {"$set": update_data}
    )

    return jsonify({"message": "Approval status updated", "transaction": str(transaction['_id'])}), 200
