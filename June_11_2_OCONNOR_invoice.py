import re
import fitz  # PyMuPDF
import openai
import json
from pymongo import MongoClient

# Set your OpenAI API key
openai.api_key = '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'  # Replace with your OpenAI API key

# Path to the PDF file containing invoices
pdf_path = r'/Users/vishalmeena/Desktop/OFFICE/piyush work/J.OCONNOR _INV.pdf'  # Path to the uploaded PDF file

# Open the PDF file
pdf_document = fitz.open(pdf_path)

# Extract text from the first page of the PDF
page = pdf_document.load_page(0)
extracted_text = page.get_text()

# Print the entire extracted text for debugging
print("Extracted Text from PDF:")
print(extracted_text)

# Manually identify and extract the relevant table lines
lines = extracted_text.split('\n')
start_index = lines.index("Description") + 1
end_index = lines.index("Subtotal")
table_lines = lines[start_index:end_index]

# Combine the extracted table lines into a single string
table_text = "\n".join(table_lines)

# Structure the prompt for OpenAI
prompt = f"""
Extract the following details from the invoice text and provide them in a structured JSON format for each item. If any information is missing, please indicate it as "Not Provided":
- Description
- Quantity
- Unit Price
- VAT
- Amount GBP

Invoice Text:
{table_text}
"""

# Call the OpenAI model with the completion endpoint
response = openai.Completion.create(
    model="gpt-3.5-turbo-instruct",
    prompt=prompt,
    max_tokens=2000,
    temperature=0.7
)

structured_data = response.choices[0].text.strip()

# Convert the structured data directly to a list of dictionaries
try:
    data_list = json.loads(structured_data)
    print("Structured Data from OpenAI:")
    print(data_list)
except json.JSONDecodeError as e:
    print(f"Error decoding JSON for the invoice: {e}")
    data_list = []

# Extract detailed invoice metadata
metadata = {
    "Company Registration No": re.search(r'Company Registration No:\s*(.+)', extracted_text).group(1),
    "Registered Office": re.search(r'Registered Office:\s*(.+)', extracted_text).group(1),
    "Invoice Number": re.search(r'Invoice Number\s*(\d+)', extracted_text).group(1),
    "Invoice Date": re.search(r'Invoice Date\s*(\d{2} \w+ \d{4})', extracted_text).group(1),
    "Reference": re.search(r'Reference\s*(.+)', extracted_text).group(1),
    "VAT Number": re.search(r'VAT Number\s*(\d+)', extracted_text).group(1),
    "Customer Name": re.search(r'^(.*?)(?=2 Estuary Boulevard)', extracted_text, re.MULTILINE).group(1).strip()
}

# Combine metadata and items into a single document
invoice_document = {
    'metadata': metadata,  # Metadata is already a dictionary
    'items': data_list
}

# Print the combined document to check its structure
print("Combined Document:")
print(invoice_document)

# Establish connection to MongoDB
client = MongoClient('mongodb://PCL_Interns_admin:PCLinterns2050admin@172.191.245.199:27017/PCL_Interns')  # Replace with your MongoDB connection string
db = client['PCL_Interns']  # Accessing database named 'mydatabase'

# Upload combined document to MongoDB collection
collection = db['Invoices']
collection.insert_one(invoice_document)

print("Data uploaded to MongoDB collection 'Piyush'.")
