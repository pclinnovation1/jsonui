from flask import Flask, request, jsonify, send_file, Blueprint
from pymongo import MongoClient
from datetime import datetime
import pdfkit
import config

payslip_blueprint = Blueprint('payslip', __name__)

# Establish connection to MongoDB
client = MongoClient(config.MONGODB_URI)
db = client[config.DATABASE_NAME]
employee_details_collection = db['OD_oras_employee_details']
salary_details_collection = db['salary_details']

# Configure pdfkit
path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # Adjust this path as necessary
config_pdfkit = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

def generate_payslip(employee, salary_details):
    # Create HTML content for the payslip
    html_content = f"""
    <html>
    <head>
        <style>
            table, th, td {{
                border: 1px solid black;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 8px;
                text-align: left;
            }}
            .header {{
                width: 100%;
                text-align: left;
                border: none;
            }}
            .header img {{
                width: 100px;
            }}
            .header div {{
                display: inline-block;
                vertical-align: top;
            }}
            .company-info {{
                text-align: center;
                margin-bottom: 20px;
            }}
            .summary-table {{
                width: 100%;
                margin-bottom: 20px;
            }}
            .summary-table td {{
                border: none;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h2>PayrollCloud Corp Limited</h2>
                <p>380015, Shivalik Shilp-II, Satellite Road, Ahmedabad</p>
            </div>
        </div>
        <h3>Payslip for the Month of {salary_details['month_year']}</h3>
        <table class="summary-table">
            <tr>
                <td>Employee Name:</td>
                <td>{employee['person_name']}</td>
            </tr>
            <tr>
                <td>Department:</td>
                <td>{employee['department']}</td>
            </tr>
            <tr>
                <td>Pay Period:</td>
                <td>{salary_details['month_year']}</td>
            </tr>
            <tr>
                <td>Worked Days:</td>
                <td>{salary_details['worked_days']}</td>
            </tr>
        </table>
        <table style="width: 100%; margin-bottom: 20px;">
            <thead>
                <tr>
                    <th>EARNINGS</th>
                    <th>AMOUNT</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Basic</td>
                    <td>{salary_details['basic']}</td>
                </tr>
                <tr>
                    <td>HRA</td>
                    <td>{salary_details['hra']}</td>
                </tr>
                <tr>
                    <td>Special Allowance</td>
                    <td>{salary_details['special_allowance']}</td>
                </tr>
                <tr>
                    <td>Gross Earnings</td>
                    <td>{salary_details['gross_earnings']}</td>
                </tr>
            </tbody>
        </table>
        <table style="width: 100%; margin-bottom: 20px;">
            <thead>
                <tr>
                    <th>DEDUCTIONS</th>
                    <th>AMOUNT</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>PF</td>
                    <td>{salary_details['pf']}</td>
                </tr>
                <tr>
                    <td>Professional Tax</td>
                    <td>{salary_details['professional_tax']}</td>
                </tr>
                <tr>
                    <td>Income Tax</td>
                    <td>{salary_details['income_tax']}</td>
                </tr>
                <tr>
                    <td>Total Deductions</td>
                    <td>{salary_details['total_deductions']}</td>
                </tr>
            </tbody>
        </table>
        <table style="width: 100%; margin-bottom: 20px;">
            <thead>
                <tr>
                    <th>NETPAY</th>
                    <th>AMOUNT</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Gross Earnings</td>
                    <td>{salary_details['gross_earnings']}</td>
                </tr>
                <tr>
                    <td>Total Deductions</td>
                    <td>{salary_details['total_deductions']}</td>
                </tr>
                <tr>
                    <td>Total Net Payable</td>
                    <td>{salary_details['net_pay']}</td>
                </tr>
            </tbody>
        </table>
        <p>Total Net Payable: ₹{salary_details['net_pay']}</p>
        <p>**Total Net Payable = Gross Earnings - Total Deductions + Total Reimbursements</p>
    </body>
    </html>
    """
    
    # Generate PDF from HTML content
    pdf_file = f"payslip_{employee['person_number']}_{salary_details['month_year'].replace(' ', '_')}.pdf"
    pdfkit.from_string(html_content, pdf_file, configuration=config_pdfkit)
    
    return pdf_file

@payslip_blueprint.route('/download_payslip', methods=['POST'])
def download_payslip():
    try:
        data = request.get_json()
        person_name = data['person_name']
        month = data['month']
        year = data['year']

        # Fetch employee details
        employee = employee_details_collection.find_one({"person_name": person_name})
        if not employee:
            return jsonify({"error": "Employee not found"}), 404

        # Combine month and year
        month_year = f"{month} {year}"

        # Fetch salary details for the given month and year
        salary_details = salary_details_collection.find_one({
            "person_name": person_name,
            "month_year": month_year
        })

        if not salary_details:
            return jsonify({"error": "No salary details found for the given month and year"}), 404

        # Generate payslip PDF
        pdf_file = generate_payslip(employee, salary_details)
        
        return send_file(pdf_file, as_attachment=True)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


