import datetime

def log_event(entry):
    """
    Log events with timestamp (console for simplicity).
    """
    timestamp = datetime.datetime.now().isoformat()
    print(f"[{timestamp}] LOG: {entry}")

def calculate_metric(metric_name, data):
    """
    Example KPI calculation.
    """
    if metric_name == "employee_count":
        return {"status": "success", "metric": metric_name, "value": len(data.get("employees", {}))}
    elif metric_name == "total_orders":
        return {"status": "success", "metric": metric_name, "value": len(data.get("orders", {}))}
    return {"status": "error", "message": "Unknown metric"}
