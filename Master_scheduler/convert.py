import os
from fpdf import FPDF
from datetime import datetime
from threading import Thread

def convert_log_to_pdf(log_filepath):
    try:
        with open(log_filepath, 'r') as file:
            lines = file.readlines()
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for line in lines:
            pdf.cell(200, 10, txt=line, ln=True)
        
        pdf_output_path = log_filepath.replace('.log', '.pdf')
        pdf.output(pdf_output_path)
        return pdf_output_path

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None

def run_task(task_name, log_filepath):
    print(f"Running {task_name} with params: ()")
    pdf_filepath = convert_log_to_pdf(log_filepath)
    if pdf_filepath:
        print(f"{task_name} log saved as {pdf_filepath}")
    else:
        print(f"Failed to convert log for {task_name}")

def main():
    tasks = [
        ("calculate_accruals_and_balances", "logs\\Calculate_Accruals_and_Balances_20240624_193915.log"),
        ("update_accrual_plan_enrollments", "logs\\Update_Accrual_Plan_Enrollments_20240624_193915.log"),
        ("evaluate_certification_updates", "logs\\Evaluate_Certification_Updates_20240624_193915.log")
    ]

    threads = []
    for task_name, log_filepath in tasks:
        thread = Thread(target=run_task, args=(task_name, log_filepath))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
