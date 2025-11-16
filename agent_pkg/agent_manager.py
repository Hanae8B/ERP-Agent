from utils.helpers import log_event
import concurrent.futures


class AgentManager:
    def __init__(self, agents: list):
        self.agents = agents

    def run_sequential(self, data: dict):
        results = {}
        for agent in self.agents:
            agent.perceive(data)
            actions = agent.decide()
            results[agent.name] = agent.act(actions if isinstance(actions, list) else [])
        log_event({"event": "run_sequential", "results": results})
        return results

    def run_parallel(self, data: dict):
        results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_map = {
                executor.submit(self._run_agent_cycle, agent, data): agent.name
                for agent in self.agents
            }
            for future in concurrent.futures.as_completed(future_map):
                results[future_map[future]] = future.result()
        log_event({"event": "run_parallel", "results": results})
        return results

    def run_loop(self, data: dict, iterations: int = 3):
        results = {}
        for i in range(iterations):
            for agent in self.agents:
                agent.perceive(data)
                actions = agent.decide()
                results.setdefault(agent.name, []).append(agent.act(actions if isinstance(actions, list) else []))
        log_event({"event": "run_loop", "results": results})
        return results

    def _run_agent_cycle(self, agent, data):
        agent.perceive(data)
        actions = agent.decide()
        return agent.act(actions if isinstance(actions, list) else [])
