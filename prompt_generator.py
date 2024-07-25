import pandas as pd
import os

def read_csv_data(file_path):
    """
    Reads a CSV file and returns a DataFrame.
    """
    df = pd.read_csv(file_path)
    return df

def read_multiple_csv_data(directory_path):
    """
    Reads multiple CSV files from a directory and concatenates them into a single DataFrame.
    """
    all_dfs = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory_path, filename)
            df = read_csv_data(file_path)
            all_dfs.append(df)
    combined_df = pd.concat(all_dfs, ignore_index=True)
    return combined_df

def generate_prompt_from_chunk(df_chunk, additional_instructions):
    """
    Analyse the following provided files and provide report with compliance status.
    - Show the compliance status of each "Mandatory" course with each person. If completion_date after Due_date then compliance status should be Non-Compliant. And if completion_date before or on Due_date then compliance status should be Compliant.
    - First, read and understand the files present in your knowledge base.
    - Generate full data whenever asked to show data.
    - Generate visuals and reports based on tasks described in text format, leveraging data from files provided in the knowledge base.
    - If data is provided in csv or any other format, then the model needs to respond as per the user's need.
    - CSV and Document files will be added to the model's knowledge.
    - The model needs to read and understand only the data present in its knowledge, no data other than that. The model cannot use data beyond its knowledge data.
    - Based on the analysis of data, the model needs to provide visualization (different charts as per need).
    - The model needs to read and store the data in memory, to use that valuable data in the future.
    - Compliant status: If Completion date > Due date, then status should be Non-Compliant, and if Completion date <= Due date, then status should be Compliant.
    """
    data_str = df_chunk.to_string(index=False)
    prompt = f"{additional_instructions}\n\nHere is the data:\n{data_str}"
    return prompt
