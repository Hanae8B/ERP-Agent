import json
import os
from collections import Counter

class PlannerModule:
    """
    ERP Planning / Decision Support module with persistent goals.
    Includes similarity detection with configurable threshold.
    """

    def __init__(self, save_file="planner_goals.json", similarity_threshold=0.5):
        self.goals = []
        self.next_actions = []
        self.save_file = save_file
        self.similarity_threshold = similarity_threshold  # configurable
        self.load_goals()  # load goals on startup

    def _similarity(self, goal1: str, goal2: str) -> float:
        """
        Compute a simple similarity score between two goals using token overlap (Jaccard).
        Returns a float between 0 and 1.
        """
        tokens1 = set(goal1.lower().split())
        tokens2 = set(goal2.lower().split())
        if not tokens1 or not tokens2:
            return 0.0
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        return len(intersection) / len(union)

    def find_similar_goals(self, goal: str):
        """Return list of goals that are similar to the given goal above threshold."""
        similar = []
        for g in self.goals:
            score = self._similarity(goal, g["goal"])
            if score >= self.similarity_threshold:
                similar.append({"goal": g["goal"], "priority": g["priority"], "similarity": score})
        return similar

    def add_goal(self, goal: str, priority: int = 1):
        """
        Add a new goal. If a similar goal exists above threshold, return warning.
        If exact duplicate, update priority instead of adding.
        """
        # Exact duplicate check
        existing = [g for g in self.goals if g["goal"].lower() == goal.lower()]
        if existing:
            for g in existing:
                g["priority"] = priority
            self.save_goals()
            return {
                "status": "duplicate",
                "message": f"Exact goal already exists: {[g['goal'] for g in existing]}",
                "existing_goals": existing
            }

        # Similarity check
        similar = self.find_similar_goals(goal)
        if similar:
            return {
                "status": "similar",
                "message": f"Similar goals detected for '{goal}'",
                "similar_goals": similar
            }

        # Add new goal
        self.goals.append({"goal": goal, "priority": priority})
        self.save_goals()
        return {"status": "success", "message": f"Goal '{goal}' added successfully."}

    def remove_goal(self, goal: str):
        """Remove a goal by its name."""
        self.goals = [g for g in self.goals if g["goal"].lower() != goal.lower()]
        self.save_goals()

    def save_goals(self):
        """Save current goals to a JSON file."""
        with open(self.save_file, "w") as f:
            json.dump(self.goals, f, indent=2)

    def load_goals(self):
        """Load goals from JSON file if it exists, deduplicating entries."""
        if os.path.exists(self.save_file):
            with open(self.save_file, "r") as f:
                loaded_goals = json.load(f)
            unique = {}
            for g in loaded_goals:
                key = g["goal"].lower()
                if key not in unique or g["priority"] > unique[key]["priority"]:
                    unique[key] = g
            self.goals = list(unique.values())
            self.save_goals()

    def analyze_goals(self):
        """Return a summary analysis of current goals, including counts per priority."""
        if not self.goals:
            return {"status": "error", "analysis": "No goals defined"}

        sorted_goals = sorted(self.goals, key=lambda g: g["priority"], reverse=True)
        priority_counts = Counter(g["priority"] for g in sorted_goals)

        analysis = {
            "total_goals": len(sorted_goals),
            "top_priority": sorted_goals[0]["goal"],
            "all_goals": [f'{g["goal"]} (Priority {g["priority"]})' for g in sorted_goals],
            "priority_summary": {f"Priority {p}": c for p, c in sorted(priority_counts.items(), reverse=True)}
        }
        return {"status": "success", "analysis": analysis}

    def plan_next_actions(self):
        """Generate next actions based on current goals, avoiding duplicates."""
        if not self.goals:
            return {"status": "error", "next_actions": [], "message": "No goals to plan actions for"}

        actions_set = set()
        for g in self.goals:
            goal = g["goal"].lower()
            if "inventory" in goal:
                actions_set.add("optimize_inventory")
            elif "cost" in goal or "expense" in goal:
                actions_set.add("reduce_costs")
            elif "growth" in goal or "sales" in goal:
                actions_set.add("increase_sales")
            elif "efficiency" in goal or "process" in goal:
                actions_set.add("improve_processes")
            else:
                actions_set.add("review_strategy")

        self.next_actions = list(actions_set)
        return {"status": "success", "next_actions": self.next_actions}

    def review_goals(self):
        """Combine analysis and planning into a single review step."""
        analysis = self.analyze_goals()
        actions = self.plan_next_actions()
        return {
            "status": "success",
            "analysis": analysis.get("analysis"),
            "next_actions": actions.get("next_actions", [])
        }
