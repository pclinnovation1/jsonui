# #All graph generation on bigger data(more than 100 employee) use this approach until find any better approach. If anyone find any better approach then notify.
import openai
import pandas as pd
import matplotlib.pyplot as plt
from flask import Blueprint, request, send_file, jsonify, url_for, render_template,Flask
from io import BytesIO
from pymongo import MongoClient
from new3 import generate_graph_fields
import re
import os
import uuid
import openai
import json
# Use only this correct import statement:
from langchain_community.chat_models import ChatOpenAI
import openai
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Set the backend to 'Agg' before importing pyplot
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Blueprint, request, send_file, jsonify, url_for, render_template, Flask
from pymongo import MongoClient
from new3 import generate_graph_fields
import re
import os
import uuid
import ast
 
# Set your OpenAI API key
openai.api_key = '...'  # Replace with your actual OpenAI API key

# Directory where images will be saved temporarily
TEMP_IMAGE_FOLDER = "static/temp_images"
 
if not os.path.exists(TEMP_IMAGE_FOLDER):
    os.makedirs(TEMP_IMAGE_FOLDER)
 
client = MongoClient('mongodb://oras_user:oras_pass@172.191.245.199:27017/oras')  # Modify according to your MongoDB setup
db = client['oras']
 
def get_dynamic_graph_code(report_type, data, description):
    print("get_dynamic_graph_code called ")
   
    """
    Generates Python code to create a graph based on the report type, user description, and data using OpenAI.
 
    Args:
    - report_type (str): The type of report for which the graph should be generated.
    - data (list): The data for creating the graph.
    - description (str): The user-provided description of the graph.
 
    Returns:
    - str: Python code that generates a graph.
    """
    
    prompt = f"""
You are a Python coding assistant. Based on the provided graph description and JSON data, generate Python code to create a graph using `pandas` and `plotly.express`.

User-Provided Graph Description:
"{description}"

Instructions:
- Use only `pandas` for data processing and `plotly.express` for graph creation.
- Interpret the graph type based on the description. For example, if the description mentions "distribution," use a pie chart or bar chart; if it mentions "trend," use a line chart; if it mentions "comparison," use a bar chart.
- Ensure that the code performs data cleaning, handles missing values, and prepares the data for analysis.
- Use the JSON data provided as a placeholder for the actual data that will be uploaded. Assume the variable `data = given data` will hold this data.
- Ensure that the generated code dynamically handles the data without hardcoding specific values, as actual data may vary.
- Customize the graph with titles, labels, and a consistent style based on the user description.
- Include data type conversions and missing value handling:
  - Convert columns to appropriate types, using `pd.to_numeric()` with `errors='coerce'` for numeric columns as needed.
  - Use `fillna()` or `dropna()` as appropriate to manage missing values.
  - Ensure that any issues related to type conversions are managed gracefully.
- Structure the code exactly as shown in the `graph_code.py` format below, where `fig` is the final figure generated with `plotly.express`.

Structure the code as follows:
    ```python
    //code
    ```

Additional Notes:
- Ensure that the generated code is ready to run in a standard Python environment.
- Avoid hardcoding any assumptions about the data format; the code should be adaptable to varied JSON data structures.

JSON Data:
{data}
"""



    response = openai.ChatCompletion.create(
        # model="ft:gpt-4o-2024-08-06:algonxai::AJIHdWE0",#5 new report
        model="ft:gpt-4o-2024-08-06:algonxai:5nov:AQFMyHPQ",#5 new report
        # model="chatgpt-4o-latest",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for generating Python code for data visualization."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=16384
    )
 
    # Extract the generated code from the response
    graph_code = response['choices'][0]['message']['content']
    print(graph_code)
    # Use regex to remove unwanted parts and only get the Python code
    # We're looking for anything between ```python and ```
    code_match = re.search(r"```python(.*?)```", graph_code, re.DOTALL)
    if code_match:
        graph_code = code_match.group(1).strip()  # Get the Python code block without the backticks
    else:
        print("Error: Could not extract valid Python code from the response.")
        return None
    
    return graph_code

def replace_data_with_full_dataset(generated_code, full_data):
    """
    Replaces the subset data in the generated code with the full dataset.
 
    Args:
    - generated_code (str): The generated Python code from OpenAI.
    - full_data (list): The full dataset for 500+ employees.
 
    Returns:
    - str: The modified Python code with full dataset.
    """
    # Convert full_data into a string format compatible with Python code
    full_data_str = f"data = {repr(full_data)}"
    
    # Replace only the data line
    modified_code = re.sub(r"data\s*=\s*\[.*?\]", full_data_str, generated_code, flags=re.DOTALL)
   
    return modified_code
  
