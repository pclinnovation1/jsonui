# # client = MongoClient(config.MONGODB_URI)
# # db = client[config.DATABASE_NAME]
# # assigned_performance_collection = db['P_assigned_performance']
# # employee_details_collection = db['s_employeedetails_2'] 


# from flask import Blueprint, request, jsonify, render_template, url_for
# from pymongo import MongoClient
# import config
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from bson import ObjectId
# import os

# # Define the Blueprint
# notify_performance_bp = Blueprint('notify_performance_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# assigned_performance_collection = db['P_assigned_performance']
# employee_details_collection = db['s_employeedetails_2']  # Assuming this is the collection where employee details are stored

# # Function to load email template from a file
# def load_template(template_name):
#     template_path = os.path.join('templates', template_name)
#     print(f"Loading template from: {template_path}")  # Debugging line
#     with open(template_path, 'r') as template_file:
#         return template_file.read()


# # Function to send email
# def send_email(to_address, subject, body):
#     smtp_config = config.SMTP_CONFIG
#     msg = MIMEMultipart()
#     msg['From'] = smtp_config['username']
#     msg['To'] = to_address
#     msg['Subject'] = subject

#     msg.attach(MIMEText(body, 'plain'))

#     try:
#         server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
#         server.starttls()
#         server.login(smtp_config['username'], smtp_config['password'])
#         text = msg.as_string()
#         server.sendmail(smtp_config['username'], to_address, text)
#         server.quit()
#         print(f"Email sent to {to_address}")
#     except Exception as e:
#         print(f"Failed to send email to {to_address}: {e}")

# # Route to serve employee feedback form
# # Route to serve employee feedback form
# @notify_performance_bp.route('/employee_feedback/<form_id>', methods=['GET'])
# def employee_feedback_form(form_id):
#     performance_document = assigned_performance_collection.find_one({"_id": ObjectId(form_id)})

#     if not performance_document:
#         return "Form not found", 404

#     competencies = performance_document.get("competencies", [])
#     feedbacks = performance_document.get("feedbacks", {})
#     employee_name = performance_document.get("employee_name", "")

#     return render_template('employee_feedback_form.html', competencies=competencies, feedbacks=feedbacks, employee_name=employee_name, form_id=form_id)

# # Route to submit employee feedback
# @notify_performance_bp.route('/submit_employee_feedback/<form_id>', methods=['POST'])
# def submit_employee_feedback(form_id):
#     performance_document = assigned_performance_collection.find_one({"_id": ObjectId(form_id)})

#     if not performance_document:
#         return "Form not found", 404

#     # Debugging: print the form data
#     print("Form Data:", request.form)

#     # Update competencies
#     for key, value in request.form.items():
#         if key.startswith('competencies'):
#             comp_id = key.split('[')[1].split(']')[0]
#             employee_rating = value

#             print(f"Updating competency {comp_id} with employee rating {employee_rating}")
            
#             # Update the MongoDB document
#             assigned_performance_collection.update_one(
#                 {"_id": ObjectId(form_id), "competencies._id": ObjectId(comp_id)},
#                 {"$set": {"competencies.$.employee_rating": employee_rating}}
#             )

#     # Update feedbacks
#     for key, value in request.form.items():
#         if key.startswith('feedbacks'):
#             q_id = key.split('[')[1].split(']')[0]
#             employee_feedback = value

#             if ObjectId.is_valid(q_id):
#                 print(f"Updating feedback question {q_id} with employee feedback {employee_feedback}")
                
#                 # Update the MongoDB document
#                 assigned_performance_collection.update_one(
#                     {"_id": ObjectId(form_id), "feedbacks.questions._id": ObjectId(q_id)},
#                     {"$set": {"feedbacks.questions.$.employee_feedback": employee_feedback}}
#                 )
#             else:
#                 print(f"Invalid Question ID: {q_id}")

