EMPLOYEES = {
    "EMP001": {"employee_id": "EMP001", "name": "Navneet Verma", "department": "IT Analyst", "designation": "Software Developer"},
    "EMP002": {"employee_id": "EMP002", "name": "Amit Kumar", "department": "HR", "designation": "HR Executive"},
    "EMP003": {"employee_id": "EMP003", "name": "Sunita Sharma", "department": "Finance", "designation": "Accountant"},
}

def get_employee(employee_id: str):
    return EMPLOYEES.get(employee_id, {
        "employee_id": employee_id, "name": "Unknown", "department": "Unknown", "designation": "Unknown"
    })
