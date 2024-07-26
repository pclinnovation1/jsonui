import pytesseract
from PIL import Image
import openai
import pandas as pd
import json

# Set your OpenAI API key
openai.api_key = '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'  # Replace with your OpenAI API key

# Path to the image file
image_path = r'C:\Users\HP\Downloads\Updates\I_2_page-0001.jpg'  # Path to the uploaded image file

# Open the image file
img = Image.open(image_path)

# Use Tesseract to do OCR on the image
extracted_text = pytesseract.image_to_string(img)

# Print the entire extracted text for debugging
print("Extracted Text from Image:")
print(extracted_text)

# Structure the prompt for OpenAI
prompt = f"""
Extract the following details from the invoice text and provide them in a structured JSON format for each item. If any information is missing, please indicate it as "Not Provided":
- Property Reference
- Supplier name
- Demand Date
- Amount Due
- Balance Brought Forward
- Account Balance
- Due Date
- Business Unit
- Unique code
- Sender's address
- Reciever's address
- Invoice type

Invoice Text:
{extracted_text}
"""

# Call the OpenAI model with the completion endpoint
response = openai.Completion.create(
    model="gpt-3.5-turbo-instruct",
    prompt=prompt,
    max_tokens=1000,
    temperature=0.7
)

structured_data = response.choices[0].text.strip()

# Print the structured data for debugging
print("Structured Data from GPT-3.5:")
print(structured_data)

# Convert the structured data directly to a list of dictionaries
try:
    data = json.loads(structured_data)
    if isinstance(data, dict):
        data = [data]  # Ensure data is a list of dictionaries
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
    data = []

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(data)

# Save to Excel
output_path = r'C:\Users\HP\Downloads\Updates\extracted_invoice_data_image.xlsx'
df.to_excel(output_path, index=False)

print(f"Data saved to {output_path}")