#     # Update overall summary
#     overall_summary_rating = request.form.get('overall_summary[employee_actual_rating]')
#     overall_summary_comments = request.form.get('overall_summary[employee_comments]')
#     print(f"Updating overall summary with rating {overall_summary_rating} and comments {overall_summary_comments}")
    
#     assigned_performance_collection.update_one(
#         {"_id": ObjectId(form_id)},
#         {"$set": {
#             "overall_summary_and_ratings.employee_actual_rating.rating": overall_summary_rating,
#             "overall_summary_and_ratings.employee_actual_rating.comments": overall_summary_comments
#         }}
#     )

#     return "Thank you for submitting your feedback!"

# # Route to send feedback form email to employee by name
# @notify_performance_bp.route('/send_feedback_form', methods=['POST'])
# def send_feedback_form():
#     data = request.json
#     performance_document_name = data.get('performance_document_name')
#     employee_name = data.get('employee_name')

#     if not performance_document_name or not employee_name:
#         return jsonify({"error": "Missing required parameters"}), 400

#     # Split employee_name into first_name and last_name
#     try:
#         first_name, last_name = employee_name.split(' ', 1)
#     except ValueError:
#         return jsonify({"error": "Invalid employee name format"}), 400

#     # Retrieve the employee's email from s_employeedetails_2 collection
#     employee_record = employee_details_collection.find_one({
#         "first_name": {"$regex": f"^{first_name}$", "$options": "i"},
#         "last_name": {"$regex": f"^{last_name}$", "$options": "i"}
#     })

#     if not employee_record:
#         return jsonify({"error": "Employee not found"}), 404

#     employee_email = employee_record.get('email')

#     if not employee_email:
#         return jsonify({"error": "Employee email not found"}), 404

#     # Retrieve the performance document by name
#     performance_document = assigned_performance_collection.find_one({
#         "performance_document_name": performance_document_name,
#         "employee_name": employee_name
#     })

#     if not performance_document:
#         return jsonify({"error": "Performance document not found"}), 404

#     # Generate the feedback form link
#     feedback_form_link = url_for('notify_performance_bp.employee_feedback_form', form_id=performance_document['_id'], _external=True)

#     # Load the email template
#     body_template = load_template('employee_feedback_email.txt')

#     # Prepare email subject and body
#     subject = f"Feedback Request for {employee_name}"
#     body = body_template.format(
#         employee_name=employee_name,
#         feedback_form_link=feedback_form_link
#     )

#     # Send the email
#     send_email(employee_email, subject, body)

#     return jsonify({"message": "Feedback form email sent successfully"}), 200




































































# from flask import Blueprint, request, jsonify, render_template, url_for
# from pymongo import MongoClient
# import config
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from bson import ObjectId
# import os
# from bson import ObjectId, errors

# # Define the Blueprint
# notify_performance_bp = Blueprint('notify_performance_bp', __name__)

# # MongoDB client setup
# client = MongoClient(config.MONGODB_URI)
# db = client[config.DATABASE_NAME]
# assigned_performance_collection = db['P_assigned_performance']
# employee_details_collection = db['s_employeedetails_2']  # Assuming this is the collection where employee details are stored

# # Function to load email template from a file
# def load_template(template_name):
#     template_path = os.path.join('templates', template_name)
#     print(f"Loading template from: {template_path}")  # Debugging line
#     with open(template_path, 'r') as template_file:
#         return template_file.read()

# # Function to send email
# def send_email(to_address, subject, body):
#     smtp_config = config.SMTP_CONFIG
#     msg = MIMEMultipart()
#     msg['From'] = smtp_config['username']
#     msg['To'] = to_address
#     msg['Subject'] = subject

#     msg.attach(MIMEText(body, 'plain'))

#     try:
#         server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
#         server.starttls()
#         server.login(smtp_config['username'], smtp_config['password'])
#         text = msg.as_string()
#         server.sendmail(smtp_config['username'], to_address, text)
#         server.quit()
#         print(f"Email sent to {to_address}")
#     except Exception as e:
#         print(f"Failed to send email to {to_address}: {e}")

