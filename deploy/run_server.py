"""
Web/API interface for multi-agent deployment.
"""

from fastapi import FastAPI, Request
from agent_pkg.agent_manager import AgentManager
from agent_pkg.agent import ERPAgent
from tools.mcp import ToolCoordinator
from tools.custom_tools import InventoryTool, SalesTool, HRTool

app = FastAPI(title="Multi-Agent ERP System")

# Setup
modules = {}
tools = {
    "inventory": InventoryTool(),
    "sales": SalesTool(),
    "hr": HRTool()
}

tool_coordinator = ToolCoordinator(tools)
agent = ERPAgent(name="ERP-1", modules=modules, tool_coordinator=tool_coordinator)
manager = AgentManager([agent])


@app.post("/run")
async def run_agent(request: Request):
    data = await request.json()
    results = manager.run_sequential(data)
    return {"results": results}


@app.get("/health")
def health_check():
    return {"status": "ok"}
