import openai
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_samples, silhouette_score
from pymongo import MongoClient
import json
from flask import Flask, jsonify

# Initialize Flask application
app = Flask(__name__)



# Connecting to MongoDB
client = MongoClient('Your mongodb')
db = client['dev1']

def get_database():
    collection_names = ["TRN_course_data", "TRN_course_to_job_family", "TRN_department_to_job_family", "TRN_employee_data", "TRN_job_skills"]
    data = {}
    for collection_name in collection_names:
        collection = db[collection_name]
        data[collection_name] = list(collection.find())
    return data

employee_sample = pd.DataFrame(list(db.TRN_employee_data.find()))
course_data = pd.DataFrame(list(db.TRN_course_data.find()))
course_to_job_family = pd.DataFrame(list(db.TRN_course_to_job_family.find()))
department_jf = pd.DataFrame(list(db.TRN_department_to_job_family.find()))
job_skills = pd.DataFrame(list(db.TRN_job_skills.find()))

# Function to get embeddings for course descriptions
def get_embedding(text):
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response['data'][0]['embedding']

# Generate embeddings for all course descriptions and skills
course_data['description_embedding'] = course_data['description'].apply(get_embedding)
course_data['skills_embedding'] = course_data['course_skills'].apply(get_embedding)

# Save embeddings to a file
course_data.to_pickle('course_data_with_embeddings.pkl')

# Load data with embeddings
course_data = pd.read_pickle('course_data_with_embeddings.pkl')

# Function to cluster courses and plot them with names
def cluster_courses():
    all_embeddings = np.vstack(course_data['description_embedding'].values)
   
    # Use KMeans to cluster courses
    kmeans = KMeans(n_clusters=7, random_state=70)
    course_data['Cluster'] = kmeans.fit_predict(all_embeddings)
   
    # Reduce dimensions for plotting
    pca = PCA(n_components=2)
    reduced_embeddings = pca.fit_transform(all_embeddings)
   
    course_data['PCA1'] = reduced_embeddings[:, 0]
    course_data['PCA2'] = reduced_embeddings[:, 1]
   
    return kmeans, all_embeddings

# Function to get JSON response
def get_json_response():
    kmeans, all_embeddings = cluster_courses()
    cluster_labels = kmeans.labels_
    silhouette_vals = silhouette_samples(all_embeddings, cluster_labels)
    silhouette_avg = silhouette_score(all_embeddings, cluster_labels)
    course_data['rating'] = employee_sample['rating']

    result = {
        "PCA1": course_data['PCA1'].tolist(),
        "PCA2": course_data['PCA2'].tolist(),
        "rating": course_data['rating'].tolist(),
        "silhouette_avg": silhouette_avg,
        "silhouette_values": silhouette_vals.tolist(),
        "clusters": course_data['Cluster'].tolist(),
        "course_name": course_data['course_name'].tolist()
    }

    return result

# Flask route to get JSON response
@app.route('/recommend_course_data', methods=['POST'])
def get_course_data():
    response = get_json_response()
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
