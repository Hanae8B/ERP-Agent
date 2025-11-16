import tkinter as tk
from tkinter import messagebox
import os
from modules.planner import PlannerModule
from modules.inventory import InventoryModule
from modules.sales import SalesModule
from modules.hr import HRModule
from utils.helpers import log_event
from agent_pkg.agent import ERPAgent


class ERPApp:
    def __init__(self, master):
        self.master = master
        master.title("ERP Agent")

        # Initialize ERP modules
        self.inventory = InventoryModule()
        self.sales = SalesModule()
        self.hr = HRModule()
        # Planner with configurable similarity threshold
        self.planner = PlannerModule(similarity_threshold=0.5)

        # Auto-load saved goals if file exists
        self.load_saved_goals()

        self.modules = {
            "inventory": self.inventory,
            "sales": self.sales,
            "hr": self.hr,
            "planner": self.planner
        }

        # Initialize ERP agent with a name
        self.agent = ERPAgent(name="ERP-GUI", modules=self.modules)

        # GUI Elements
        self.label = tk.Label(master, text="ERP Agent Dashboard", font=("Arial", 14, "bold"))
        self.label.pack(pady=10)

        # Goal entry
        self.goal_entry = tk.Entry(master, width=50)
        self.goal_entry.pack(pady=5)
        self.priority_entry = tk.Entry(master, width=5)
        self.priority_entry.pack(pady=2)
        self.priority_entry.insert(0, "1")

        # Buttons for goals
        self.add_goal_button = tk.Button(master, text="Add Goal", command=self.add_goal)
        self.add_goal_button.pack(pady=2)
        self.save_goals_button = tk.Button(master, text="Save Goals", command=self.save_goals)
        self.save_goals_button.pack(pady=2)

        # Similarity threshold slider
        self.threshold_scale = tk.Scale(
            master,
            from_=0.0,
            to=1.0,
            resolution=0.05,
            orient="horizontal",
            label="Similarity Threshold",
            command=self.update_threshold
        )
        self.threshold_scale.set(self.planner.similarity_threshold)
        self.threshold_scale.pack(pady=5)

        # Run agent button
        self.run_button = tk.Button(master, text="Run Agent", command=self.run_agent)
        self.run_button.pack(pady=5)

        # Output text box
        self.output_text = tk.Text(master, height=20, width=80, wrap="word")
        self.output_text.pack(pady=10)

        # Display initial goals after output_text exists
        self.display_goals()

    def load_saved_goals(self):
        """Load goals from saved_goals.txt if it exists, deduplicated via planner."""
        if os.path.exists("saved_goals.txt"):
            with open("saved_goals.txt", "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split("|")
                    if len(parts) == 2:
                        goal, priority = parts
                        try:
                            priority = int(priority)
                        except ValueError:
                            priority = 1
                        self.planner.add_goal(goal, priority)
        else:
            # Add some default example goals if no file exists
            self.planner.add_goal("Improve inventory management", priority=3)
            self.planner.add_goal("Reduce operational costs", priority=2)
            self.planner.add_goal("Boost sales growth", priority=1)

    def add_goal(self):
        goal_text = self.goal_entry.get().strip()
        try:
            priority = int(self.priority_entry.get())
        except ValueError:
            priority = 1

        if not goal_text:
            messagebox.showwarning("Missing goal", "Please enter a goal before adding.")
            return

        # Call planner.add_goal which now handles duplicates and similarity
        result = self.planner.add_goal(goal_text, priority)

        if result.get("status") == "duplicate":
            existing_list = "\n".join(
                [f"- {g['goal']} (Priority {g['priority']})" for g in result.get("existing_goals", [])]
            )
            messagebox.showinfo(
                "Goal already exists",
                f"The following goal already exists and priority was updated if needed:\n\n{existing_list}"
            )

        elif result.get("status") == "similar":
            similar_list = "\n".join(
                [f"- {g['goal']} (Priority {g['priority']}, similarity {g['similarity']:.2f})"
                 for g in result.get("similar_goals", [])]
            )
            proceed = messagebox.askyesno(
                "Similar goals detected",
                f"Similar goals were found:\n\n{similar_list}\n\nDo you still want to add '{goal_text}'?"
            )
            if proceed:
                self.planner.goals.append({"goal": goal_text, "priority": priority})
                self.planner.save_goals()
                messagebox.showinfo("Goal added", f"Goal '{goal_text}' added successfully.")
            else:
                return  # user canceled

        elif result.get("status") == "success":
            messagebox.showinfo("Goal added", result.get("message"))

        # Persist and refresh UI
        self.save_goals()
        self.display_goals()

        # Reset inputs
        self.goal_entry.delete(0, tk.END)
        self.priority_entry.delete(0, tk.END)
        self.priority_entry.insert(0, "1")

    def save_goals(self):
        """Save goals to a file (deduplicated, overwrite)."""
        with open("saved_goals.txt", "w", encoding="utf-8") as f:
            for g in self.planner.goals:
                f.write(f"{g['goal']}|{g['priority']}\n")
        self.output_text.insert(tk.END, "Goals saved successfully.\n\n")

    def display_goals(self):
        """Display deduplicated goals, priority summary, and threshold."""
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Current Goals:\n")

        for g in sorted(self.planner.goals, key=lambda x: x["priority"], reverse=True):
            self.output_text.insert(tk.END, f"- {g['goal']} (Priority {g['priority']})\n")

        # Show priority summary from planner analysis
        self.output_text.insert(tk.END, "\nPriority Summary:\n")
        analysis = self.planner.analyze_goals()
        if analysis.get("status") == "success":
            summary = analysis["analysis"].get("priority_summary", {})
            for p_label, count in summary.items():
                self.output_text.insert(tk.END, f"- {p_label}: {count}\n")
        else:
            self.output_text.insert(tk.END, "- No goals defined\n")

        # Show similarity threshold
        self.output_text.insert(tk.END, f"\nSimilarity threshold: {self.planner.similarity_threshold}\n\n")

    def update_threshold(self, value):
        """Update planner similarity threshold from slider."""
        try:
            self.planner.similarity_threshold = float(value)
            self.display_goals()  # refresh display to show new threshold
        except ValueError:
            pass

    def run_agent(self):
        # Example input data
        data = {
            "low_stock_item": "V01",
            "new_order": {"customer": "Hanae", "items": [{"item_id": "V01", "qty": 2}]},
            "new_employee": {"name": "Anagura", "role": "Sales"}
        }

        self.agent.perceive(data)
        actions = self.agent.decide()
        results = self.agent.act(actions)

        # Display results
        self.output_text.insert(tk.END, "=== Agent Run ===\n")
        self.output_text.insert(tk.END, f"Perceived Data: {data}\n")
        self.output_text.insert(tk.END, f"Planned Actions: {actions}\n")
        self.output_text.insert(tk.END, f"Execution Results: {results}\n\n")

        log_event({"agent_actions": actions, "results": results})


if __name__ == "__main__":
    root = tk.Tk()
    app = ERPApp(root)
    root.mainloop()
