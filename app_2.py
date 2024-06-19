import sys
from flask import Flask, request, jsonify, Response, render_template
from werkzeug.utils import secure_filename
import uuid
import logging
from openai_integration import ConversationState, query_openai_chat, convert_text_to_speech, transcribe_audio
from database import create_employee_details_table, insert_employee_details, insert_contact_details
import os
from flask import Flask, request, jsonify, Response, render_template
from werkzeug.utils import secure_filename
import uuid
from reportoutput import reportoutput
from routes import setup_routes


# Configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


app = Flask(__name__)
setup_routes(app)
DATABASE = 'UK_PCL_TEST.db'
app.register_blueprint(reportoutput, url_prefix='/reports')

# Temporary store for audio responses
audio_store = {}
conversation_state = ConversationState()
token_limit = 1000  # Set your token limit here
# Initialize the conversation with the provided context
conversation_state.add_message("system", "Ask user what task he wants to perform. If the task is related to adding employee, then ask these UK employee details one at a time to store them in the database: name, email(should be in proper email format - ask the user if any ambiguity), taxable_ytd (if skiped, take the default value as 0), ni_ytd (if skiped, take the default value as 0), p45_code, salary(note that it is annual salary), bank_account_number, bank_sort_code (should be in UK format), department; and at last, provide the final output for a review in this format enclosed by dual double quotation marks from name to department: \"\"name=Sumanth;email=sumanth@gmail.com;taxable_ytd=4000;ni_ytd=123;p45_code=1257L;salary=100000;bank_account_number=435232342;bank_sort_code=434343;department=Product\"\"")


@app.route('/home')
def home():
    return render_template('index.html')

@app.route("/")
def ai():
    return render_template('ai_speech_to_text.html')

@app.route('/reports/generate-text', methods=['POST'])
def generate_text():
    # Your function implementation here
    return "Functionality here"

@app.route('/conversation', methods=['POST'])
def conversation():
    user_input = request.json.get('message', '')
    logger.debug(f"Received user input for conversation: {user_input}")

    try:
        openai_response, response = query_openai_chat(user_input, conversation_state, token_limit)
        if response is None:
            logger.error("OpenAI chat completion response is None, indicating a failure in the API call.")
            return jsonify({"message": "Failed to process your request.", "audio_url": None}), 500

        logger.info(f"Received response from OpenAI chat: {openai_response}")
        audio_id = str(uuid.uuid4())
        logger.debug(f"Generated audio ID {audio_id} for storing the response.")

        audio_store[audio_id] = openai_response
        logger.info(f"Stored OpenAI response in audio_store under ID {audio_id}.")

        audio_url = f'{request.url_root}stream-audio/{audio_id}'
        logger.info(f"Constructed audio URL for the response: {audio_url}")

        return jsonify({"message": openai_response, "audio_url": audio_url})
    except Exception as e:
        logger.exception("Failed during processing the conversation request.")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/stream-audio/<audio_id>')
def stream_audio(audio_id):
    logger.debug(f"Received request to stream audio for ID: {audio_id}")
    text_response = audio_store.get(audio_id, None)

    if text_response is not None:
        logger.info(f"Found text for audio_id {audio_id}: {text_response}")
        try:
            logger.info("Attempting to convert text to speech.")
            audio_bytes = convert_text_to_speech(text_response)
            if audio_bytes:
                logger.info("Text to speech conversion successful.")
                del audio_store[audio_id]  # Consider deleting after successful transmission or manage cleanup elsewhere
                return Response(audio_bytes, mimetype='audio/mpeg')
            else:
                logger.warning("Text to speech conversion returned no audio data.")
        except Exception as e:
            logger.exception("Failed during text to speech conversion.")
    else:
        logger.warning(f"Audio not found for ID: {audio_id}")

    return jsonify({"error": "Audio not found"}), 404

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    if 'file' not in request.files:
        logger.error("No file part in the request")
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        logger.error("No file selected")
        return jsonify({"error": "No selected file"}), 400
    if file and file.content_type == 'audio/mpeg':
        # Ensure the directory exists
        tmp_dir = os.path.join(os.getcwd(), 'tmp')
        os.makedirs(tmp_dir, exist_ok=True)  # Create tmp directory if it does not exist
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(tmp_dir, filename)  # Save file to temporary directory
        file.save(filepath)
        logger.debug(f"File received and saved to: {filepath}")

        # Process the file for transcription
        transcription = transcribe_audio(filepath)
        if transcription is None:
            return jsonify({"error": "Failed to transcribe audio"}), 500

        return jsonify({"text": transcription})
    else:
        logger.error("Invalid file type: Expected 'audio/mpeg'")
        return jsonify({"error": "Invalid file type. Please upload an MP3 file."}), 400

@app.route('/submit-form', methods=['POST'])
def submit_form():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    
    try:
        insert_contact_details(name, email, message)
        return render_template('thank_you.html')
    except Exception as e:
        logger.exception("Failed to process form submission")
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == '__main__':
    create_employee_details_table()
    app.run(debug=True, host="0.0.0.0", port=8000)
