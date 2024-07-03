# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.preprocessing import LabelEncoder
# from sklearn.metrics import classification_report, accuracy_score, mean_absolute_error
# from sklearn.linear_model import LinearRegression
# from datetime import datetime, timedelta
# import openai
# import matplotlib.pyplot as plt
# import seaborn as sns
# from wordcloud import WordCloud
# import pickle
# import joblib

# # Load your data
# file_path = 'updated_final_records_with_active_day.csv'
# data = pd.read_csv(file_path)

# # Ensure the 'Timestamp' column is in datetime format
# data['Timestamp'] = pd.to_datetime(data['Timestamp'])

# # Set the 'Timestamp' column as the index
# data.set_index('Timestamp', inplace=True)

# # Plot the number of emails sent over time
# plt.figure(figsize=(12, 6))
# data.resample('M').size().plot()
# plt.title('Number of Emails Sent Over Time')
# plt.xlabel('Time')
# plt.ylabel('Number of Emails')
# plt.grid(True)
# plt.show()

# # Priority Level Distribution
# plt.figure(figsize=(8, 6))
# sns.countplot(x='Priority Level', data=data, palette='viridis')
# plt.title('Distribution of Priority Levels')
# plt.xlabel('Priority Level')
# plt.ylabel('Count')
# plt.show()

# # Response Likelihood by Priority Level
# plt.figure(figsize=(12, 6))
# sns.boxplot(x='Priority Level', y='Response Likelihood', data=data, palette='viridis')
# plt.title('Response Likelihood by Priority Level')
# plt.xlabel('Priority Level')
# plt.ylabel('Response Likelihood')
# plt.grid(True)
# plt.show()

# # WordClouds
# send_now_comments = data[data['Send Now'] == 1]['Comments']
# dont_send_now_comments = data[data['Send Now'] == 0]['Comments']

# send_now_text = ' '.join(send_now_comments.dropna().tolist())
# dont_send_now_text = ' '.join(dont_send_now_text.dropna().tolist())

# send_now_wordcloud = WordCloud(width=800, height=400, background_color='white').generate(send_now_text)
# dont_send_now_wordcloud = WordCloud(width=800, height=400, background_color='white').generate(dont_send_now_text)

# plt.figure(figsize=(15, 8))

# plt.subplot(1, 2, 1)
# plt.imshow(send_now_wordcloud, interpolation='bilinear')
# plt.title('Word Cloud for Sending Emails')
# plt.axis('off')

# plt.subplot(1, 2, 2)
# plt.imshow(dont_send_now_wordcloud, interpolation='bilinear')
# plt.title('Word Cloud for Not Sending Emails')
# plt.axis('off')

# plt.show()

# # OpenAI API key
# openai.api_key = 'sk-proj-rA3HFQjuD7OljqVUA3h4T3BlbkFJEx9yd9Q0uwkNWpdD8AXM'

# # Function to generate embeddings using OpenAI with caching
# embedding_cache = {}

# def get_openai_embeddings(text):
#     if text in embedding_cache:
#         return embedding_cache[text]
#     response = openai.Embedding.create(input=[text], model="text-embedding-ada-002")
#     embedding = response['data'][0]['embedding']
#     embedding_cache[text] = embedding
#     return embedding

# # Generate embeddings for text features
# data['Trigger_Embedding'] = data['Trigger'].apply(lambda x: get_openai_embeddings(x))
# data['Applies_To_Embedding'] = data['Applies To'].apply(lambda x: get_openai_embeddings(x))
# data['Learning_Type_Embedding'] = data['Learning Type'].apply(lambda x: get_openai_embeddings(x))
# data['Most_Active_Day_Embedding'] = data['Most Active Day'].apply(lambda x: get_openai_embeddings(x))

# X_embeddings = np.hstack([
#     np.vstack(data['Trigger_Embedding']),
#     np.vstack(data['Applies_To_Embedding']),
#     np.vstack(data['Learning_Type_Embedding']),
# ])

# le_priority = LabelEncoder()
# y_priority = le_priority.fit_transform(data['Priority Level'])

# X_train_priority, X_test_priority, y_train_priority, y_test_priority = train_test_split(X_embeddings, y_priority, test_size=0.2, random_state=42)

# priority_model = RandomForestClassifier(random_state=42)
# priority_model.fit(X_train_priority, y_train_priority)

# y_pred_priority = priority_model.predict(X_test_priority)
# print(classification_report(y_test_priority, y_pred_priority, target_names=le_priority.classes_))
# print("Accuracy:", accuracy_score(y_test_priority, y_pred_priority))