# @notify_performance_bp.route('/employee_feedback/<form_id>', methods=['GET', 'POST'])
# def employee_feedback_form(form_id):
#     performance_document = assigned_performance_collection.find_one({"_id": ObjectId(form_id)})

#     if not performance_document:
#         return "Form not found", 404

#     if request.method == 'POST':
#         # Print all form keys and values to check if 'goals' keys are present
#         print("Form data received:")
#         for key, value in request.form.items():
#             print(f"Key: {key}, Value: {value}")

#         # Update competencies
#         for key, value in request.form.items():
#             if key.startswith('competencies'):
#                 comp_id = key.split('[')[1].split(']')[0]
#                 employee_rating = int(value)

#                 update_result = assigned_performance_collection.update_one(
#                     {"_id": ObjectId(form_id), "competencies._id": ObjectId(comp_id)},
#                     {"$set": {"competencies.$.employee_rating": employee_rating}}
#                 )
#                 if update_result.modified_count == 0:
#                     update_result = assigned_performance_collection.update_one(
#                         {"_id": ObjectId(form_id), "competencies._id": comp_id},
#                         {"$set": {"competencies.$.employee_rating": employee_rating}}
#                     )

#         # Update feedbacks
#         for key, value in request.form.items():
#             if key.startswith('feedbacks'):
#                 question_name = key.split('[')[1].split(']')[0]
#                 employee_feedback = value

#                 update_result = assigned_performance_collection.update_one(
#                     {"_id": ObjectId(form_id), "feedbacks.questions.question_name": question_name},
#                     {"$set": {"feedbacks.questions.$.employee_feedback": employee_feedback}}
#                 )

#         # Update goals
#         print("Starting to process goals...")
#         for key, value in request.form.items():
#             if key.startswith('goals'):
#                 try:
#                     goal_name = key.split('[')[1].split(']')[0]
#                     employee_rating = int(value)

#                     print(f"Processing goal: {goal_name} with employee rating: {employee_rating}")

#                     # Print the full goals list to verify structure
#                     print(f"Goals in document before update: {performance_document['goals']}")

#                     # First, let's find the correct goal object using the goal name
#                     goal_obj = next((g for g in performance_document['goals'] if g['goal_name'].strip() == goal_name.strip()), None)

#                     if goal_obj:
#                         print(f"Found matching goal object: {goal_obj}")
#                         update_result = assigned_performance_collection.update_one(
#                             {"_id": ObjectId(form_id), "goals.goal_name": goal_name.strip()},
#                             {"$set": {"goals.$.employee_rating": employee_rating}}
#                         )
#                         print(f"Update result for goal '{goal_name}': {update_result.modified_count} document(s) updated")
#                         if update_result.modified_count == 0:
#                             print(f"No match found for goal: {goal_name}")
#                         else:
#                             print(f"Goal update successful for: {goal_name}")
#                     else:
#                         print(f"Goal name not found in document: {goal_name}")

#                 except Exception as e:
#                     print(f"Error updating goal: {goal_name}, Error: {str(e)}")

#         # Update overall summary
#         overall_summary_rating = int(request.form.get('overall_summary[employee_actual_rating]'))
#         overall_summary_comments = request.form.get('overall_summary[employee_comments]')
#         print(f"Updating overall summary with rating {overall_summary_rating} and comments {overall_summary_comments}")

#         update_result = assigned_performance_collection.update_one(
#             {"_id": ObjectId(form_id)},
#             {"$set": {
#                 "overall_summary_and_ratings.employee_actual_rating.rating": overall_summary_rating,
#                 "overall_summary_and_ratings.employee_actual_rating.comments": overall_summary_comments
#             }}
#         )
#         print(f"Update result for overall summary: {update_result.modified_count} document(s) updated")

#         return "Thank you for submitting your feedback!"

