"""
ERP-specific custom tools for specialized operations.
"""

from utils.helpers import log_event


class InventoryTool:
    def restock_item(self, item_id: str):
        log_event({"tool": "InventoryTool", "event": "restock_item", "item_id": item_id})
        return f"Item {item_id} restocked successfully."


class SalesTool:
    def process_order(self, order: dict):
        log_event({"tool": "SalesTool", "event": "process_order", "order": order})
        return f"Order for {order['customer']} processed."


class HRTool:
    def add_employee(self, employee: dict):
        log_event({"tool": "HRTool", "event": "add_employee", "employee": employee})
        return f"Employee {employee['name']} added to HR system."
