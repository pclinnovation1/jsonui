# import json
# import os
# from PIL import Image, ImageDraw, ImageFont
# from fpdf import FPDF

# def load_json(file_path):
#     with open(file_path, 'r') as f:
#         json_data = json.load(f)
#     return json_data

# def extract_certificate_details(json_data):
#     recipient_name = json_data.get('Awarded to', 'Recipient Name')
#     course_name = json_data.get('For Completing', 'Course Name')
#     issued_by = json_data.get('Issued By', 'Issuer')
#     completed_on = json_data.get('Completed On', 'Completion Date')
#     actual_effort = json_data.get('Actual Effort', 'Effort')
#     return recipient_name, course_name, issued_by, completed_on, actual_effort

# def load_positions(file_path, template_path):
#     positions_data = load_json(file_path)
#     normalized_template_path = os.path.normpath(template_path)
#     return positions_data.get(normalized_template_path, {})

# def create_certificate_image(recipient_name, course_name, issued_by, completed_on, actual_effort, template_path, positions_file, output_path='certificate_output.png', font_size_large=60, font_size_medium=35, font_size_small=30):
#     # Load positions from the positions file
#     positions = load_positions(positions_file, template_path)

#     # Debug: Print the positions loaded
#     print(f"Loaded positions for template '{template_path}': {positions}")

#     # Check if all necessary positions are present
#     required_keys = ["recipient_name", "course_name", "issued_by", "completed_on", "actual_effort"]
#     for key in required_keys:
#         if key not in positions:
#             raise KeyError(f"Position for '{key}' not found in positions file for template '{template_path}'.")

#     # Load certificate template
#     image = Image.open(template_path)
#     draw = ImageDraw.Draw(image)
    
#     # Set fonts with custom sizes
#     font_large = ImageFont.truetype("georgiab.ttf", font_size_large)
#     font_medium = ImageFont.truetype("georgia.ttf", font_size_medium)
#     font_small = ImageFont.truetype("georgia.ttf", font_size_small)

#     # Draw text on the image
#     draw.text(tuple(positions["recipient_name"]), recipient_name, font=font_large, fill="black", anchor="mm")
#     draw.text(tuple(positions["course_name"]), course_name, font=font_medium, fill="black", anchor="mm")
#     draw.text(tuple(positions["issued_by"]), issued_by, font=font_small, fill="black", anchor="mm")
#     draw.text(tuple(positions["completed_on"]), completed_on, font=font_small, fill="black", anchor="mm")
#     draw.text(tuple(positions["actual_effort"]), actual_effort, font=font_small, fill="black", anchor="mm")

#     # Save the image with the added text
#     image.save(output_path)
#     print(f"Certificate saved to {output_path}")

# def create_pdf_from_image(image_path, output_pdf_path='certificate_output.pdf'):
#     # Create a PDF document
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.image(image_path, x=0, y=0, w=210, h=297)  # A4 size
#     pdf.output(output_pdf_path)
#     print(f"PDF saved to {output_pdf_path}")

# if __name__ == '__main__':
#     # File paths
#     json_file = r'.\data.json'
#     # template_path = r'.\Certificate-1.png'
#     template_path = r'.\course_completion_certificate_template-1.png'
#     positions_file = r'.\positions.json'
    
#     # Load JSON data from file
#     json_data = load_json(json_file)
    
#     # Extract certificate details from JSON data
#     recipient_name, course_name, issued_by, completed_on, actual_effort = extract_certificate_details(json_data)
    
#     # Create certificate image
#     create_certificate_image(recipient_name, course_name, issued_by, completed_on, actual_effort, template_path, positions_file)
    
#     # Convert the certificate image to a PDF
#     create_pdf_from_image('certificate_output.png')







import json
import os
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import tempfile

def load_json(file_path):
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    return json_data

def extract_certificate_details(json_data):
    recipient_name = json_data.get('Awarded to', 'Recipient Name')
    course_name = json_data.get('For Completing', 'Course Name')
    issued_by = json_data.get('Issued By', 'Issuer')
    completed_on = json_data.get('Completed On', 'Completion Date')
    actual_effort = json_data.get('Actual Effort', 'Effort')
    return recipient_name, course_name, issued_by, completed_on, actual_effort

def load_positions(file_path, template_path):
    positions_data = load_json(file_path)
    normalized_template_path = os.path.normpath(template_path)
    return positions_data.get(normalized_template_path, {})

def create_certificate_image(recipient_name, course_name, issued_by, completed_on, actual_effort, template_path, positions_file, font_size_large=60, font_size_medium=35, font_size_small=30):
    # Load positions from the positions file
    positions = load_positions(positions_file, template_path)

    # Debug: Print the positions loaded
    print(f"Loaded positions for template '{template_path}': {positions}")

    # Check if all necessary positions are present
    required_keys = ["recipient_name", "course_name", "issued_by", "completed_on", "actual_effort"]
    for key in required_keys:
        if key not in positions:
            raise KeyError(f"Position for '{key}' not found in positions file for template '{template_path}'.")

    # Load certificate template
    image = Image.open(template_path)
    draw = ImageDraw.Draw(image)
    
    # Set fonts with custom sizes
    font_large = ImageFont.truetype("georgiab.ttf", font_size_large)
    font_medium = ImageFont.truetype("georgia.ttf", font_size_medium)
    font_small = ImageFont.truetype("georgia.ttf", font_size_small)

    # Draw text on the image
    draw.text(tuple(positions["recipient_name"]), recipient_name, font=font_large, fill="black", anchor="mm")
    draw.text(tuple(positions["course_name"]), course_name, font=font_medium, fill="black", anchor="mm")
    draw.text(tuple(positions["issued_by"]), issued_by, font=font_small, fill="black", anchor="mm")
    draw.text(tuple(positions["completed_on"]), completed_on, font=font_small, fill="black", anchor="mm")
    draw.text(tuple(positions["actual_effort"]), actual_effort, font=font_small, fill="black", anchor="mm")

    return image

def create_pdf_from_image(image, output_pdf_path='certificate_output.pdf'):
    # Save the image to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_image_file:
        image.save(temp_image_file, format='PNG')
        temp_image_path = temp_image_file.name
    
    # Create a PDF document
    pdf = FPDF()
    pdf.add_page()
    pdf.image(temp_image_path, x=0, y=0, w=210, h=297)  # A4 size
    pdf.output(output_pdf_path)
    print(f"PDF saved to {output_pdf_path}")
    
    # Clean up the temporary image file
    os.remove(temp_image_path)

if __name__ == '__main__':
    # File paths
    json_file = r'.\data.json'
    template_path = r'.\course_completion_certificate_template-1.png'
    positions_file = r'.\positions.json'
    
    # Load JSON data from file
    json_data = load_json(json_file)
    
    # Loop through each entry in the JSON data
    for i, entry in enumerate(json_data):
        # Extract certificate details from JSON data
        recipient_name, course_name, issued_by, completed_on, actual_effort = extract_certificate_details(entry)
        
        # Create certificate image
        certificate_image = create_certificate_image(recipient_name, course_name, issued_by, completed_on, actual_effort, template_path, positions_file)
        
        # Define output PDF path
        pdf_output_path = f'certificate_output_{i}.pdf'
        
        # Convert the certificate image to a PDF
        create_pdf_from_image(certificate_image, output_pdf_path=pdf_output_path)