#     # If GET request, render the form
#     competencies = performance_document.get("competencies", [])
#     feedbacks = performance_document.get("feedbacks", {})
#     goals = performance_document.get("goals", [])
#     employee_name = performance_document.get("employee_name", "")

#     return render_template('employee_feedback_form.html', 
#                            competencies=competencies, 
#                            feedbacks=feedbacks, 
#                            goals=goals,
#                            employee_name=employee_name, 
#                            form_id=form_id)


# @notify_performance_bp.route('/submit_employee_feedback/<form_id>', methods=['POST'])
# def submit_employee_feedback(form_id):
#     performance_document = assigned_performance_collection.find_one({"_id": ObjectId(form_id)})

#     if not performance_document:
#         return "Form not found", 404

#     # Print the document before the update
#     print(f"Document before update: {performance_document}")

#     for key, value in request.form.items():
#         if key.startswith('competencies'):
#             comp_id = key.split('[')[1].split(']')[0]
#             employee_rating = int(value)

#             print(f"Competency ID: {comp_id}, Type: {type(comp_id)}")
#             print(f"Employee Rating: {employee_rating}, Type: {type(employee_rating)}")

#             # Attempt to update using ObjectId first
#             try:
#                 comp_id_obj = ObjectId(comp_id)
#             except errors.InvalidId:
#                 comp_id_obj = comp_id  # If conversion fails, keep as string

#             # Try updating with ObjectId
#             update_result = assigned_performance_collection.update_one(
#                 {"_id": ObjectId(form_id), "competencies._id": comp_id_obj},
#                 {"$set": {"competencies.$.employee_rating": employee_rating}}
#             )
#             print(f"Competency update result with ObjectId: {update_result.modified_count} document(s) updated")

#             # If ObjectId fails, try updating with string ID
#             if update_result.modified_count == 0:
#                 update_result = assigned_performance_collection.update_one(
#                     {"_id": ObjectId(form_id), "competencies._id": comp_id},
#                     {"$set": {"competencies.$.employee_rating": employee_rating}}
#                 )
#                 print(f"Competency update result with string ID: {update_result.modified_count} document(s) updated")

#     # Update feedbacks using question_name as the identifier
#     for key, value in request.form.items():
#         if key.startswith('feedbacks'):
#             try:
#                 # Extract question_name from the form key
#                 question_name = key.split('[')[1].split(']')[0]
#                 employee_feedback = value

#                 # Log the question name and feedback
#                 print(f"Updating feedback for question: {question_name} with feedback: {employee_feedback}")

#                 # Use the question_name to identify the correct question to update
#                 update_result = assigned_performance_collection.update_one(
#                     {
#                         "_id": ObjectId(form_id),
#                         "feedbacks.questions.question_name": question_name
#                     },
#                     {"$set": {"feedbacks.questions.$.employee_feedback": employee_feedback}}
#                 )
#                 print(f"Feedback update result: {update_result.modified_count} document(s) updated")

#                 if update_result.modified_count == 0:
#                     print(f"No match found for question: {question_name}")
#             except IndexError as e:
#                 print(f"Error parsing question name from key: {key}, Error: {str(e)}")

#     # Update overall summary
#     overall_summary_rating = int(request.form.get('overall_summary[employee_actual_rating]'))
#     overall_summary_comments = request.form.get('overall_summary[employee_comments]')
#     print(f"Updating overall summary with rating {overall_summary_rating} and comments {overall_summary_comments}")
    
#     update_result = assigned_performance_collection.update_one(
#         {"_id": ObjectId(form_id)},
#         {"$set": {
#             "overall_summary_and_ratings.employee_actual_rating.rating": overall_summary_rating,
#             "overall_summary_and_ratings.employee_actual_rating.comments": overall_summary_comments
#         }}
#     )
#     print(f"Update result: {update_result.modified_count} document(s) updated")

#     # Print the document after the update
#     updated_document = assigned_performance_collection.find_one({"_id": ObjectId(form_id)})
#     print(f"Document after update: {updated_document}")

