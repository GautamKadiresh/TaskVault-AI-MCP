import pytest
import asyncio
import json
from taskvault_ai_mcp.mcp_server.task_storage_service import TaskStorageMcpServer

@pytest.fixture
def server():
    return TaskStorageMcpServer()

@pytest.mark.asyncio
async def test_add_and_list_tasks(server):
    await server.mcp.call_tool("add_task", arguments={"desc": "Dummy Task"})
    task_lists = await server.mcp.call_tool("list_tasks", arguments={})
    assert json.loads(task_lists[0].text)["desc"] == "Dummy Task"
    assert json.loads(task_lists[0].text)["id"] == server.id_generator("Dummy Task")

@pytest.mark.asyncio
async def test_mcp_server_list_tools(server):
    all_tools = await server.mcp.list_tools()
    assert len(all_tools) == 2
    tool_names = [tool.name for tool in all_tools]
    assert "add_task" in tool_names
    assert "list_tasks" in tool_names