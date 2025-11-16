"""
Long-term memory for storing historical data.
"""

import datetime

class MemoryBank:
    def __init__(self):
        # persistent historical records
        self.records = []

    def add_record(self, agent_name: str, event: str, data: dict):
        timestamp = datetime.datetime.utcnow().isoformat()
        self.records.append({
            "agent": agent_name,
            "event": event,
            "data": data,
            "timestamp": timestamp
        })

    def get_records(self, agent_name: str = None, event: str = None):
        results = self.records
        if agent_name:
            results = [r for r in results if r["agent"] == agent_name]
        if event:
            results = [r for r in results if r["event"] == event]
        return results

    def all(self):
        return list(self.records)
