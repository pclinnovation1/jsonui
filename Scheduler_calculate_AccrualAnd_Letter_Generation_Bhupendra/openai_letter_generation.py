# import openai
# import json
# from fpdf import FPDF

# # Configure OpenAI API key
# openai.api_key = "sk-proj-rA3HFQjuD7OljqVUA3h4T3BlbkFJEx9yd9Q0uwkNWpdD8AXM"

# def load_json(file_path):
#     with open(file_path, 'r') as f:
#         json_data = json.load(f)
#     return json_data

# def generate_letter(json_data, letter_config):
#     letter_type = json_data.get('letter_type')  # Assuming 'letter_type' is in data.json
    
#     # Fetch details from data.json
#     details = "\n".join([f"{key}: {value}" for key, value in json_data.items()])
    
#     # Fetch template from letter_config.json based on letter_type
#     template = letter_config.get(letter_type, {}).get('template', '')
    
#     # Generate letter content using OpenAI API
#     prompt = f"Create a {letter_type} based on the following details:\n{details}"
#     response = openai.Completion.create(
#         engine="gpt-3.5-turbo-instruct",
#         prompt=prompt,
#         max_tokens=300,
#         temperature=0.7
#     )
#     generated_text = response['choices'][0]['text'].strip()
    
#     # Replace placeholders in generated_text with values from json_data
#     for key, value in json_data.items():
#         placeholder = f"[{key}]"
#         generated_text = generated_text.replace(placeholder, str(value))
    
#     return generated_text

# def create_pdf(letter_content, letterhead_image_path, file_name='generated_letter.pdf'):
#     # Create PDF document with letterhead image
#     class PDF(FPDF):
#         def __init__(self, letterhead_image_path):
#             super().__init__()
#             self.letterhead_image_path = letterhead_image_path
#             self.set_auto_page_break(auto=True, margin=40)
            
#         def header(self):
#             self.image(self.letterhead_image_path, 0, 0, 210)  # Adjust image dimensions as needed
#             self.set_font("Arial", size=12)
#             self.cell(0, 50, "", ln=True)  # Space for the letterhead image
        
#         def footer(self):
#             self.set_y(-30)
#             self.set_font("Arial", size=8)
#             # self.cell(0, 10, txt="If you choose to accept this offer, please sign and return the enclosed copy of this letter by [Acceptance Deadline].", ln=True, align='C')
#             # self.cell(0, 10, txt="@reallygreatsite hello@reallygreatsite.com www.reallygreatsite.com 123-456-7890", ln=True, align='C')

#     pdf = PDF(letterhead_image_path)
#     pdf.add_page()
    
#     # Add generated letter content to PDF
#     pdf.set_xy(10, 50)  # Adjust coordinates to position text properly
#     pdf.set_font("Arial", size=12)  # Standardize the font and size
#     pdf.multi_cell(0, 10, txt=letter_content)  # Adjust line height to standardize spacing
    
#     # Output PDF file
#     pdf.output(file_name)

# if __name__ == '__main__':
#     # File paths
#     json_file = 'data.json'
#     letter_config_file = 'letters_config.json'
    
#     # Load JSON data from files
#     json_data = load_json(json_file)
#     letter_config = load_json(letter_config_file)
    
#     # Generate letter content
#     letter_content = generate_letter(json_data, letter_config)
#     print("Generated Letter Content:\n", letter_content)
    
#     # Specify the path to the letterhead image
#     letterhead_image_path = r'C:\Users\DELL\Downloads\Letterhead.png'  # Update this to your image path
    
#     # Create PDF with letter content and letterhead image
#     create_pdf(letter_content, letterhead_image_path)
#     print("PDF letter created successfully.")


























import openai
from fpdf import FPDF
import gridfs
from pymongo import MongoClient
from bson import ObjectId
import logging
from datetime import datetime, timezone
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='letter_generation.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Configure OpenAI API key
openai.api_key = "sk-proj-iGXpSyV0DuezfSiWyWxXT3BlbkFJqrtzCXe0J05YEc5r5CQr"

# Set up MongoDB client
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')
db = client['PCL_Interns']
process_details_collection = db['Results_Collection']
client_collection = db['Client_Collection2']
processes_collection = db['Processes_Collection2']
fs = gridfs.GridFS(db)

