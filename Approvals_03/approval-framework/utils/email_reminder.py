# # utils/email_reminder.py

# import numpy as np
# from datetime import datetime, timedelta
# import joblib

# # Load pre-trained models and encoders
# priority_model = joblib.load('models/priority_model.pkl')
# regression_model = joblib.load('models/regression_model.pkl')
# le_priority = joblib.load('models/le_priority.pkl')
# le_active_day = joblib.load('models/le_active_day.pkl')
# le_tone = joblib.load('models/le_tone.pkl')

# def get_next_active_day(current_date, active_day):
#     days_ahead = (active_day - current_date.weekday() + 7) % 7
#     if days_ahead == 0:
#         days_ahead = 7
#     return current_date + timedelta(days=int(days_ahead))

# def predict_priority_level(trigger, applies_to, learning_type):
#     trigger_embedding = get_openai_embeddings(trigger)
#     applies_to_embedding = get_openai_embeddings(applies_to)
#     learning_type_embedding = get_openai_embeddings(learning_type)

#     input_features = np.hstack([
#         trigger_embedding,
#         applies_to_embedding,
#         learning_type_embedding,
#     ]).reshape(1, -1)

#     predicted_priority_encoded = priority_model.predict(input_features)[0]
#     predicted_priority = le_priority.inverse_transform([predicted_priority_encoded])[0]

#     return predicted_priority

# def predict_response_likelihood(most_active_day, response_likelihood, tone):
#     most_active_day_encoded = le_active_day.transform([most_active_day])[0]
#     tone_encoded = le_tone.transform([tone])[0]

#     input_features = np.array([[most_active_day_encoded, response_likelihood, tone_encoded]])
#     predicted_days = regression_model.predict(input_features)[0]

#     predicted_priority = "Medium"  # Example priority, modify as needed

#     return predicted_days, predicted_priority

# def send_reminders(most_active_day, response_likelihood, tone):
#     predicted_days_to_wait, predicted_priority = predict_response_likelihood(most_active_day, response_likelihood, tone)
#     return predicted_days_to_wait, predicted_priority



# utils/email_reminder.py

# import numpy as np
# from datetime import datetime, timedelta
# import joblib

# # Load the trained models and encoders
# priority_model = joblib.load('models/priority_model.pkl')
# regression_model = joblib.load('models/regression_model.pkl')
# le_priority = joblib.load('models/le_priority.pkl')
# le_active_day = joblib.load('models/le_active_day.pkl')
# le_tone = joblib.load('models/le_tone.pkl')

# def get_next_active_day(current_date, active_day):
#     days_ahead = (active_day - current_date.weekday() + 7) % 7
#     if days_ahead == 0:
#         days_ahead = 7
#     return current_date + timedelta(days=int(days_ahead))

# def send_reminders(most_active_day, response_likelihood, tone):
#     most_active_day_encoded = le_active_day.transform([most_active_day])[0]
#     tone_encoded = le_tone.transform([tone])[0]

#     input_features = np.array([[most_active_day_encoded, response_likelihood, tone_encoded]])
#     predicted_days = regression_model.predict(input_features)[0]

#     if response_likelihood < 0.5:
#         predicted_days_to_wait = max(predicted_days, 0)
#     else:
#         next_active_day = get_next_active_day(datetime.now(), most_active_day_encoded)
#         predicted_days_to_wait = (next_active_day - datetime.now()).days

#     predicted_priority = "Medium"  # Replace with logic if needed

#     return predicted_days_to_wait, predicted_priority

# def check_pending_approvals_and_send_reminders(transactions_collection, reminder_predictions_collection):
#     current_date = datetime.now()
#     pending_transactions = transactions_collection.find({"status": "pending"})

#     for transaction in pending_transactions:
#         approvers = transaction.get("approvals", [])
#         if not any(approver['status'] == "approved" for approver in approvers):
#             # No approver has approved the transaction, send a reminder
#             most_active_day = transaction.get('most_active_day', 'Monday')
#             response_likelihood = transaction.get('response_likelihood', 0.5)
#             tone = transaction.get('tone', 'Neutral')

#             predicted_days_to_wait, predicted_priority = send_reminders(most_active_day, response_likelihood, tone)

#             # Save the reminder prediction details to the MongoDB collection
#             reminder_predictions_collection.insert_one({
#                 "transaction_id": transaction['_id'],
#                 "most_active_day": most_active_day,
#                 "response_likelihood": response_likelihood,
#                 "tone": tone,
#                 "predicted_days_to_wait": predicted_days_to_wait,
#                 "predicted_priority": predicted_priority,
#                 "timestamp": datetime.utcnow()
#             })
#             # Logic to send email (not implemented here)

#     return "Reminders sent based on pending approvals"









