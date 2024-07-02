1. http://127.0.0.1:5000/api/processes/

{
  "name": "Change Manager 2",
  "description": "Process to change manager"
}
{
    "message": "Process created",
    "process": {
        "_id": "667e6b3253df78f67abef84e",
        "description": "Process to change manager",
        "name": "Change Manager 2",
        "processId": "667e6b3253df78f67abef84d"
    }
}



2. http://127.0.0.1:5000/api/approvers/group

{
  "group": "Finance Team",
  "allowEmptyGroups": true,
  "email": ["piyushbirkh@gmail.com", "piyush@payrollcloudcorp.com"]
}
{
    "approver": {
        "_id": "667e6e50c203a066dce8c65d",
        "allowEmptyGroups": true,
        "approverId": "667e6e50c203a066dce8c65c",
        "email": [
            "piyushbirkh@gmail.com",
            "piyush@payrollcloudcorp.com"
        ],
        "group": "Finance Team",
        "type": "group"
    },
    "message": "Approval group added"
}

http://127.0.0.1:5000/api/approvers/hierarchy

{
  "startsWith": "Manager",
  "routesUsing": "Direct Manager",
  "topApprover": "CEO",
  "approvalChainOf": "Employee",
  "email": ["sajal@payrollcloyudcorp.com", "piyush@payrollcloyudcorp.com"]
}
{
    "approver": {
        "_id": "667e6eeec203a066dce8c65f",
        "approvalChainOf": "Employee",
        "approverId": "667e6eeec203a066dce8c65e",
        "email": [
            "sajal@payrollcloyudcorp.com",
            "piyush@payrollcloyudcorp.com"
        ],
        "routesUsing": "Direct Manager",
        "startsWith": "Manager",
        "topApprover": "CEO",
        "type": "hierarchy"
    },
    "message": "Management hierarchy added"
}

http://127.0.0.1:5000/api/approvers/representative

{
  "representativeType": "HR",
  "representativeOf": "Employee",
  "email": ["piyushbirkh@gmail.com"]
}
{
    "approver": {
        "_id": "667e6f2ec203a066dce8c661",
        "approverId": "667e6f2ec203a066dce8c660",
        "email": [
            "piyushbirkh@gmail.com"
        ],
        "representativeOf": "Employee",
        "representativeType": "HR",
        "type": "representative"
    },
    "message": "Representative added"
}





3. http://127.0.0.1:5000/api/conditions

POST
{
  "processId": "6676d09dcd8a5b0b40dd37bd",
  "type": "threshold",
  "field": "amount",
  "operator": ">",
  "value": 1000,
  "action": "require_approval"
}
{
  "message": "Condition added",
  "condition": {
    "conditionId": "some-generated-id",
    "processId": "6676d09dcd8a5b0b40dd37bd",
    "type": "threshold",
    "field": "amount",
    "operator": ">",
    "value": 1000,
    "action": "require_approval",
    "_id": "some-generated-object-id"
  }
}

{
  "processId": "6676d09dcd8a5b0b40dd37bd",
  "type": "range",
  "field": "amount",
  "operator": "between",
  "value": [1000, 10000],
  "action": "require_approval_from_manager"
}
{
    "condition": {
        "_id": "667e77a1833d7f2fa69a6bcf",
        "action": "require_approval_from_manager",
        "conditionId": "667e77a1833d7f2fa69a6bce",
        "field": "amount",
        "operator": "between",
        "processId": "6676d09dcd8a5b0b40dd37bd",
        "type": "range",
        "value": [
            1000,
            10000
        ]
    },
    "message": "Condition added"
}

{
  "processId": "6676d09dcd8a5b0b40dd37bd",
  "type": "threshold",
  "field": "amount",
  "operator": ">",
  "value": 10000,
  "action": "require_approval_from_director"
}
{
    "condition": {
        "_id": "667e77b6833d7f2fa69a6bd1",
        "action": "require_approval_from_director",
        "conditionId": "667e77b6833d7f2fa69a6bd0",
        "field": "amount",
        "operator": ">",
        "processId": "6676d09dcd8a5b0b40dd37bd",
        "type": "threshold",
        "value": 10000
    },
    "message": "Condition added"
}




GET
http://127.0.0.1:5000/api/conditions

NO INPUT
OUTPUT - ALL CONDITIONS













4. http://127.0.0.1:5000/api/approval_rules

{
  "processId": "6676d09dcd8a5b0b40dd37bd",
  "conditions": [
    {
      "conditionId": "667e767595328af65f4a0c7c",
      "approvers": ["auto_approve"]
    },
    {
      "conditionId": "667e77a1833d7f2fa69a6bce",
      "approvers": ["667e6e50c203a066dce8c65c", "667e6eeec203a066dce8c65e"]
    },
    {
      "conditionId": "667e77b6833d7f2fa69a6bd0",
      "approvers": ["667e6e50c203a066dce8c65c", "667e6eeec203a066dce8c65e", "667e6f2ec203a066dce8c660"]
    }
  ]
}


{
    "approval_rule": {
        "_id": "667fc2b0e3239d48ec00168f",
        "processId": "6676d09dcd8a5b0b40dd37bd",
        "rules": [{
                "approvers": [
                    "auto_approve"
                ],
                "conditionId": "667e767595328af65f4a0c7c"
            },
            {
                "approvers": [
                    "667e6e50c203a066dce8c65c",
                    "667e6eeec203a066dce8c65e"
                ],
                "conditionId": "667e77a1833d7f2fa69a6bce"
            },
            {
                "approvers": [
                    "667e6e50c203a066dce8c65c",
                    "667e6eeec203a066dce8c65e",
                    "667e6f2ec203a066dce8c660"
                ],
                "conditionId": "667e77b6833d7f2fa69a6bd0"
            }
        ]
    },
    "message": "Approval rule created"
}









5. http://127.0.0.1:5000/api/transactions


{
  "processId": "6676d09dcd8a5b0b40dd37bd",
  "transaction_fields": {
    "amount": 5000,
    "fieldType": "amount"
  }
}


6. http://127.0.0.1:5000/api/transactions/reminders

{
 "transaction_id":"6683b86495b894c7dd99205f"
}

























