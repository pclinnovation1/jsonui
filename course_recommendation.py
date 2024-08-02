from flask import Flask, request, jsonify
from pymongo import MongoClient
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import numpy as np
import openai
from datetime import datetime

app = Flask(__name__)

# Set up OpenAI API key
openai.api_key = ''  # Make sure to set this environment variable

# MongoDB Client Setup
client = MongoClient('mongodb://dev1_user:dev1_pass@172.191.245.199:27017/dev1')
db = client['dev1']

# Function to parse dates with multiple possible formats
def parse_date(date_str):
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Date format for '{date_str}' is not supported")

@app.route('/recommend_course_data', methods=['POST'])
def process_data():
    # Fetch data from MongoDB collections
    lrn_courses = list(db.LRN_course.find())
    lrn_employee_details = list(db.HRM_employee_details.find())
    lrn_employee_offering_details = list(db.LRN_employee_offering_detail.find())
    
    data = []
    embeddings = []

    # Process each course
    for course in lrn_courses:
        short_description = course['general_information']['basic_information']['short_description']
        
        # Get embedding for short_description using OpenAI API
        embedding_response = openai.Embedding.create(input=short_description, engine="text-embedding-ada-002")
        embedding = embedding_response['data'][0]['embedding']
        
        # Calculate real effort
        min_effort = float(course['general_information']['other_details']['minimum_expected_effort'].split()[0])
        max_effort = float(course['general_information']['other_details']['maximum_expected_effort'].split()[0])
        real_effort = (min_effort + max_effort) / 2

        # Find associated employee offering details
        for offering in lrn_employee_offering_details:
            if offering['offering_name'] == course['general_information']['basic_information']['title']:
                # Find associated employee details
                for employee in lrn_employee_details:
                    if employee['person_name'] == offering['person_name']:
                        # Ensure the 'completed_on' key exists
                        if 'completed_on' in offering:
                            # Convert date strings to datetime objects
                            enrolled_on = parse_date(offering['enrollment_date'])
                            completed_on = parse_date(offering['completed_on'])
                            
                            # Calculate average price
                            price = (course['general_information']['other_details']['minimum_price'] +
                                     course['general_information']['other_details']['maximum_price']) / 2
                            
                            # Append data and embeddings
                            data.append({
                                "course_name": course['general_information']['basic_information']['title'],
                                "person_name": employee['person_name'],
                                "completed_on": offering['completed_on'].split()[0],  # Extract date only
                                "enrolled_on": offering['enrollment_date'],
                                "embedding": embedding,
                                "feedback": course['feedback'],
                                "price": price,
                                "real_effort": real_effort,
                                "department": employee['department']
                            })
                            embeddings.append(embedding)
    
    # Prepare embeddings for PCA and clustering
    embeddings_array = np.array(embeddings)
    pca = PCA(n_components=2)
    reduced_embeddings = pca.fit_transform(embeddings_array)
    
    # Perform KMeans clustering
    kmeans = KMeans(n_clusters=7, random_state=0)
    clusters = kmeans.fit_predict(reduced_embeddings)
    
    # Add PCA and cluster information to data
    for i, d in enumerate(data):
        d['PCA1'] = reduced_embeddings[i, 0]
        d['PCA2'] = reduced_embeddings[i, 1]
        d['cluster'] = int(clusters[i])
        del d['embedding']  # Remove raw embedding for brevity
    
    return jsonify({"data": data})

if __name__ == '__main__':
    app.run(debug=True)