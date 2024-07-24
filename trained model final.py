

import pandas as pd
import numpy as np
import openai
from sklearn.metrics.pairwise import cosine_similarity
import re

# Initialize OpenAI API key
openai.api_key = 'sk-proj-rA3HFQjuD7OljqVUA3h4T3BlbkFJEx9yd9Q0uwkNWpdD8AXM'  # Replace with your OpenAI API key

# Function to get embeddings from OpenAI
def get_embeddings(texts):
    response = openai.Embedding.create(input=texts, engine="text-embedding-ada-002")
    embeddings = [data['embedding'] for data in response['data']]
    return np.array(embeddings)

# Load the provided Excel file
file_path = '/Users/vishalmeena/Downloads/Personnel list 5 (1) 1.xlsx'  # Update with your actual file path
excel_data = pd.ExcelFile(file_path)

# Display the sheet names to understand the structure of the file
sheet_names = excel_data.sheet_names
print(sheet_names)

# Function to concatenate column names and data for better similarity matching
def concatenate_column_data(df, n_samples=10):
    concatenated_data = {}
    for col in df.columns:
        sample_data = df[col].astype(str).sample(n=min(n_samples, len(df)), random_state=1).tolist()
        concatenated_data[col] = f"{col}: {' '.join(sample_data)}"
    return concatenated_data

# Function to collect column names and concatenated data from each sheet
def collect_sheet_data(excel_data, sheet_names, exclude_sheets=[]):
    collected_data = {}
    for sheet in sheet_names:
        if sheet not in exclude_sheets:  # Exclude specified sheets
            df = excel_data.parse(sheet)
            sheet_data = concatenate_column_data(df)
            collected_data.update(sheet_data)
    return collected_data

# Load the data from Sheet1 (reference) and original test 7 (input for matching)
sheet1_df = excel_data.parse('Sheet1')
sheet7_df = excel_data.parse('vishal')

# Reference columns and concatenated data from Sheet1
ref_data = concatenate_column_data(sheet1_df)
ref_columns = list(ref_data.keys())

# Collect data from all other sheets for training
training_collected_data = collect_sheet_data(excel_data, sheet_names, exclude_sheets=['Sheet1', 'vishal'])

# Function to get combined embeddings for columns and data
def get_combined_embeddings(columns_data):
    column_names = [col for col, _ in columns_data.items()]
    data_samples = [data for _, data in columns_data.items()]
    
    # Get embeddings for column names
    column_name_embeddings = get_embeddings(column_names)
    # Get embeddings for data samples
    data_sample_embeddings = get_embeddings(data_samples)
    
    # Combine the embeddings with more weight to the column name
    combined_embeddings = 0.3 * column_name_embeddings + 0.7 * data_sample_embeddings
    return combined_embeddings

# Get combined embeddings for reference and training data
ref_embeddings = get_combined_embeddings(ref_data)
train_embeddings = get_combined_embeddings(training_collected_data)

# Function to map new data columns using the trained model
def map_new_columns(input_df, ref_columns, ref_embeddings):
    # Collect data from the input DataFrame
    input_data = concatenate_column_data(input_df)
    input_columns = list(input_data.keys())

    # Get combined embeddings for input data
    input_embeddings = get_combined_embeddings(input_data)
    
    # Calculate cosine similarity
    similarity_matrix = cosine_similarity(input_embeddings, ref_embeddings)
    
    # Find the best matches for each new column
    new_column_mappings = {}
    for i, input_col in enumerate(input_columns):
        if similarity_matrix.shape[0] <= i:
            print(f"Skipping column {input_col} due to mismatch in embeddings.")
            continue
        best_match_index = np.argmax(similarity_matrix[i])
        best_match_score = similarity_matrix[i][best_match_index]
        if best_match_index < len(ref_columns) and best_match_score >= 0.7:
            new_column_mappings[input_col] = (ref_columns[best_match_index], best_match_score)
        else:
            new_column_mappings[input_col] = ('No Match', best_match_score)
    
    # Convert the mappings to a DataFrame for better readability
    new_mappings_df = pd.DataFrame(new_column_mappings).T
    new_mappings_df.columns = ['Mapped Reference Column', 'Cosine Similarity']
    
    return new_mappings_df

# Use the trained model to detect columns in original test 7
new_mappings_df = map_new_columns(sheet7_df, ref_columns, ref_embeddings)

# Display the mappings DataFrame
print(new_mappings_df)

# Save the mappings DataFrame to a CSV file
output_file_path = '/Users/vishalmeena/Downloads/piyushW/column_mappings.csv'
new_mappings_df.to_csv(output_file_path, index=True)

print(f"Mappings saved to {output_file_path}")