#     return "Thank you for submitting your feedback!"


# # Route to send feedback form email to employee by name
# @notify_performance_bp.route('/send_feedback_form', methods=['POST'])
# def send_feedback_form():
#     data = request.json
#     performance_document_name = data.get('performance_document_name')
#     employee_name = data.get('employee_name')

#     if not performance_document_name or not employee_name:
#         return jsonify({"error": "Missing required parameters"}), 400

#     # Split employee_name into first_name and last_name
#     try:
#         first_name, last_name = employee_name.split(' ', 1)
#     except ValueError:
#         return jsonify({"error": "Invalid employee name format"}), 400

#     # Retrieve the employee's email from s_employeedetails_2 collection
#     employee_record = employee_details_collection.find_one({
#         "first_name": {"$regex": f"^{first_name}$", "$options": "i"},
#         "last_name": {"$regex": f"^{last_name}$", "$options": "i"}
#     })

#     if not employee_record:
#         return jsonify({"error": "Employee not found"}), 404

#     employee_email = employee_record.get('email')

#     if not employee_email:
#         return jsonify({"error": "Employee email not found"}), 404

#     # Retrieve the performance document by name
#     performance_document = assigned_performance_collection.find_one({
#         "performance_document_name": performance_document_name,
#         "employee_name": employee_name
#     })

#     if not performance_document:
#         return jsonify({"error": "Performance document not found"}), 404

#     # Generate the feedback form link
#     feedback_form_link = url_for('notify_performance_bp.employee_feedback_form', form_id=performance_document['_id'], _external=True)

#     # Load the email template
#     body_template = load_template('employee_feedback_email.txt')

#     # Prepare email subject and body
#     subject = f"Feedback Request for {employee_name}"
#     body = body_template.format(
#         employee_name=employee_name,
#         feedback_form_link=feedback_form_link
#     )

#     # Send the email
#     send_email(employee_email, subject, body)

#     return jsonify({"message": "Feedback form email sent successfully"}), 200


























































from flask import Blueprint, request, jsonify, render_template, url_for
from pymongo import MongoClient
import config
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bson import ObjectId, errors
import os

# Define the Blueprint
notify_performance_bp = Blueprint('notify_performance_bp', __name__)

# MongoDB client setup
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
assigned_performance_collection = db['P_assigned_performance']
employee_details_collection = db['s_employeedetails_2']  # Assuming this is the collection where employee details are stored

# Function to load email template from a file
def load_template(template_name):
    template_path = os.path.join('templates', template_name)
    print(f"Loading template from: {template_path}")  # Debugging line
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

