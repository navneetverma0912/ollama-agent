import uuid

LEAVE_BALANCES = {
    "EMP001": {"annual_leave": 12, "sick_leave": 7},
    "EMP002": {"annual_leave": 10, "sick_leave": 5},
    "EMP003": {"annual_leave": 15, "sick_leave": 10},
}

def get_leave_balance(employee_id: str):
    return LEAVE_BALANCES.get(employee_id, {"annual_leave": 0, "sick_leave": 0})

def create_leave_request(employee_id: str, start_date: str, end_date: str):
    return {
        "request_id": "LR-" + uuid.uuid4().hex[:8].upper(),
        "employee_id": employee_id,
        "start_date": start_date,
        "end_date": end_date,
        "status": "pending_approval",
    }
