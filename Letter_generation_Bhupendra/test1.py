# import json
# import openai
# import textwrap
# from reportlab.lib.pagesizes import letter as pdf_letter
# from reportlab.pdfgen import canvas

# # Set your OpenAI API key
# openai.api_key = "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"

# # Load letter templates and purposes from JSON config file
# with open('letters_config.json', 'r') as file:
#     letter_config = json.load(file)

# # Load prompt template from JSON file
# with open('prompt_template.json', 'r') as file:
#     prompt_template = json.load(file)["prompt"]

# # Load employee details from JSON file
# with open('employee_details.json', 'r') as file:
#     employee_details = json.load(file)["employees"]

# # Function to generate a letter for a given employee details
# def generate_letter(details, purpose):
#     prompt = prompt_template.format(
#         purpose=purpose,
#         candidate_name=details.get("Candidate Name", "Employee"),
#         job_title=details.get("Job Name", details.get("Job Title", "Job Title")),
#         hiring_manager=details.get("Hiring Manager", "Hiring Manager"),
#         start_date=details.get("Projected Start Date", "Start Date"),
#         work_location=details.get("Work Location", "Work Location"),
#         department=details.get("Department", "Department"),
#         business_unit=details.get("Business Unit", "Business Unit"),
#         legal_employer=details.get("Legal Employer", "Legal Employer"),
#         recruiter=details.get("Recruiter", "Recruiter")
#     )

#     # Call the OpenAI API
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": prompt}
#         ],
#         max_tokens=300
#     )
    
#     # Extract the generated letter from the response
#     letter = response['choices'][0]['message']['content'].strip()
#     return letter

# def save_letters_as_pdf(letters):
   
#      # Create a PDF file
#     c = canvas.Canvas("generated_letters.pdf", pagesize=pdf_letter)
    
#     # Set up formatting for the PDF
#     c.setFont("Helvetica", 12)
    
#     # Define page margins
#     left_margin = 72
#     right_margin = pdf_letter[0] - 72
#     top_margin = pdf_letter[1] - 72
#     bottom_margin = 72
    
#     # Write each letter to a new page in the PDF
#     for idx, entry in enumerate(letters, start=1):
#         details = entry["details"]
#         letter = entry["letter"]

#         if idx > 1:
#             c.showPage()  # Start a new page for each letter after the first one
        
#         # Adjust the y_position for each letter
#         y_position = top_margin  # Starting y-position for the content of the letter
        
#         # Add standard letter formatting
#         c.drawString(left_margin, y_position, "Your Company Name")
#         y_position -= 20
#         c.drawString(left_margin, y_position, "Company Address Line 1")
#         y_position -= 15
#         c.drawString(left_margin, y_position, "Company Address Line 2")
#         y_position -= 15
#         c.drawString(left_margin, y_position, "City, State, Zip Code")
#         y_position -= 30
        
#         c.drawString(left_margin, y_position, f"Date: {details.get('Projected Start Date', 'Start Date')}")
#         y_position -= 30
        
#         c.drawString(left_margin, y_position, f"Generated Letter {idx}:")
#         y_position -= 20  # Move down for the title
        
#         lines = letter.split('\n')
        
#         # Write the content of the letter
#         for line in lines:
#             # Wrap the line if it exceeds the width
#             wrapped_lines = textwrap.wrap(line, width=95)  # Adjust width as necessary
#             for wrapped_line in wrapped_lines:
#                 if y_position < bottom_margin:
#                     c.showPage()  # Move to the next page if content goes out of bounds
#                     y_position = top_margin  # Reset y_position for the new page
#                 c.drawString(left_margin, y_position, wrapped_line)
#                 y_position -= 15  # Move down for each line of text
        
#         # Add space after each letter
#         y_position -= 20

#         # Add standard footer information
#         c.drawString(left_margin, y_position, "[Your Name]")
#         y_position -= 15
#         c.drawString(left_margin, y_position, "[Your Title]")
#         y_position -= 15
#         c.drawString(left_margin, y_position, "[Department]")
#         y_position -= 15
#         c.drawString(left_margin, y_position, "[Email]")
#         y_position -= 15
#         c.drawString(left_margin, y_position, "[Phone Number]")
    
#     # Save the PDF
#     c.save()


# if __name__ == "__main__":
#     letters = []
    
#     # Iterate over each employee and generate letters
#     for details in employee_details:
#         letter_type = details["Letter Type"]

#         # Determine the purpose based on the letter_type
#         purpose = letter_config['letters'].get(letter_type, {}).get('purpose', 'generic letter')

#         # Generate the letter
#         letter = generate_letter(details, purpose)
#         letters.append({
#             "details": details,
#             "letter": letter
#         })

#     # Save all generated letters into a single PDF file, each on a separate page
#     save_letters_as_pdf(letters)

#     # Save generated letters to a JSON file
#     with open('generated_letters.json', 'w') as file:
#         json.dump(letters, file, indent=4)
    
#     # Print the generated letters
#     # print(json.dumps(letters, indent=4))

#     print("Generated letters saved to generated_letters.pdf and generated_letters.json")










import json
import openai
import textwrap
from reportlab.lib.pagesizes import letter as pdf_letter
from reportlab.pdfgen import canvas