@notify_performance_bp.route('/employee_feedback/<form_id>', methods=['GET', 'POST'])
def employee_feedback_form(form_id):
    performance_document = assigned_performance_collection.find_one({"_id": ObjectId(form_id)})

    if not performance_document:
        return "Form not found", 404

    if request.method == 'POST':
        # Print all form keys and values to check if 'goals' keys are present
        print("Form data received:")
        for key, value in request.form.items():
            print(f"Key: {key}, Value: {value}")

        # Update competencies
        for key, value in request.form.items():
            if key.startswith('competencies'):
                comp_id = key.split('[')[1].split(']')[0]
                employee_rating = int(value)

                update_result = assigned_performance_collection.update_one(
                    {"_id": ObjectId(form_id), "competencies._id": ObjectId(comp_id)},
                    {"$set": {"competencies.$.employee_rating": employee_rating}}
                )
                if update_result.modified_count == 0:
                    update_result = assigned_performance_collection.update_one(
                        {"_id": ObjectId(form_id), "competencies._id": comp_id},
                        {"$set": {"competencies.$.employee_rating": employee_rating}}
                    )

        # Update feedbacks
        for key, value in request.form.items():
            if key.startswith('feedbacks'):
                question_name = key.split('[')[1].split(']')[0]
                employee_feedback = value

                update_result = assigned_performance_collection.update_one(
                    {"_id": ObjectId(form_id), "feedbacks.questions.question_name": question_name},
                    {"$set": {"feedbacks.questions.$.employee_feedback": employee_feedback}}
                )

        # Update goals
        print("Starting to process goals...")
        for key, value in request.form.items():
            if key.startswith('goals'):
                try:
                    goal_name = key.split('[')[1].split(']')[0]
                    employee_rating = int(value)

                    print(f"Processing goal: {goal_name} with employee rating: {employee_rating}")

                    # Print the full goals list to verify structure
                    print(f"Goals in document before update: {performance_document['goals']}")

                    # First, let's find the correct goal object using the goal name
                    goal_obj = next((g for g in performance_document['goals'] if g['goal_name'].strip() == goal_name.strip()), None)

                    if goal_obj:
                        print(f"Found matching goal object: {goal_obj}")
                        update_result = assigned_performance_collection.update_one(
                            {"_id": ObjectId(form_id), "goals.goal_name": goal_name.strip()},
                            {"$set": {"goals.$.employee_rating": employee_rating}}
                        )
                        print(f"Update result for goal '{goal_name}': {update_result.modified_count} document(s) updated")
                        if update_result.modified_count == 0:
                            print(f"No match found for goal: {goal_name}")
                        else:
                            print(f"Goal update successful for: {goal_name}")
                    else:
                        print(f"Goal name not found in document: {goal_name}")

                except Exception as e:
                    print(f"Error updating goal: {goal_name}, Error: {str(e)}")

        # Update overall summary
        overall_summary_rating = int(request.form.get('overall_summary[employee_actual_rating]'))
        overall_summary_comments = request.form.get('overall_summary[employee_comments]')
        print(f"Updating overall summary with rating {overall_summary_rating} and comments {overall_summary_comments}")

        update_result = assigned_performance_collection.update_one(
            {"_id": ObjectId(form_id)},
            {"$set": {
                "overall_summary_and_ratings.employee_actual_rating.rating": overall_summary_rating,
                "overall_summary_and_ratings.employee_actual_rating.comments": overall_summary_comments
            }}
        )
        print(f"Update result for overall summary: {update_result.modified_count} document(s) updated")

        return "Thank you for submitting your feedback!"

    # If GET request, render the form
    competencies = performance_document.get("competencies", [])
    feedbacks = performance_document.get("feedbacks", {})
    goals = performance_document.get("goals", [])
    employee_name = performance_document.get("employee_name", "")

    return render_template('employee_feedback_form.html', 
                           competencies=competencies, 
                           feedbacks=feedbacks, 
                           goals=goals,
                           employee_name=employee_name, 
                           form_id=form_id)

