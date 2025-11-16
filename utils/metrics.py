"""
Metrics tracking for performance, success/failure counts.
"""

import time
from collections import defaultdict


class MetricsTracker:
    def __init__(self):
        self.metrics = defaultdict(int)
        self.timings = {}

    def start_timer(self, name: str):
        """Start a timer for a metric."""
        self.timings[name] = time.perf_counter()

    def stop_timer(self, name: str):
        """Stop a timer and record elapsed time."""
        if name in self.timings:
            elapsed = time.perf_counter() - self.timings[name]
            self.metrics[f"{name}_time_total"] += elapsed
            self.metrics[f"{name}_time_count"] += 1
            del self.timings[name]
            return elapsed
        return None

    def increment(self, name: str):
        """Increment a counter metric."""
        self.metrics[name] += 1

    def record_success(self, name: str):
        self.increment(f"{name}_success")

    def record_failure(self, name: str):
        self.increment(f"{name}_failure")

    def summary(self):
        """Return all metrics as a dict."""
        return dict(self.metrics)
