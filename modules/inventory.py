class InventoryModule:
    def __init__(self):
        self.inventory = {}

    def check_stock(self, item_id):
        """
        Return current stock level for an item.
        """
        return self.inventory.get(item_id, 0)

    def reorder_item(self, item_id, quantity):
        """
        Increase stock of an item by the given quantity.
        """
        current = self.inventory.get(item_id, 0)
        self.inventory[item_id] = current + quantity
        return {
            "status": "success",
            "item_id": item_id,
            "updated_quantity": self.inventory[item_id]
        }

    def predict_demand(self, item_id):
        """
        Stub demand forecast for an item.
        """
        return {"item_id": item_id, "forecast": 100}

    def restock_item(self, item_id, quantity=10):
        """
        Restock an item by delegating to reorder_item.
        Default restock quantity is 10 unless specified.
        """
        return self.reorder_item(item_id, quantity)
