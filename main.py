from agent.agent import ERPAgent
from modules.inventory import InventoryModule
from modules.sales import SalesModule
from modules.hr import HRModule
from modules.planner import PlannerModule
from utils.helpers import log_event, calculate_metric

def main():
    """
    Entry point for the ERP Agent system.
    """
    # Initialize ERP modules
    inventory = InventoryModule()
    sales = SalesModule()
    hr = HRModule()
    planner = PlannerModule()

    # Add dynamic goals
    planner.add_goal("Improve inventory management", priority=3)
    planner.add_goal("Reduce operational costs", priority=2)
    planner.add_goal("Boost sales growth", priority=1)

    modules = {
        "inventory": inventory,
        "sales": sales,
        "hr": hr,
        "planner": planner
    }

    # Initialize ERP agent
    agent = ERPAgent(modules=modules)

    # Example input data
    data = {
        "low_stock_item": "V01",
        "new_order": {"customer": "Hanae", "items": [{"item_id": "V01", "qty": 2}]},
        "new_employee": {"name": "Anagura", "role": "Sales"}
    }

    # Perceive → Decide → Act
    agent.perceive(data)
    actions = agent.decide()
    results = agent.act(actions)

    # Logging
    log_event({"agent_actions": actions, "results": results})

    # Calculate metrics
    metric_result = calculate_metric("employee_count", {"employees": hr.employees})
    print("Metric Result:", metric_result)

    # Display results
    print("=== ERP Agent Run ===")
    print("Perceived Data:", data)
    print("Planned Actions:", actions)
    print("Execution Results:", results)

if __name__ == "__main__":
    main()
