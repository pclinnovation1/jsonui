# report_generator.py

from fpdf import FPDF
import json
from datetime import datetime

def create_report_pdf(parameters, task_name, file_name, start_time, end_time, duration, status, log_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_margins(10, 10, 10)

    # Report Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Scheduler Task Report", ln=True, align='C')
    pdf.ln(10)
    
    # General Information
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "1. General Information:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Report Title: Scheduler Task Report", ln=True)
    pdf.cell(200, 10, f"Generation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(200, 10, "Prepared By: Automated Scheduler System", ln=True)
    pdf.ln(10)
    
    # Task Details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "2. Task Details:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Task Name: {task_name}", ln=True)
    pdf.cell(200, 10, f"Description: {parameters.get('description', 'No description provided')}", ln=True)
    
    # Parameters
    pdf.cell(200, 10, "Parameters:", ln=True)
    pdf.set_font("Arial", size=10)
    parameters_json = json.dumps(parameters, indent=4)
    for line in parameters_json.splitlines():
        pdf.cell(200, 10, line, ln=True)
    
    pdf.ln(10)

    # Execution Details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "3. Execution Details:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Start Time: {start_time}", ln=True)
    pdf.cell(200, 10, f"End Time: {end_time}", ln=True)
    pdf.cell(200, 10, f"Duration: {duration}", ln=True)
    pdf.cell(200, 10, f"Status: {status}", ln=True)
    pdf.cell(200, 10, f"Next Scheduled Time: {parameters.get('next_scheduled_time', 'Not Available')}", ln=True)
    pdf.ln(10)

    # Performance Metrics
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "4. Performance Metrics:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Execution Time: Detailed in log content", ln=True)
    pdf.cell(200, 10, "Resource Usage: Not Implemented", ln=True)
    pdf.ln(10)

    # Logs
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "5. Logs:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Log Summary: See attached log content", ln=True)
    pdf.cell(200, 10, f"Log File Links: {log_content}", ln=True)
    pdf.ln(10)

    pdf_output = pdf.output(dest='S').encode('latin1')  # Get PDF output as bytes
    return pdf_output
