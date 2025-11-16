"""
Agent Evaluator
Functions to assess goal completion, efficiency, and errors for ERP agents.
"""

import statistics
import datetime


class AgentEvaluator:
    def __init__(self):
        self.reports = []

    def evaluate_goal_completion(self, agent_name: str, goals: list, memory_records: list):
        """
        Assess whether agent goals were addressed in memory records.
        :param agent_name: name of the agent
        :param goals: list of goals (strings)
        :param memory_records: list of memory entries from MemoryBank
        :return: dict with completion status
        """
        completed = {}
        for goal in goals:
            matched = any(goal.lower() in str(r["data"]).lower() for r in memory_records)
            completed[goal] = matched
        report = {
            "agent": agent_name,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "goal_completion": completed
        }
        self.reports.append(report)
        return report

    def evaluate_efficiency(self, agent_name: str, metrics_summary: dict):
        """
        Assess efficiency based on metrics (timings, success/failure counts).
        :param agent_name: name of the agent
        :param metrics_summary: dict from MetricsTracker.summary()
        :return: dict with efficiency stats
        """
        times = [v for k, v in metrics_summary.items() if k.endswith("_time_total")]
        avg_time = statistics.mean(times) if times else None

        successes = sum(v for k, v in metrics_summary.items() if k.endswith("_success"))
        failures = sum(v for k, v in metrics_summary.items() if k.endswith("_failure"))

        efficiency = {
            "agent": agent_name,
            "avg_time": avg_time,
            "successes": successes,
            "failures": failures,
            "success_rate": successes / (successes + failures) if (successes + failures) > 0 else None
        }
        self.reports.append(efficiency)
        return efficiency

    def evaluate_errors(self, agent_name: str, memory_records: list):
        """
        Scan memory records for error messages.
        :param agent_name: name of the agent
        :param memory_records: list of memory entries
        :return: dict with error count and examples
        """
        errors = [r for r in memory_records if "error" in str(r["data"]).lower()
                  or "not found" in str(r["data"]).lower()
                  or "mismatch" in str(r["data"]).lower()]

        error_report = {
            "agent": agent_name,
            "error_count": len(errors),
            "examples": errors[:5]  # show first 5 examples
        }
        self.reports.append(error_report)
        return error_report

    def full_report(self):
        """Return all accumulated evaluation reports."""
        return self.reports
