from modules.inventory import InventoryModule
from modules.sales import SalesModule
from modules.hr import HRModule
from modules.planner import PlannerModule
from utils.helpers import log_event
from memory.session_service import SessionService
from memory.memory_bank import MemoryBank


class ERPAgent:
    def __init__(self, name: str, modules: dict, tool_coordinator=None,
                 session: SessionService = None, memory: MemoryBank = None):
        """
        ERPAgent coordinates ERP modules, tools, and memory.
        :param name: identifier for the agent
        :param modules: dict of initialized modules (inventory, sales, hr, planner)
        :param tool_coordinator: optional ToolCoordinator instance for dynamic tool calls
        :param session: temporary in-memory session service
        :param memory: long-term memory bank
        """
        self.name = name
        self.modules = modules
        self.tool_coordinator = tool_coordinator
        self.session = session or SessionService()
        self.memory = memory or MemoryBank()
        self.perceived_data = None
        self.actions = None

    def perceive(self, data: dict):
        """Receive and store input data from environment."""
        self.perceived_data = data
        self.session.set("last_perception", data)
        self.memory.add_record(self.name, "perceive", data)
        log_event({"agent": self.name, "event": "perceive", "data": data})

    def decide(self):
        """Decide actions based on perceived data and planner goals."""
        actions = []

        if not self.perceived_data:
            return []

        if "low_stock_item" in self.perceived_data:
            item = self.perceived_data["low_stock_item"]
            actions.append(("inventory", "restock_item", {"item_id": item}))

        if "new_order" in self.perceived_data:
            order = self.perceived_data["new_order"]
            actions.append(("sales", "process_order", {"order": order}))

        if "new_employee" in self.perceived_data:
            employee = self.perceived_data["new_employee"]
            actions.append(("hr", "add_employee", {"employee": employee}))

        actions.append(("planner", "review_goals", {}))

        self.actions = actions
        self.session.set("last_actions", actions)
        self.memory.add_record(self.name, "decide", {"actions": actions})
        log_event({"agent": self.name, "event": "decide", "actions": actions})
        return actions

    def act(self, actions: list):
        """Execute planned actions across modules or tools."""
        results = []
        for module_name, action, params in actions:
            # If tool coordinator is provided, try tools first
            if self.tool_coordinator and module_name in self.tool_coordinator.tools:
                result = self.tool_coordinator._run_task(module_name, action, params)
                results.append((module_name, result))
                continue

            # Otherwise fallback to ERP modules
            module = self.modules.get(module_name)
            if not module:
                results.append((module_name, "Module not found"))
                continue

            method = getattr(module, action, None)
            if callable(method):
                try:
                    result = method(**params)
                except TypeError as e:
                    result = f"Parameter mismatch: {e}"
                results.append((module_name, result))
            else:
                results.append((module_name, f"Action {action} not implemented"))

        self.session.set("last_results", results)
        self.memory.add_record(self.name, "act", {"results": results})
        log_event({"agent": self.name, "event": "act", "results": results})
        return results


if __name__ == "__main__":
    # Initialize ERP modules
    inventory = InventoryModule()
    sales = SalesModule()
    hr = HRModule()
    planner = PlannerModule()

    # Add initial example goals
    planner.add_goal("Improve inventory management", priority=3)
    planner.add_goal("Reduce operational costs", priority=2)
    planner.add_goal("Boost sales growth", priority=1)

    # Register modules in agent
    modules = {
        "inventory": inventory,
        "sales": sales,
        "hr": hr,
        "planner": planner
    }

    # Create agent with session + memory
    agent = ERPAgent(name="ERP-1", modules=modules,
                     session=SessionService(), memory=MemoryBank())

    # Example input data
    data = {
        "low_stock_item": "V01",
        "new_order": {"customer": "Hanae", "items": [{"item_id": "V01", "qty": 2}]},
        "new_employee": {"name": "Anagura", "role": "Sales"}
    }

    # Run agent cycle
    agent.perceive(data)
    actions = agent.decide()
    results = agent.act(actions)

    print("=== Agent Run ===")
    print("Perceived Data:", data)
    print("Planned Actions:", actions)
    print("Execution Results:", results)
    print("Session State:", agent.session.all())
    print("Memory Records:", agent.memory.all())
