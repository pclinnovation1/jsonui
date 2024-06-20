import openai
import json
from fpdf import FPDF

# Configure OpenAI API key
openai.api_key = "sk-proj-z0XZHt1zdmPlZyvg6wGYT3BlbkFJEDXnpBKYpAaeIfrMc9mE"

def load_json(file_path):
    with open(file_path, 'r') as f:
        json_data = json.load(f)
    return json_data

def generate_letter(json_data, letter_config):
    letter_type = json_data.get('letter_type')  # Assuming 'letter_type' is in data.json
    
    # Fetch details from data.json
    details = "\n".join([f"{key}: {value}" for key, value in json_data.items()])
    
    # Fetch template from letter_config.json based on letter_type
    template = letter_config.get(letter_type, {}).get('template', '')
    
    # Generate letter content using OpenAI API
    prompt = f"Create a {letter_type} based on the following details:\n{details}"
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=300,
        temperature=0.7
    )
    generated_text = response['choices'][0]['text'].strip()
    
    # Replace placeholders in generated_text with values from json_data
    for key, value in json_data.items():
        placeholder = f"[{key}]"
        generated_text = generated_text.replace(placeholder, str(value))
    
    return generated_text

def create_pdf(letter_content, letterhead_image_path, file_name='generated_letter.pdf'):
    # Create PDF document with letterhead image
    class PDF(FPDF):
        def __init__(self, letterhead_image_path):
            super().__init__()
            self.letterhead_image_path = letterhead_image_path
            self.set_auto_page_break(auto=True, margin=40)
            
        def header(self):
            self.image(self.letterhead_image_path, 0, 0, 210)  # Adjust image dimensions as needed
            self.set_font("Arial", size=12)
            self.cell(0, 50, "", ln=True)  # Space for the letterhead image
        
        def footer(self):
            self.set_y(-30)
            self.set_font("Arial", size=8)
            # self.cell(0, 10, txt="If you choose to accept this offer, please sign and return the enclosed copy of this letter by [Acceptance Deadline].", ln=True, align='C')
            # self.cell(0, 10, txt="@reallygreatsite hello@reallygreatsite.com www.reallygreatsite.com 123-456-7890", ln=True, align='C')

    pdf = PDF(letterhead_image_path)
    pdf.add_page()
    
    # Add generated letter content to PDF
    pdf.set_xy(10, 50)  # Adjust coordinates to position text properly
    pdf.set_font("Arial", size=12)  # Standardize the font and size
    pdf.multi_cell(0, 10, txt=letter_content)  # Adjust line height to standardize spacing
    
    # Output PDF file
    pdf.output(file_name)

if __name__ == '__main__':
    # File paths
    json_file = 'data.json'
    letter_config_file = 'letters_config.json'
    
    # Load JSON data from files
    json_data = load_json(json_file)
    letter_config = load_json(letter_config_file)
    
    # Generate letter content
    letter_content = generate_letter(json_data, letter_config)
    print("Generated Letter Content:\n", letter_content)
    
    # Specify the path to the letterhead image
    letterhead_image_path = r'C:\Users\DELL\Downloads\Letterhead.png'  # Update this to your image path
    
    # Create PDF with letter content and letterhead image
    create_pdf(letter_content, letterhead_image_path)
    print("PDF letter created successfully.")
