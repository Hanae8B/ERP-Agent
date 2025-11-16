"""
InMemory session management for temporary state.
"""

class SessionService:
    def __init__(self):
        # ephemeral state, cleared when agent restarts
        self.state = {}

    def set(self, key: str, value):
        self.state[key] = value

    def get(self, key: str, default=None):
        return self.state.get(key, default)

    def clear(self):
        self.state.clear()

    def all(self):
        return dict(self.state)
