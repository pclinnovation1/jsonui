# Leave accrual configuration
leave_accrual_config = {
    "leave_types": {
        "annual_leave": {
            "description": "Annual paid leave",
            "accrual_rates": {
                "full-time": 2.5,
                "part-time": 2.5,  # This will be prorated based on FTE
                "contractor": 0.5
            },
            "max_carry_forward": 10
        },
        "sick_leave": {
            "description": "Paid sick leave",
            "accrual_rates": {
                "full-time": 1.0,
                "part-time": 1.0,  # This will be prorated based on FTE
                "contractor": 0.25
            },
            "max_entitlement": 10
        },
        "maternity_leave": {
            "description": "Paid leave for mothers before and after childbirth",
            "applicable_gender": "female",
            "accrual_rates": {
                "full-time": 1.5,
                "part-time": 1.5,  # This will be prorated based on FTE
                "contractor": 0.5
            },
            "max_entitlement": 52
        },
        "paternity_leave": {
            "description": "Paid leave for fathers after childbirth",
            "applicable_gender": "male",
            "accrual_rates": {
                "full-time": 1.0,
                "part-time": 1.0,  # This will be prorated based on FTE
                "contractor": 0.25
            },
            "max_entitlement": 2
        },
        "adoption_leave": {
            "description": "Paid leave for parents who are adopting a child",
            "accrual_rates": {
                "full-time": 1.5,
                "part-time": 1.5,  # This will be prorated based on FTE
                "contractor": 0.5
            },
            "max_entitlement": 52
        },
        "bereavement_leave": {
            "description": "Paid leave due to the death of a family member",
            "accrual_rates": {
                "full-time": 0.5,
                "part-time": 0.5,  # This will be prorated based on FTE
                "contractor": 0.1
            },
            "max_entitlement": 5
        },
        "unpaid_leave": {
            "description": "Unpaid leave",
            "accrual_rates": {
                "full-time": 0.0,
                "part-time": 0.0,
                "contractor": 0.0
            }
        },
        "parental_leave": {
            "description": "Leave taken by parents to care for their children",
            "accrual_rates": {
                "full-time": 1.0,
                "part-time": 1.0,  # This will be prorated based on FTE
                "contractor": 0.25
            },
            "max_entitlement": 18
        },
        "compassionate_leave": {
            "description": "Leave for personal emergencies",
            "accrual_rates": {
                "full-time": 0.5,
                "part-time": 0.5,  # This will be prorated based on FTE
                "contractor": 0.1
            },
            "max_entitlement": 5
        },
        "shared_parental_leave": {
            "description": "Leave that allows parents to share time off after the birth or adoption of a child",
            "accrual_rates": {
                "full-time": 1.5,
                "part-time": 1.5,  # This will be prorated based on FTE
                "contractor": 0.5
            },
            "max_entitlement": 50
        },
        "study_leave": {
            "description": "Leave for educational purposes",
            "accrual_rates": {
                "full-time": 1.0,
                "part-time": 1.0,  # This will be prorated based on FTE
                "contractor": 0.25
            },
            "max_entitlement": 10
        },
        "sabbatical_leave": {
            "description": "Extended leave for personal development or travel",
            "accrual_rates": {
                "full-time": 0.5,
                "part-time": 0.5,  # This will be prorated based on FTE
                "contractor": 0.1
            },
            "max_entitlement": 24
        }
    },
    "employee_types": {
        "full-time": {
            "description": "Employees working full-time hours",
            "full_time_hours": 40
        },
        "part-time": {
            "description": "Employees working part-time hours",
            "full_time_hours": 40
        },
        "contractor": {
            "description": "Employees on a contract basis",
            "full_time_hours": 40
        }
    },
    "shift_types": {
        "day": {
            "description": "Day shift",
            "additional_leave_rate": 0.0
        },
        "night": {
            "description": "Night shift",
            "additional_leave_rate": 0.5
        },
        "rotating": {
            "description": "Rotating shift",
            "additional_leave_rate": 0.25
        }
    },
    "seniority_levels": {
        "1-5": {
            "description": "1 to 5 years of service",
            "additional_leave_rate": 0.0
        },
        "6-10": {
            "description": "6 to 10 years of service",
            "additional_leave_rate": 0.25
        },
        "10+": {
            "description": "More than 10 years of service",
            "additional_leave_rate": 0.5
        }
    },
    "union_activities": {
        "description": "Leave for participating in union activities",
        "leave_entitlement": 5
    },
    "unionized_employees": {
        "description": "Leave entitlements and accrual rates for unionized employees",
        "accrual_rates": {
            "full-time": 3.0,
            "part-time": 3.0,  # This will be prorated based on FTE
            "contractor": 0.75
        }
    },
    "holidays": {
        "public_holidays": [
            "2024-01-01",
            "2024-04-19",
            "2024-04-22",
            "2024-05-06",
            "2024-05-27",
            "2024-08-26",
            "2024-12-25",
            "2024-12-26"
        ]
    },
    "general_rules": {
        "financial_year_start": "04-01",
        "default_annual_leave_entitlement": 0,
        "accrual_period": "monthly"
    }
}