from flask import Flask, jsonify
import concurrent.futures
import absence  # Import absence.py
import performanceGoals  # Import performanceGoals.py
import emps  # Import emps.py
import salary  # Import salary.py
import absence_balance
import perfEvaluations_PerDoc
import goalPlanAssignees
import goalPlan
import journeys
import journeyTaskLibrary
import workerJourneys
import eligible_options_lov
import relatedFlowSubmissions
import searchGoals
import elementEntries
import flowInstances
import flowInstancesLOV
import flowPatterns
import organizationPaymentMethodsLOV
import payrollBalanceDefinitionsLOV
import payrollDefinitionsLOV
import payrollDocumentRecords
import payrollElementDefinitionsLOV
import payrollInputValuesLOV
import payrollRelationships
import payrollStatutoryUnitsLOV
import payrollTimeDefinitionsLOV
import 

# Flask App initialization
app = Flask(__name__)

def run_absence_report():
    print("Generating absence report...")
    absence.generate_report3()
    print("Done - absence report")

def run_generate_perfEvaluations_PerDoc_report():
    print("Generating performance evaluations report...")
    perfEvaluations_PerDoc.generate_report3()
    print("Done - performance evaluations")

def run_goal_plan_assignees_report():
    print("Generating goal plan ssignees report...")
    goalPlanAssignees.generate_report3()
    print("Done - goal plan ssignees report")   

def run_goal_plan_report():
    print("Generating goal plan report...")
    goalPlan.generate_report3()
    print("Done - goal plan report")       

def run_performance_goals_report():
    print("Generating performance goals report...")
    performanceGoals.generate_report3()
    print("Done - performance goals report")

def run_employee_report():
    print("Generating employee report...")
    emps.generate_report3()
    print("Done - employee report")

def run_salary_report():
    print("Generating salary report...")
    salary.generate_report3()
    print("Done - salary report")

def run_generate_plan_balances_report():
    print("Generating absence balances report...")
    absence_balance.generate_report3()
    print("Done - absence balances")

def run_generate_journeys_report():
    print("Generating journeys report...")
    journeys.generate_report3()
    print("Done - journeys")

def run_generate_journeyTaskLibrary_report():
    print("Generating journeyTaskLibrary report...")
    journeyTaskLibrary.generate_report3()
    print("Done - journeyTaskLibrary")

def run_generate_workerJourneys_report():
    print("Generating workerJourneys report...")
    workerJourneys.generate_report3()
    print("Done - workerJourneys")   

def run_generate_eligible_options_lov_report():
    print("Generating eligible_options_lov report...")
    eligible_options_lov.generate_report3()
    print("Done - eligible_options_lov")  

def run_generate_searchGoals_report():
    print("Generating searchGoals report...")
    searchGoals.generate_report3()
    print("Done - searchGoals") 

# payroll    

def run_generate_relatedFlowSubmissions_report():
    print("Generating relatedFlowSubmissions report...")
    relatedFlowSubmissions.generate_report3()
    print("Done - relatedFlowSubmissions")   

def run_generate_elementEntries_report():
    print("Generating elementEntries report...")
    elementEntries.generate_report3()
    print("Done - elementEntries")  

def run_generate_flowInstances_report():
    print("Generating flowInstances report...")
    flowInstances.generate_report3()
    print("Done - flowInstances")          

def run_generate_flow_instances_lov_report():
    print("Generating flowInstancesLOV report...")
    flowInstancesLOV.generate_report3()
    print("Done - flowInstancesLOV")          

def run_generate_flow_patterns_report():
    print("Generating flowPatterns report...")
    flowPatterns.generate_report3()
    print("Done - flowPatterns")          

def run_generate_org_payment_methods_report():
    print("Generating organizationPaymentMethodsLOV report...")
    organizationPaymentMethodsLOV.generate_report3()
    print("Done - organizationPaymentMethodsLOV")          

def run_generate_payroll_balance_definitions_report():
    print("Generating payrollBalanceDefinitionsLOV report...")
    payrollBalanceDefinitionsLOV.generate_report3()
    print("Done - payrollBalanceDefinitionsLOV")          

def run_generate_payroll_definitions_report():
    print("Generating payrollDefinitionsLOV report...")
    payrollDefinitionsLOV.generate_report3()
    print("Done - payrollDefinitionsLOV")          

def run_generate_payroll_document_records_report():
    print("Generating payrollDocumentRecords report...")
    payrollDocumentRecords.generate_report3()
    print("Done - payrollDocumentRecords")          

def run_generate_payroll_element_definitions3_report():
    print("Generating payrollElementDefinitionsLOV report...")
    payrollElementDefinitionsLOV.generate_report3()
    print("Done - payrollElementDefinitionsLOV") 

def run_generate_payroll_input_values_report():
    print("Generating payrollInputValuesLOV report...")
    payrollInputValuesLOV.generate_report3()
    print("Done - payrollInputValuesLOV") 

def run_generate_payroll_relationships_report():
    print("Generating payrollRelationships report...")
    payrollRelationships.generate_report3()
    print("Done - payrollRelationships") 

def run_generate_payroll_statutory_units_report():
    print("Generating payrollStatutoryUnitsLOV report...")
    payrollStatutoryUnitsLOV.generate_report3()
    print("Done - payrollStatutoryUnitsLOV")

def run_generate_payroll_time_definitions_report():
    print("Generating payrollTimeDefinitionsLOV report...")
    payrollTimeDefinitionsLOV.generate_report3()
    print("Done - payrollTimeDefinitionsLOV")

def run_generate_payroll_time_definitions_report():
    print("Generating payrollTimeDefinitionsLOV report...")
    payrollTimeDefinitionsLOV.generate_report3()
    print("Done - payrollTimeDefinitionsLOV")

def run_all_reports():
    """
    Runs all the report generation functions in parallel.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            # executor.submit(run_absence_report),
            # executor.submit(run_generate_perfEvaluations_PerDoc_report),
            # executor.submit(run_performance_goals_report),
            # executor.submit(run_generate_searchGoals_report),
            # executor.submit(run_goal_plan_report),
            # executor.submit(run_goal_plan_assignees_report),
            # executor.submit(run_employee_report),
            # executor.submit(run_salary_report),
            # executor.submit(run_generate_plan_balances_report),
            # executor.submit(run_generate_journeys_report),
            # executor.submit(run_generate_journeyTaskLibrary_report),
            # executor.submit(run_generate_workerJourneys_report),
            # executor.submit(run_generate_eligible_options_lov_report),
            # executor.submit(run_generate_relatedFlowSubmissions_report),
            # executor.submit(run_generate_elementEntries_report),
            # executor.submit(run_generate_flowInstances_report),
            # executor.submit(run_generate_flow_instances_lov_report),
            # executor.submit(run_generate_flow_patterns_report),
            # executor.submit(run_generate_org_payment_methods_report),
            # executor.submit(run_generate_payroll_balance_definitions_report),
            # executor.submit(run_generate_payroll_definitions_report),
            # executor.submit(run_generate_payroll_document_records_report),
            # executor.submit(run_generate_payroll_element_definitions3_report),
            # executor.submit(run_generate_payroll_input_values_report),
            # executor.submit(run_generate_payroll_relationships_report),
            # executor.submit(run_generate_payroll_statutory_units_report),
            # executor.submit(run_generate_payroll_time_definitions_report),
            executor.submit(run_generate_payroll_time_definitions_report)
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # Wait for the task to complete and raise exceptions if any
            except Exception as e:
                print(f"An error occurred: {e}")

@app.route('/generate-report', methods=['POST'])
def report_route():
    try:
        message = run_all_reports()
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

