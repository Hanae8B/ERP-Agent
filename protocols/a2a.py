"""
Agent-to-Agent (A2A) communication logic.
Provides structured messaging between agents, with support for synchronous and asynchronous flows.
"""

import datetime
import queue
import threading
from utils.helpers import log_event


class A2AMessage:
    def __init__(self, sender: str, recipient: str, content: dict, msg_type: str = "request"):
        """
        Represents a message exchanged between agents.
        :param sender: name of sending agent
        :param recipient: name of receiving agent
        :param content: dict payload of the message
        :param msg_type: type of message ("request", "response", "event")
        """
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.msg_type = msg_type
        self.timestamp = datetime.datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "content": self.content,
            "msg_type": self.msg_type,
            "timestamp": self.timestamp
        }


class A2AChannel:
    def __init__(self):
        """Shared communication channel for agents."""
        self.queues = {}
        self.lock = threading.Lock()

    def register_agent(self, agent_name: str):
        """Register an agent with its own message queue."""
        with self.lock:
            if agent_name not in self.queues:
                self.queues[agent_name] = queue.Queue()

    def send(self, message: A2AMessage):
        """Send a message to the recipient's queue."""
        with self.lock:
            if message.recipient not in self.queues:
                raise ValueError(f"Recipient {message.recipient} not registered")
            self.queues[message.recipient].put(message)
            log_event({"event": "a2a_send", "message": message.to_dict()})

    def receive(self, agent_name: str, block: bool = True, timeout: int = 5):
        """Receive the next message for an agent."""
        if agent_name not in self.queues:
            raise ValueError(f"Agent {agent_name} not registered")
        try:
            msg = self.queues[agent_name].get(block=block, timeout=timeout)
            log_event({"event": "a2a_receive", "message": msg.to_dict()})
            return msg
        except queue.Empty:
            return None

    def broadcast(self, sender: str, content: dict, msg_type: str = "event"):
        """Broadcast a message to all agents."""
        with self.lock:
            for recipient in self.queues.keys():
                if recipient != sender:
                    msg = A2AMessage(sender, recipient, content, msg_type)
                    self.queues[recipient].put(msg)
                    log_event({"event": "a2a_broadcast", "message": msg.to_dict()})
