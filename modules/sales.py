class SalesModule:
    def __init__(self):
        self.orders = {}
        self.next_id = 1

    def create_order(self, order_data):
        """
        Create a new order and assign it an ID.
        """
        order_id = self.next_id
        self.orders[order_id] = order_data
        self.next_id += 1
        return {
            "status": "success",
            "order_id": order_id,
            "data": order_data
        }

    def process_order(self, order):
        """
        Wrapper for create_order so the agent can call process_order.
        :param order: dict with order details
        """
        return self.create_order(order)

    def update_order_status(self, order_id, status):
        """
        Update the status of an existing order.
        """
        if order_id not in self.orders:
            return {"status": "error", "message": f"Order {order_id} not found"}
        self.orders[order_id]["status"] = status
        return {
            "status": "success",
            "order_id": order_id,
            "status": status
        }

    def cancel_order(self, order_id):
        """
        Cancel an existing order.
        """
        if order_id not in self.orders:
            return {"status": "error", "message": f"Order {order_id} not found"}
        self.orders.pop(order_id)
        return {
            "status": "success",
            "order_id": order_id,
            "status": "cancelled"
        }