# Set your OpenAI API key
openai.api_key = "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"

# Load letter templates and purposes from JSON config file
with open('letters_config.json', 'r') as file:
    letter_config = json.load(file)

# Load prompt template from JSON file
with open('prompt_template.json', 'r') as file:
    prompt_template = json.load(file)["prompt"]

# Load employee details from JSON file
with open('employee_details.json', 'r') as file:
    employee_details = json.load(file)["employees"]

# Function to generate a letter for a given employee details
def generate_letter(details, purpose):
    prompt = prompt_template.format(
        purpose=purpose,
        candidate_name=details.get("Candidate Name", "Employee"),
        job_title=details.get("Job Name", details.get("Job Title", "Job Title")),
        hiring_manager=details.get("Hiring Manager", "Hiring Manager"),
        start_date=details.get("Projected Start Date", "Start Date"),
        work_location=details.get("Work Location", "Work Location"),
        department=details.get("Department", "Department"),
        business_unit=details.get("Business Unit", "Business Unit"),
        legal_employer=details.get("Legal Employer", "Legal Employer"),
        recruiter=details.get("Recruiter", "Recruiter")
    )

    # Call the OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )
    
    # Extract the generated letter from the response
    letter = response['choices'][0]['message']['content'].strip()
    return letter

def save_letters_as_pdf(letters):
    # Create a PDF file
    c = canvas.Canvas("generated_letters.pdf", pagesize=pdf_letter)
    
    # Set up formatting for the PDF
    c.setFont("Helvetica", 12)
    
    # Define page margins
    left_margin = 72
    right_margin = pdf_letter[0] - 72
    top_margin = pdf_letter[1] - 72
    bottom_margin = 72
    
    # Write each letter to a new page in the PDF
    for idx, entry in enumerate(letters, start=1):
        details = entry["details"]
        letter = entry["letter"]

        if idx > 1:
            c.showPage()  # Start a new page for each letter after the first one
        
        # Adjust the y_position for each letter
        y_position = top_margin  # Starting y-position for the content of the letter
        
        # Add standard letter formatting
        c.drawString(left_margin, y_position, "Your Company Name")
        y_position -= 20
        c.drawString(left_margin, y_position, "Company Address Line 1")
        y_position -= 15
        c.drawString(left_margin, y_position, "Company Address Line 2")
        y_position -= 15
        c.drawString(left_margin, y_position, "City, State, Zip Code")
        y_position -= 30
        
        c.drawString(left_margin, y_position, f"Date: {details.get('Projected Start Date', 'Start Date')}")
        y_position -= 30
        
        c.drawString(left_margin, y_position, f"Generated Letter {idx}:")
        y_position -= 20  # Move down for the title
        
        # Adding extra spaces for the header section as in the screenshot
        header_info = [
            "[Your Company Letterhead]",
            "[Date]",
            details.get("Candidate Name", ""),
            details.get("Hiring Manager", ""),
            details.get("Legal Employer", ""),
            "[Company Address]",
            details.get("Work Location", "")
        ]
        
        for header in header_info:
            c.drawString(left_margin, y_position, header)
            y_position -= 15
        
        # Add an extra space before starting the letter content
        y_position -= 20
        
        lines = letter.split('\n')
        
        # Write the content of the letter
        for line in lines:
            # Check for subject line and add extra space after it
            if line.startswith("Subject:"):
                c.drawString(left_margin, y_position, line)
                y_position -= 20  # Extra space after subject line
            else:
                # Wrap the line if it exceeds the width
                wrapped_lines = textwrap.wrap(line, width=95)  # Adjust width as necessary
                for wrapped_line in wrapped_lines:
                    if y_position < bottom_margin:
                        c.showPage()  # Move to the next page if content goes out of bounds
                        y_position = top_margin  # Reset y_position for the new page
                    c.drawString(left_margin, y_position, wrapped_line)
                    y_position -= 15  # Move down for each line of text
        
        # Add space after each letter
        y_position -= 20

        # Add standard footer information only once
        c.drawString(left_margin, y_position, "Kind regards,")
        y_position -= 15
        c.drawString(left_margin, y_position, "[Your Name]")
        y_position -= 15
        c.drawString(left_margin, y_position, "[Your Title]")
        y_position -= 15
        c.drawString(left_margin, y_position, "[Department]")
        y_position -= 15
        c.drawString(left_margin, y_position, "[Email]")
        y_position -= 15
        c.drawString(left_margin, y_position, "[Phone Number]")
    
    # Save the PDF
    c.save()

if __name__ == "__main__":
    letters = []
    
    # Iterate over each employee and generate letters
    for details in employee_details:
        letter_type = details["Letter Type"]

        # Determine the purpose based on the letter_type
        purpose = letter_config['letters'].get(letter_type, {}).get('purpose', 'generic letter')

        # Generate the letter
        letter = generate_letter(details, purpose)
        letters.append({
            "details": details,
            "letter": letter
        })

    # Save all generated letters into a single PDF file, each on a separate page
    save_letters_as_pdf(letters)

    # Save generated letters to a JSON file
    with open('generated_letters.json', 'w') as file:
        json.dump(letters, file, indent=4)
    
    print("Generated letters saved to generated_letters.pdf and generated_letters.json")