def generate_report3(description):
    global modified_code_correct
    report_name = 'report_name'
    print("report name : ", report_name)
    print("*" * 25)
    user_description = description  # User-provided description

    # Fetch the report info from the report_fields_mapping1
    report_info = generate_graph_fields(user_description)  # Assuming this is a custom function
    print(report_info)
    if not report_info:
        print("Error: Invalid report name provided.")
        return

    # Initialize full_data
    full_data = []

    # Fetch full data from all collections (without limiting to 50 employees)
    for idx, (collection_name, field_names) in enumerate(report_info.items()):
        projection = {field: 1 for field in field_names}
        projection.update({'_id': 0})

        print("collection name : ", collection_name)
        print("*" * 25)
        
        # Fetch full dataset from each collection
        collection_data = list(db[collection_name].find({}, projection).limit(50))
        print('collection data: ', collection_data)
        print("*" * 25)
        
        collection_data2 = list(db[collection_name].find({}, projection).limit(1500))
        print()
        if idx == 0:
            full_data = collection_data

        else:
            collection_data_dict = {employee.get('person_name', 'Unknown'): employee for employee in collection_data}
            for employee in full_data:
                person_name = employee.get('person_name')
                if person_name and person_name in collection_data_dict:
                    for key in field_names:
                        employee[key] = collection_data_dict[person_name].get(key, None)

        if idx == 0:
            full_data2 = collection_data2

        else:
            collection_data_dict2 = {employee.get('person_name', 'Unknown'): employee for employee in collection_data2}
            for employee in full_data2:
                person_name = employee.get('person_name')
                if person_name and person_name in collection_data_dict2:
                    for key in field_names:
                        employee[key] = collection_data_dict2[person_name].get(key, None)

    print("Full data:", full_data)
    print("Collection 2 data:", full_data2)

    # Generate dynamic graph code (placeholder function)
    graph_code = get_dynamic_graph_code(report_name, full_data, user_description)  # Placeholder function

    if graph_code is None:
        print("Error: Failed to generate graph code.")
        return

    print('Graph Code:', graph_code)

    # Replace the full data with the full dataset in the generated code
    modified_code = replace_data_with_full_dataset(graph_code, full_data2)  # Placeholder function
    print('Modified Code:', modified_code)

    try:
        ast.parse(modified_code)
        print("Syntax check passed. No syntax errors detected.")
        modified_code_correct = modified_code
        try:
            exec(modified_code_correct, globals())
        except Exception as e:
            print("Execution Error:", e)
            newcoe = preprocess_code_for_openai(modified_code_correct)  # Placeholder function
            print("Execution error removal step 1st")
            corrected_code = handle_openai_error_correction(newcoe, e)  # Placeholder function

            # Final execution attempt after correction
            modified_code_correct = replace_data_with_full_dataset(corrected_code, full_data2)  # Placeholder function
            exec(modified_code_correct, globals())
    except SyntaxError as se:
        print(f"Syntax Error found on line {se.lineno}: {se.text.strip()}")
        newcoe = preprocess_code_for_openai(modified_code)  # Placeholder function
        corrected_code = handle_openai_syntax_correction(newcoe)  # Placeholder function

        modified_code_correct = replace_data_with_full_dataset(corrected_code, full_data2)  # Placeholder function
        exec(modified_code_correct, globals())
    except Exception as e:
            print("Execution Error:", e)
            newcoe = preprocess_code_for_openai(modified_code_correct)  # Placeholder function
            print("Execution error removal step 1st")
            corrected_code = handle_openai_error_correction(newcoe, e)  # Placeholder function

            # Final execution attempt after correction
            modified_code_correct = replace_data_with_full_dataset(corrected_code, full_data2)  # Placeholder function
            exec(modified_code_correct, globals())

    # with open('2.py', 'w', encoding='utf-8') as code_file:
    #   code_file.write(modified_code_correct)
      
    return modified_code_correct

def extract_sample_from_data(data_str, num_samples=5):
    """
    Extracts a sample from a large dataset (e.g., list or dictionary) as a string.
    
    Args:
    - data_str (str): String representation of the data (e.g., a list or dictionary).
    - num_samples (int): The number of samples to extract.

    Returns:
    - str: Truncated version of the dataset with 'num_samples' entries.
    """
    try:
        # Try to parse the data string into a Python object
        data = ast.literal_eval(data_str)
        
        if isinstance(data, list):
            # If it's a list, slice it to get a smaller sample
            return str(data[:num_samples])
        elif isinstance(data, dict):
            # If it's a dictionary, sample the first 'num_samples' items
            return str(dict(list(data.items())[:num_samples]))
        else:
            # If it's not a list or dict, return the original (small enough)
            return data_str
    except Exception as e:
        print(f"Error parsing data for sampling: {e}")
        return data_str