# Load letter configurations from JSON file
with open('letters_config.json', 'r') as f:
    letter_config = json.load(f)

# Function to generate letter
def generate_letter(parameters, letter_config):
    letter_type = parameters.get('letter_type')
    template = letter_config.get('letters', {}).get(letter_type, {}).get('purpose', '')
   
    logging.info(f"Generating content for {letter_type} with template: {template}")
    prompt = f"Create a {letter_type} based on the following template and details:\nTemplate: {template}\nDetails:\n"
    details = "\n".join([f"{key}: {value}" for key, value in parameters.items()])
    prompt += details
    
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=300,
        temperature=0.7
    )
    generated_text = response['choices'][0]['text'].strip()

    for key, value in parameters.items():
        placeholder = f"[{key}]"
        generated_text = generated_text.replace(placeholder, str(value))
   
    logging.info("Letter content generated successfully")
    print("Letter content generated successfully")
    return generated_text

# Function to create PDF
def create_pdf(letter_content, letterhead_image_path, file_name='generated_letter.pdf'):
    class PDF(FPDF):
        def __init__(self, letterhead_image_path):
            super().__init__()
            self.letterhead_image_path = letterhead_image_path
            self.set_auto_page_break(auto=True, margin=40)
       
        def header(self):
            self.image(self.letterhead_image_path, 0, 0, 210)
            self.set_font("Arial", size=12)
            self.cell(0, 50, "", ln=True)
       
        def footer(self):
            self.set_y(-30)
            self.set_font("Arial", size=8)

    pdf = PDF(letterhead_image_path)
    pdf.add_page()
    pdf.set_xy(10, 50)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=letter_content)
    pdf.output(file_name)
    print(f"PDF created and saved as {file_name}")

# Function to read log file
def read_log_file(log_filepath):
    with open(log_filepath, 'r') as file:
        return file.read()

# Function to find person number
def find_person_number(db, first_name, last_name, job_title):
    """ Find the Person_Number based on First_Name, Last_Name, and Job_Title """
    employee = db['S_EmployeeDetails_UK'].find_one({"First_Name": first_name, "Last_Name": last_name, "Job_Title": job_title})
    if employee:
        logging.info(f"Employee found: {employee['First_Name']} {employee['Last_Name']} with Person Number: {employee['Person_Number']}")
        return employee.get('Person_Number')
    else:
        logging.error("Employee not found.")
        return None

# Function to run letter generation
def run_letter_generation(parameters, letter_config, letterhead_image_path, db, process_details_id):
    print(f"Parameters received by run_letter_generation: {parameters}")
    first_name, last_name = parameters['employee_name'].split()[:2]  # Adjust splitting logic if necessary
    person_number = find_person_number(db, first_name, last_name, parameters['position'])
    if not person_number:
        logging.error("Person number not found for given parameters.")
        return "Failed"

    # Update parameters to include the found Person_Number
    parameters['person_number'] = person_number

    # Print the matching person number
    print(f"Matching Person Number: {person_number}")

    status = "Failed"
    try:
        letter_content = generate_letter(parameters, letter_config)
        file_name = f"{parameters.get('letter_type', 'generated_letter')}.pdf"
        create_pdf(letter_content, letterhead_image_path, file_name)
       
        with open(file_name, 'rb') as pdf_file:
            fs.put(pdf_file, filename=file_name)
        logging.info(f"PDF file {file_name} uploaded to MongoDB GridFS")
        status = "Completed"
    except Exception as e:
        logging.error(f"An error occurred in run_letter_generation: {e}")
        status = "Failed"
    finally:
        process_details_collection.update_one(
            {'_id': process_details_id},
            {'$set': {
                'Completion Time': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'Status': status,
                'Log Details': read_log_file('letter_generation.log')
            }}
        )
        return status

if __name__ == '__main__':
    parameters = {
        "letter_type": "OfferLetterTemplate",
        "employee_name": "John Doe",
        "position": "Software Developer"
    }
    letterhead_image_path = r'letterhead.png'
    process_details_id = ObjectId()  # Replace with actual ObjectId from your process
    status = run_letter_generation(parameters, letter_config, letterhead_image_path, db, process_details_id)
    logging.info(f"Letter generation process completed with status: {status}")
    print(f"Letter generation process completed with status: {status}")
