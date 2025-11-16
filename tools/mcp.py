"""
Multi-tool coordination logic.
Allows agents to call multiple tools either sequentially, in parallel, or in loops.
"""

from utils.helpers import log_event
import concurrent.futures


class ToolCoordinator:
    def __init__(self, tools: dict):
        """
        :param tools: dict of available tool instances {tool_name: tool_object}
        """
        self.tools = tools

    def run_sequential(self, tasks: list):
        """
        Run tools sequentially.
        :param tasks: list of (tool_name, method, params)
        """
        results = []
        for tool_name, method, params in tasks:
            tool = self.tools.get(tool_name)
            if not tool:
                results.append((tool_name, "Tool not found"))
                continue
            func = getattr(tool, method, None)
            if callable(func):
                results.append((tool_name, func(**params)))
            else:
                results.append((tool_name, f"Method {method} not implemented"))
        log_event({"event": "tools_sequential", "results": results})
        return results

    def run_parallel(self, tasks: list):
        """
        Run tools in parallel using threads.
        """
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_map = {
                executor.submit(self._run_task, tool_name, method, params): tool_name
                for tool_name, method, params in tasks
            }
            for future in concurrent.futures.as_completed(future_map):
                results.append((future_map[future], future.result()))
        log_event({"event": "tools_parallel", "results": results})
        return results

    def run_loop(self, tasks: list, iterations: int = 3):
        """
        Run tools repeatedly for a fixed number of iterations.
        """
        results = []
        for i in range(iterations):
            for tool_name, method, params in tasks:
                results.append(self._run_task(tool_name, method, params))
        log_event({"event": "tools_loop", "results": results})
        return results

    def _run_task(self, tool_name, method, params):
        tool = self.tools.get(tool_name)
        if not tool:
            return f"{tool_name} not found"
        func = getattr(tool, method, None)
        if callable(func):
            return func(**params)
        return f"Method {method} not implemented"