def preprocess_code_for_openai(generated_code):
    """
    Preprocesses the generated code by identifying large datasets and replacing them with smaller samples.
    
    Args:
    - generated_code (str): The dynamically generated Python code.

    Returns:
    - str: The preprocessed code with datasets truncated or replaced with smaller samples.
    """
    # Use regex to find 'data = [...]' or 'data = {...}' or similar assignments
    data_pattern = re.compile(r'(data\s*=\s*)(\[.*?\]|\{.*?\})', re.DOTALL)

    # Find all dataset assignments and truncate them
    def replace_data(match):
        # Extract the full dataset (match group 2) and replace it with a sample
        original_data = match.group(2)
        truncated_data = extract_sample_from_data(original_data, num_samples=5)
        return match.group(1) + truncated_data

    # Replace large datasets with smaller samples
    truncated_code = data_pattern.sub(replace_data, generated_code)
    
    return truncated_code

def handle_openai_error_correction(code_with_error, error_message):
    """
    Sends the code and error message to OpenAI's API for correction, 
    requesting only error corrections without altering data structures.
    
    Parameters:
    - code_with_error (str): The code containing execution errors.
    - error_message (str): The specific error message encountered.
    
    Returns:
    - str: The corrected code as suggested by OpenAI, if available.
    """
    # Define the prompt with the necessary instructions for correction
    prompt = f"""
            The following Python code contains a execution error. Correct only the execution errors without modifying the structure, content, or length of any arrays, lists, or dictionaries in the code. 

            The 'data' variable has been truncated for simplicity, but **DO NOT** modify or reduce any data structures in the code. Only correct the execution error.
            do not rename anything also
            
            Code:
            ```python
            {code_with_error}
            ```
            {error_message}
            After correction, the code must be returned **without any changes** to the structure or values of global arrays.
            do not removed for brevity
            i want as it as code i have given only remove execution errors do not trucate any arrays or variables 
            """

    # Make a request to OpenAI API for correction
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Replace with your model choice
            messages=[
                {"role": "system", "content": "You are an expert Python code debugger."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048
        )

        # Extract the corrected code from the response
        corrected_code = response['choices'][0]['message']['content']
        
        # Use regex to isolate the code section if it's returned within ```python code blocks
        code_match = re.search(r"```python(.*?)```", corrected_code, re.DOTALL)
        if code_match:
            corrected_code = code_match.group(1).strip()

        print("Corrected Code from OpenAI:\n", corrected_code)
        return corrected_code

    except Exception as e:
        print("Error in calling OpenAI API:", e)
        return code_with_error  # Return the original code if correction fails
    
def handle_openai_syntax_correction(code_with_syntax_error):
    """
    Sends the code with syntax errors to OpenAI's API for syntax correction, 
    requesting only syntax corrections without altering data structures.
    
    Parameters:
    - code_with_syntax_error (str): The code containing syntax errors.
    
    Returns:
    - str: The corrected code as suggested by OpenAI, if available.
    """
    # Define the prompt with instructions for correcting only syntax errors
    prompt = f"""
        The following Python code contains a syntax error. Correct only the syntax errors without modifying the structure, content, or length of any arrays, lists, or dictionaries in the code. 

        The 'data' variable has been truncated for simplicity, but **DO NOT** modify or reduce any data structures in the code. Only correct the syntax.
        do not rename anything also
        
        Code:
        ```python
        {code_with_syntax_error}
        ```
        After correction, the code must be returned **without any changes** to the structure or values of global arrays.
        do not removed for brevity
        i want as it as code i have given only remove syntax errors do not trucate any arrays or variables 
        """
        
    # Make a request to OpenAI API for syntax correction
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Replace with your model choice
            messages=[
                {"role": "system", "content": "You are an expert Python code debugger."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048
        )

        # Extract the corrected code from the response
        corrected_code = response['choices'][0]['message']['content']
        
        # Use regex to isolate the code section if it's returned within ```python code blocks
        code_match = re.search(r"```python(.*?)```", corrected_code, re.DOTALL)
        if code_match:
            corrected_code = code_match.group(1).strip()

        print("Corrected Code from OpenAI:\n", corrected_code)
        return corrected_code

    except Exception as e:
        print("Error in calling OpenAI API:", e)
        return code_with_syntax_error  # Return the original code if correction fails
    