@notify_performance_bp.route('/submit_employee_feedback/<form_id>', methods=['POST'])
def submit_employee_feedback(form_id):
    performance_document = assigned_performance_collection.find_one({"_id": ObjectId(form_id)})

    if not performance_document:
        return "Form not found", 404

    # Print the document before the update
    print(f"Document before update: {performance_document}")

    for key, value in request.form.items():
        if key.startswith('competencies'):
            comp_id = key.split('[')[1].split(']')[0]
            employee_rating = int(value)

            print(f"Competency ID: {comp_id}, Type: {type(comp_id)}")
            print(f"Employee Rating: {employee_rating}, Type: {type(employee_rating)}")

            # Attempt to update using ObjectId first
            try:
                comp_id_obj = ObjectId(comp_id)
            except errors.InvalidId:
                comp_id_obj = comp_id  # If conversion fails, keep as string

            # Try updating with ObjectId
            update_result = assigned_performance_collection.update_one(
                {"_id": ObjectId(form_id), "competencies._id": comp_id_obj},
                {"$set": {"competencies.$.employee_rating": employee_rating}}
            )
            print(f"Competency update result with ObjectId: {update_result.modified_count} document(s) updated")

            # If ObjectId fails, try updating with string ID
            if update_result.modified_count == 0:
                update_result = assigned_performance_collection.update_one(
                    {"_id": ObjectId(form_id), "competencies._id": comp_id},
                    {"$set": {"competencies.$.employee_rating": employee_rating}}
                )
                print(f"Competency update result with string ID: {update_result.modified_count} document(s) updated")

    # Update feedbacks using question_name as the identifier
    for key, value in request.form.items():
        if key.startswith('feedbacks'):
            try:
                # Extract question_name from the form key
                question_name = key.split('[')[1].split(']')[0]
                employee_feedback = value

                # Log the question name and feedback
                print(f"Updating feedback for question: {question_name} with feedback: {employee_feedback}")

                # Use the question_name to identify the correct question to update
                update_result = assigned_performance_collection.update_one(
                    {
                        "_id": ObjectId(form_id),
                        "feedbacks.questions.question_name": question_name
                    },
                    {"$set": {"feedbacks.questions.$.employee_feedback": employee_feedback}}
                )
                print(f"Feedback update result: {update_result.modified_count} document(s) updated")

                if update_result.modified_count == 0:
                    print(f"No match found for question: {question_name}")
            except IndexError as e:
                print(f"Error parsing question name from key: {key}, Error: {str(e)}")

    # Update overall summary
    overall_summary_rating = int(request.form.get('overall_summary[employee_actual_rating]'))
    overall_summary_comments = request.form.get('overall_summary[employee_comments]')
    print(f"Updating overall summary with rating {overall_summary_rating} and comments {overall_summary_comments}")
    
    update_result = assigned_performance_collection.update_one(
        {"_id": ObjectId(form_id)},
        {"$set": {
            "overall_summary_and_ratings.employee_actual_rating.rating": overall_summary_rating,
            "overall_summary_and_ratings.employee_actual_rating.comments": overall_summary_comments
        }}
    )
    print(f"Update result: {update_result.modified_count} document(s) updated")

    # Print the document after the update
    updated_document = assigned_performance_collection.find_one({"_id": ObjectId(form_id)})
    print(f"Document after update: {updated_document}")

    return "Thank you for submitting your feedback!"

# Route to send feedback form email to employee by name
@notify_performance_bp.route('/send_feedback_form', methods=['POST'])
def send_feedback_form():
    data = request.json
    performance_document_name = data.get('performance_document_name')
    employee_name = data.get('employee_name')

    if not performance_document_name or not employee_name:
        return jsonify({"error": "Missing required parameters"}), 400

    # Split employee_name into first_name and last_name
    try:
        first_name, last_name = employee_name.split(' ', 1)
    except ValueError:
        return jsonify({"error": "Invalid employee name format"}), 400

    # Retrieve the employee's email from s_employeedetails_2 collection
    employee_record = employee_details_collection.find_one({
        "first_name": {"$regex": f"^{first_name}$", "$options": "i"},
        "last_name": {"$regex": f"^{last_name}$", "$options": "i"}
    })

    if not employee_record:
        return jsonify({"error": "Employee not found"}), 404

    employee_email = employee_record.get('email')

    if not employee_email:
        return jsonify({"error": "Employee email not found"}), 404

    # Retrieve the performance document by name
    performance_document = assigned_performance_collection.find_one({
        "performance_document_name": performance_document_name,
        "employee_name": employee_name
    })

    if not performance_document:
        return jsonify({"error": "Performance document not found"}), 404

    # Generate the feedback form link
    feedback_form_link = url_for('notify_performance_bp.employee_feedback_form', form_id=performance_document['_id'], _external=True)

    # Load the email template
    body_template = load_template('employee_feedback_email.txt')

    # Prepare email subject and body
    subject = f"Feedback Request for {employee_name}"
    body = body_template.format(
        employee_name=employee_name,
        feedback_form_link=feedback_form_link
    )

    # Send the email
    send_email(employee_email, subject, body)

    return jsonify({"message": "Feedback form email sent successfully"}), 200
