

 
# #All graph generation on bigger data(more than 100 employee) use this approach until find any better approach. If anyone find any better approach then notify.
import openai
import pandas as pd
import matplotlib.pyplot as plt
from flask import Blueprint, request, send_file, jsonify, url_for, render_template
from io import BytesIO
from pymongo import MongoClient
from HR_graph_fields import generate_graph_fields
import re
import os
import uuid
import openai
from flask import Flask, request, send_file, jsonify
import json

app = Flask(__name__)
 
# Set your OpenAI API key
openai.api_key = ''  # Replace with your actual OpenAI API key
 
generate_report = Blueprint('generate_report', __name__)
 
# Directory where images will be saved temporarily
TEMP_IMAGE_FOLDER = "static/temp_images"
 
if not os.path.exists(TEMP_IMAGE_FOLDER):
    os.makedirs(TEMP_IMAGE_FOLDER)
 
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
    You are a Python coding assistant. Based on the graph description and the provided JSON data, generate Python code to create a suitable graph using matplotlib and pandas.
   
    Here is the user-provided description of the graph:
    "{description}"
   
    JSON Data:
    {data}
    Instructions:
    - Use the provided JSON data as-is, ensuring you handle missing values and perform necessary type conversions (e.g., converting date strings to datetime).
    - For any data transformation (e.g., reshaping data for heatmaps, line charts, or bar charts), **use `pivot_table()` for multi-dimensional data aggregation, not `pivot()`**. 
      Ensure that `pivot_table()` uses `index`, `values`, and `aggfunc` parameters correctly.
    - When generating heatmaps or similar visualizations, ensure the code uses `pivot_table()` for creating a valid data structure, and specify appropriate aggregation functions (e.g., `sum`, `mean`).
    - Handle large datasets efficiently by performing aggregation, filtering, or sampling as necessary, ensuring scalability.
    - For visualization, use `matplotlib`, `seaborn`, or `pandas` plotting functions. Select the correct chart type based on the report type or description (e.g., line charts for trends, bar charts for comparisons, heatmaps for distributions).
    - Ensure visualizations work in both GUI and non-GUI environments by using `plt.savefig()` in addition to `plt.show()`.
    - Add appropriate titles, labels, legends, and customize the plot (e.g., axis labels, font sizes, and color schemes) based on the data and report requirements.
    - Validate and clean the data, checking for missing values or invalid data types, and handle errors gracefully (e.g., remove or replace missing data).
    - You can use mathematics to calculate any fields from given data only if required, for example if you need to calculate age group from the given date of birth.
    - Please do not truncate data for simplicity. You can use the full data to generate the graph because you can handle large datasets.
    - This is not for demonstration purposes, so you can use the full data to generate the graph.
    - Do not make any assumptions about the data. You can use the data as-is to generate the graph.
    - Generate Python code that performs data cleaning, handles missing values, and creates graphs for data analysis using `seaborn` and `matplotlib`.
    - Create graphs according to the `{report_type}` and `{description}`.
    - Customize the graphs with titles, labels, and a consistent color palette. Use appropriate libraries and functions to create the graphs.
    """
 
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for generating Python code for data visualization."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=16384
    )
 
    # Extract the generated code from the response
    graph_code = response['choices'][0]['message']['content']
   
    # print("Graph Code initial:", graph_code)
   
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
    print("replace_data_with_full_dataset called")
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
def generate_report2():
    request_data = request.get_json()
    report_name = request_data.get('report_name')
    print("report name : ", report_name)
    print("*"*25)
    user_description = request_data.get('description')  # User-provided description
 
    # Fetch the report info from the report_fields_mapping1
    #report_info = report_fields_mapping.get(report_name)
    report_info = generate_graph_fields(user_description)
    if not report_info:
        return jsonify({"error": "Invalid report name provided."}), 400
 
    # Initialize full_data
    full_data = []
 
    # Fetch full data from all collections (without limiting to 50 employees)
    for idx, (collection_name, field_names) in enumerate(report_info.items()):
        projection = {field: 1 for field in field_names}
        projection.update({'_id': 0})

        print("collection name : ", collection_name)
        print("*"*25)
        # Fetch full dataset from each collection
        #collection_data = list(db[collection_name].find({}, projection).limit(150))
        collection_data = list(db[collection_name].find({}, projection))
        
        print('collection name : ',collection_data)
        print("*"*25)
        print()

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

    print("Full data : ",full_data)
                       
    # Get dynamic graph code from OpenAI using the full data and the user description
    graph_code = get_dynamic_graph_code(report_name, full_data, user_description)

    if graph_code is None:
        # Return an error response if the graph_code could not be generated
        return jsonify({"error": "Failed to generate graph code from OpenAI."}), 500
 
    print('Graph Code:', graph_code)
 
    # Replace the fukk data with the full dataset in the generated code because openai doesn't support large data
    modified_code = replace_data_with_full_dataset(graph_code, full_data)
 
    print('Modified Code:', modified_code)
   
    # Generate a unique filename to save the image
    image_filename = f"{uuid.uuid4().hex}.png"
    image_path = os.path.join(TEMP_IMAGE_FOLDER, image_filename)
 
    # Execute the dynamically generated and modified code
    local_scope = {}
    exec(modified_code, {"plt": plt}, local_scope)
 
    # Read the generated graph from the file
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
   
    # Save the graph to the image path
    plt.savefig(image_path)
    plt.close()
 
    # Generate a URL to access the image in a temporary UI
    image_url = url_for('generate_report.show_image', image_filename=image_filename, _external=True)
    view_image_url = url_for('generate_report.view_image', image_filename=image_filename, _external=True)
 
    # Return a link to view the image in the frontend
    return jsonify({
        "image_url": image_url,
        "view_image_url": view_image_url
    })
 
    # return send_file(buf, mimetype='image/png')
 
# Route to show the image directly (you can access this from the URL)
@generate_report.route('/image/<image_filename>')
def show_image(image_filename):
    image_path = os.path.join(TEMP_IMAGE_FOLDER, image_filename)
    return send_file(image_path, mimetype='image/png')
 
# Route to display the image in a temporary UI
@generate_report.route('/view-image/<image_filename>')
def view_image(image_filename):
    image_url = url_for('generate_report.show_image', image_filename=image_filename, _external=True)
    return render_template('view_image.html', image_url=image_url)
 
 
#All graph generation on bigger data(more than 100 employee) use this approach until find any better approach. If anyone find any better approach then notify.
 

if __name__ == "__main__":
     app.run(debug=True)