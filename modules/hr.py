class HRModule:
    def __init__(self):
        self.employees = {}
        self.next_id = 1

    def add_employee(self, employee):
        """
        Add a new employee.
        :param employee: dict with employee details (e.g. {"name": ..., "role": ...})
        """
        emp_id = self.next_id
        employee["employee_id"] = emp_id
        self.employees[emp_id] = employee
        self.next_id += 1
        return {
            "status": "success",
            "employee_id": emp_id,
            "data": employee
        }

    def update_employee(self, employee_id, info):
        """
        Update an existing employee's information.
        :param employee_id: int
        :param info: dict of fields to update
        """
        if employee_id not in self.employees:
            return {"status": "error", "message": f"Employee {employee_id} not found"}
        self.employees[employee_id].update(info)
        return {
            "status": "success",
            "employee_id": employee_id,
            "updated": self.employees[employee_id]
        }

    def remove_employee(self, employee_id):
        """
        Remove an employee by ID.
        :param employee_id: int
        """
        if employee_id not in self.employees:
            return {"status": "error", "message": f"Employee {employee_id} not found"}
        removed = self.employees.pop(employee_id)
        return {
            "status": "success",
            "employee_id": employee_id,
            "removed": removed
        }
