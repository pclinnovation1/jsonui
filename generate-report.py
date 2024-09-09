import openai
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, request, send_file, jsonify
from io import BytesIO
from pymongo import MongoClient
from report_mapping import report_fields_mapping
import re
import json
# Set your OpenAI API key
openai.api_key = ''  # Replace with your actual OpenAI API key
 
app = Flask(__name__)
 
client = MongoClient('')  # Modify according to your MongoDB setup
db = client['']
 
 
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
    You are a Python coding assistant. Based on the report type "{report_type}" and the provided JSON data for 50 employees, generate Python code to create a suitable bar graph using matplotlib.

    Here is the user-provided description of the graph:
    "{description}"

    JSON Data:
    {data}

    Instructions:
    - Use the exact field names as provided in the JSON data.
    - The x-axis should represent the relevant field based on the user description, and the y-axis should represent the count or relevant values.
    - Label the x-axis and y-axis based on the user-provided description.
    - Title the graph as per the user’s description.
    - Ensure all labels are readable and include grid lines along the y-axis for better readability.
    - Save the graph as 'graph_output.png'.
    - Write a generic code with the user-provided description and also write algorithms if needed because we will use this code with large data points.
    - Make sure the Python code uses the exact field names provided in the JSON data, as this code will be dynamically applied to the full dataset of all employees with the same fields. Do not change any field names.
    """

    # Use the new method `completions.create`
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use the appropriate model
        messages=[
            {"role": "system", "content": "You are a helpful assistant for generating Python code for data visualization."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4096  # Increased max_tokens to accommodate longer code for data handling
    )

    # Extract the generated code from the response
    graph_code = response['choices'][0]['message']['content']

    # Extract code part only using regex to remove unwanted instructions
    code_match = re.search(r"```python(.*?)```", graph_code, re.DOTALL)
    if code_match:
        graph_code = code_match.group(1)

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
    # Extract the data section from the generated code using regex
    data_pattern = re.compile(r'data = \[.*?\]', re.DOTALL)
   
    # Prepare the full dataset in the same format as the subset data
    full_data_str = f"data = {full_data}"
   
    # Replace the subset data with the full dataset
    modified_code = re.sub(data_pattern, full_data_str, generated_code)
   
    return modified_code
 



@app.route('/generate-report', methods=['POST'])
def generate_report():
    request_data = request.get_json()
    report_name = request_data.get('report_name')
    user_description = request_data.get('description')  # User-provided description

    # Fetch the report info from the report_fields_mapping1
    report_info = report_fields_mapping.get(report_name)
    if not report_info:
        return jsonify({"error": "Invalid report name provided."}), 400

    # Initialize report_data and full_data
    report_data = []
    full_data = []

    # Iterate through collections and fetch data
    for idx, (collection_name, field_names) in enumerate(report_info.items()):
        projection = {field: 1 for field in field_names}
        projection.update({'_id': 0})

        # Fetch limited data for report (50 employees)
        collection_data = list(db[collection_name].find({}, projection).limit(50))

        if idx == 0:
            # Initialize report_data with the first collection
            report_data = collection_data
        else:
            # Merge this collection's data with the report_data based on 'person_name'
            collection_data_dict = {employee['person_name']: employee for employee in collection_data}

            for employee in report_data:
                person_name = employee.get('person_name')
                if person_name and person_name in collection_data_dict:
                    # Merge fields from this collection's data into report_data
                    for key in field_names:
                        employee[key] = collection_data_dict[person_name].get(key, None)

    # Get dynamic graph code from OpenAI using the data for 50 employees and the user description
    graph_code = get_dynamic_graph_code(report_name, report_data, user_description)

    print('Graph Code:', graph_code)

    # Fetch full data from all collections (without limiting to 50 employees)
    for idx, (collection_name, field_names) in enumerate(report_info.items()):
        projection = {field: 1 for field in field_names}
        projection.update({'_id': 0})

        # Fetch full dataset from each collection
        collection_data = list(db[collection_name].find({}, projection))

        if idx == 0:
            # Initialize full_data with the first collection
            full_data = collection_data
        else:
            # Merge this collection's data with the full_data based on 'person_name'
            collection_data_dict = {employee['person_name']: employee for employee in collection_data}

            for employee in full_data:
                person_name = employee.get('person_name')
                if person_name and person_name in collection_data_dict:
                    # Merge fields from this collection's data into full_data
                    for key in field_names:
                        employee[key] = collection_data_dict[person_name].get(key, None)

    # Replace the 50 employee data with the full dataset in the generated code
    modified_code = replace_data_with_full_dataset(graph_code, full_data)

    print('Modified Code:', modified_code)

    # Execute the dynamically generated and modified code
    local_scope = {}
    exec(modified_code, {"plt": plt}, local_scope)

    # Read the generated graph from the file
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return send_file(buf, mimetype='image/png')




 
if __name__ == "__main__":
    app.run(debug=True)
 
 
 
#All graph generation on bigger data(more than 100 employee) use this approach until find any better approach. If anyone find any better approach then notify.