"""
Enhanced structured logging with tracing support.
"""

import logging
import json
import uuid
import datetime

# Configure base logger
logger = logging.getLogger("ERPSystem")
logger.setLevel(logging.DEBUG)

# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)


def log_event(event: dict, trace_id: str = None):
    """
    Log an event in structured JSON format.
    :param event: dict containing event details
    :param trace_id: optional trace identifier for correlation
    """
    if not trace_id:
        trace_id = str(uuid.uuid4())

    structured = {
        "trace_id": trace_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "event": event
    }

    logger.info(json.dumps(structured))
    return trace_id


def start_trace():
    """Generate a new trace ID for a workflow run."""
    return str(uuid.uuid4())
