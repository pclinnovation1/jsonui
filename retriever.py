import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def read_multiple_csv_data(directory_path):
    all_dfs = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory_path, filename)
            df = pd.read_csv(file_path)
            all_dfs.append(df)
    combined_df = pd.concat(all_dfs, ignore_index=True)
    return combined_df

def retrieve_relevant_data(query, df, top_n=3):
    df['combined'] = df.apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
    documents = df['combined'].tolist()
    vectorizer = TfidfVectorizer().fit_transform(documents + [query])
    vectors = vectorizer.toarray()
    cosine_similarities = cosine_similarity(vectors[-1], vectors[:-1])
    similar_indices = cosine_similarities.argsort()[0][-top_n:]
    similar_items = [(cosine_similarities[0][i], documents[i]) for i in similar_indices]
    return [item[1] for item in similar_items]