# # Function to predict priority level
# def predict_priority_level(trigger, applies_to, learning_type):
#     # Generate embeddings for the input text
#     trigger_embedding = get_openai_embeddings(trigger)
#     applies_to_embedding = get_openai_embeddings(applies_to)
#     learning_type_embedding = get_openai_embeddings(learning_type)

#     # Combine embeddings into a single feature array
#     input_features = np.hstack([
#         trigger_embedding,
#         applies_to_embedding,
#         learning_type_embedding,
#     ]).reshape(1, -1)

#     # Predict the priority level
#     predicted_priority_encoded = priority_model.predict(input_features)[0]
#     predicted_priority = le_priority.inverse_transform([predicted_priority_encoded])[0]

#     return predicted_priority

# trigger = "90 days "
# applies_to = "Reassignment"
# learning_type = "Instructor-led"

# predicted_priority = predict_priority_level(trigger, applies_to, learning_type)
# print(f"Predicted Priority Level: {predicted_priority}")

# # Function to get the next active day from a given day
# def get_next_active_day(current_date, active_day):
#     days_ahead = (active_day - current_date.weekday() + 7) % 7
#     if days_ahead == 0:
#         days_ahead = 7
#     return current_date + timedelta(days=int(days_ahead))  # Convert to int

# # Encode categorical variables
# le_active_day = LabelEncoder()
# data['Most Active Day Encoded'] = le_active_day.fit_transform(data['Most Active Day'])

# le_tone = LabelEncoder()
# data['Tone Encoded'] = le_tone.fit_transform(data['Tone'])

# # Define features and target for the regression model
# X = data[['Most Active Day Encoded', 'Response Likelihood', 'Tone Encoded']]
# y = data['Typical Response Time']

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# regression_model = LinearRegression()
# regression_model.fit(X_train, y_train)

# # Predict and evaluate
# y_pred = regression_model.predict(X_test)
# mae = mean_absolute_error(y_test, y_pred)
# print(f"Mean Absolute Error: {mae}")

# def predict_days_to_send(most_active_day, response_likelihood, tone, current_date):
#     # Encode input parameters
#     most_active_day_encoded = le_active_day.transform([most_active_day])[0]
#     tone_encoded = le_tone.transform([tone])[0]

#     # Create input feature array
#     input_features = np.array([[most_active_day_encoded, response_likelihood, tone_encoded]])

#     # Predict the number of days to wait
#     predicted_days = regression_model.predict(input_features)[0]
    
#     if response_likelihood < 0.5:
#         # Send early if response likelihood is low
#         return max(predicted_days, 0)
#     else:
#         # Send on the next active day if response likelihood is high
#         next_active_day = get_next_active_day(current_date, le_active_day.transform([most_active_day])[0])
#         return (next_active_day - current_date).days

# current_date = datetime.now()

# most_active_day = "Wednesday"
# response_likelihood = 0.3
# tone = "Neutral"

# days_to_wait = predict_days_to_send(most_active_day, response_likelihood, tone, current_date)
# print(f"Predicted days to wait: {days_to_wait}")

# # Function to adjust response likelihood based on compliance
# def adjust_response_likelihood(response_likelihood, complied):
#     if complied:
#         return min(response_likelihood + 0.1, 1.0)
#     else:
#         return max(response_likelihood - 0.1, 0.0)

# # Example user input for compliance
# user_complied_input = input("Did the user comply within the predicted number of days? (yes/no): ").strip().lower()
# user_complied = user_complied_input == 'yes'

# # Adjust response likelihood for a specific record (for example, the first record)
# original_response_likelihood = data.iloc[0]['Response Likelihood']
# new_response_likelihood = adjust_response_likelihood(original_response_likelihood, user_complied)

# print(f"Original Response Likelihood: {original_response_likelihood}")
# print(f"New Response Likelihood: {new_response_likelihood}")

# # Save the embedding cache
# with open('embedding_cache.pkl', 'wb') as f:
#     pickle.dump(embedding_cache, f)

# # Save models and encoders after training
# joblib.dump(priority_model, 'priority_model.pkl')
# joblib.dump(regression_model, 'regression_model.pkl')
# joblib.dump(le_priority, 'le_priority.pkl')
# joblib.dump(le_active_day, 'le_active_day.pkl')
# joblib.dump(le_tone, 'le_tone.pkl')


































# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.preprocessing import LabelEncoder
# from sklearn.metrics import classification_report, accuracy_score, mean_absolute_error
# from sklearn.linear_model import LinearRegression
# from datetime import datetime, timedelta
# import openai
# import matplotlib.pyplot as plt
# import seaborn as sns
# from wordcloud import WordCloud
# import pickle
# import joblib

# # Load your data
# file_path = r'C:\Users\HP\Pictures\Approvals_26\approval-framework\data\updated_final_records_with_active_day.csv'
# data = pd.read_csv(file_path)

# # Ensure the 'Timestamp' column is in datetime format
# data['Timestamp'] = pd.to_datetime(data['Timestamp'])

# # Set the 'Timestamp' column as the index
# data.set_index('Timestamp', inplace=True)

# # Plot the number of emails sent over time
# plt.figure(figsize=(12, 6))
# data.resample('M').size().plot()
# plt.title('Number of Emails Sent Over Time')
# plt.xlabel('Time')
# plt.ylabel('Number of Emails')
# plt.grid(True)
# plt.show()

# # Priority Level Distribution
# plt.figure(figsize=(8, 6))
# sns.countplot(x='Priority Level', data=data, palette='viridis')
# plt.title('Distribution of Priority Levels')
# plt.xlabel('Priority Level')
# plt.ylabel('Count')
# plt.show()

# # Response Likelihood by Priority Level
# plt.figure(figsize=(12, 6))
# sns.boxplot(x='Priority Level', y='Response Likelihood', data=data, palette='viridis')
# plt.title('Response Likelihood by Priority Level')
# plt.xlabel('Priority Level')
# plt.ylabel('Response Likelihood')
# plt.grid(True)
# plt.show()

# # WordClouds
# send_now_comments = data[data['Send Now'] == 1]['Comments']
# dont_send_now_comments = data[data['Send Now'] == 0]['Comments']

# send_now_text = ' '.join(send_now_comments.dropna().tolist())
# dont_send_now_text = ' '.join(dont_send_now_comments.dropna().tolist())

# send_now_wordcloud = WordCloud(width=800, height=400, background_color='white').generate(send_now_text)
# dont_send_now_wordcloud = WordCloud(width=800, height=400, background_color='white').generate(dont_send_now_text)

# plt.figure(figsize=(15, 8))

# plt.subplot(1, 2, 1)
# plt.imshow(send_now_wordcloud, interpolation='bilinear')
# plt.title('Word Cloud for Sending Emails')
# plt.axis('off')

# plt.subplot(1, 2, 2)
# plt.imshow(dont_send_now_wordcloud, interpolation='bilinear')
# plt.title('Word Cloud for Not Sending Emails')
# plt.axis('off')

# plt.show()

# # OpenAI API key
# openai.api_key = 'sk-proj-rA3HFQjuD7OljqVUA3h4T3BlbkFJEx9yd9Q0uwkNWpdD8AXM'

# # Function to generate embeddings using OpenAI with caching
# embedding_cache = {}

# def get_openai_embeddings(text):
#     if text in embedding_cache:
#         return embedding_cache[text]
#     response = openai.Embedding.create(input=[text], model="text-embedding-ada-002")
#     embedding = response['data'][0]['embedding']
#     embedding_cache[text] = embedding
#     return embedding

# # Generate embeddings for text features
# data['Trigger_Embedding'] = data['Trigger'].apply(lambda x: get_openai_embeddings(x))
# data['Applies_To_Embedding'] = data['Applies To'].apply(lambda x: get_openai_embeddings(x))
# data['Learning_Type_Embedding'] = data['Learning Type'].apply(lambda x: get_openai_embeddings(x))
# data['Most_Active_Day_Embedding'] = data['Most Active Day'].apply(lambda x: get_openai_embeddings(x))

# X_embeddings = np.hstack([
#     np.vstack(data['Trigger_Embedding']),
#     np.vstack(data['Applies_To_Embedding']),
#     np.vstack(data['Learning_Type_Embedding']),
# ])

# le_priority = LabelEncoder()
# y_priority = le_priority.fit_transform(data['Priority Level'])

# X_train_priority, X_test_priority, y_train_priority, y_test_priority = train_test_split(X_embeddings, y_priority, test_size=0.2, random_state=42)

# priority_model = RandomForestClassifier(random_state=42)
# priority_model.fit(X_train_priority, y_train_priority)

# y_pred_priority = priority_model.predict(X_test_priority)
# print(classification_report(y_test_priority, y_pred_priority, target_names=le_priority.classes_))
# print("Accuracy:", accuracy_score(y_test_priority, y_pred_priority))

# # Function to predict priority level
# def predict_priority_level(trigger, applies_to, learning_type):
#     # Generate embeddings for the input text
#     trigger_embedding = get_openai_embeddings(trigger)
#     applies_to_embedding = get_openai_embeddings(applies_to)
#     learning_type_embedding = get_openai_embeddings(learning_type)

#     # Combine embeddings into a single feature array
#     input_features = np.hstack([
#         trigger_embedding,
#         applies_to_embedding,
#         learning_type_embedding,
#     ]).reshape(1, -1)

#     # Predict the priority level
#     predicted_priority_encoded = priority_model.predict(input_features)[0]
#     predicted_priority = le_priority.inverse_transform([predicted_priority_encoded])[0]

#     return predicted_priority

# trigger = "90 days "
# applies_to = "Reassignment"
# learning_type = "Instructor-led"

# predicted_priority = predict_priority_level(trigger, applies_to, learning_type)
# print(f"Predicted Priority Level: {predicted_priority}")

# # Function to get the next active day from a given day
# def get_next_active_day(current_date, active_day):
#     days_ahead = (active_day - current_date.weekday() + 7) % 7
#     if days_ahead == 0:
#         days_ahead = 7
#     return current_date + timedelta(days=int(days_ahead))  # Convert to int

# # Encode categorical variables
# le_active_day = LabelEncoder()
# data['Most Active Day Encoded'] = le_active_day.fit_transform(data['Most Active Day'])

# le_tone = LabelEncoder()
# data['Tone Encoded'] = le_tone.fit_transform(data['Tone'])

# # Define features and target for the regression model
# X = data[['Most Active Day Encoded', 'Response Likelihood', 'Tone Encoded']]
# y = data['Typical Response Time']

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# regression_model = LinearRegression()
# regression_model.fit(X_train, y_train)

# # Predict and evaluate
# y_pred = regression_model.predict(X_test)
# mae = mean_absolute_error(y_test, y_pred)
# print(f"Mean Absolute Error: {mae}")

# def predict_days_to_send(most_active_day, response_likelihood, tone, current_date):
#     # Encode input parameters
#     most_active_day_encoded = le_active_day.transform([most_active_day])[0]
#     tone_encoded = le_tone.transform([tone])[0]

#     # Create input feature array
#     input_features = np.array([[most_active_day_encoded, response_likelihood, tone_encoded]])

#     # Predict the number of days to wait
#     predicted_days = regression_model.predict(input_features)[0]
    
#     if response_likelihood < 0.5:
#         # Send early if response likelihood is low
#         return max(predicted_days, 0)
#     else:
#         # Send on the next active day if response likelihood is high
#         next_active_day = get_next_active_day(current_date, le_active_day.transform([most_active_day])[0])
#         return (next_active_day - current_date).days

# current_date = datetime.now()

# most_active_day = "Wednesday"
# response_likelihood = 0.3
# tone = "Neutral"

# days_to_wait = predict_days_to_send(most_active_day, response_likelihood, tone, current_date)
# print(f"Predicted days to wait: {days_to_wait}")

# # Function to adjust response likelihood based on compliance
# def adjust_response_likelihood(response_likelihood, complied):
#     if complied:
#         return min(response_likelihood + 0.1, 1.0)
#     else:
#         return max(response_likelihood - 0.1, 0.0)

# # Example user input for compliance
# user_complied_input = input("Did the user comply within the predicted number of days? (yes/no): ").strip().lower()
# user_complied = user_complied_input == 'yes'

# # Adjust response likelihood for a specific record (for example, the first record)
# original_response_likelihood = data.iloc[0]['Response Likelihood']
# new_response_likelihood = adjust_response_likelihood(original_response_likelihood, user_complied)

# print(f"Original Response Likelihood: {original_response_likelihood}")
# print(f"New Response Likelihood: {new_response_likelihood}")

# # Save the embedding cache
# with open('embedding_cache.pkl', 'wb') as f:
#     pickle.dump(embedding_cache, f)

# # Save models and encoders after training
# joblib.dump(priority_model, 'priority_model.pkl')
# joblib.dump(regression_model, 'regression_model.pkl')
# joblib.dump(le_priority, 'le_priority.pkl')
# joblib.dump(le_active_day, 'le_active_day.pkl')
# joblib.dump(le_tone, 'le_tone.pkl')
