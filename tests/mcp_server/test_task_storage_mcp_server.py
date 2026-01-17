import pytest
import asyncio
import json
from taskvault_ai_mcp.mcp_server.task_storage_service import TaskStorageMcpServer


@pytest.fixture
def server():
    # start server with no tasks stores
    return TaskStorageMcpServer(clean_db=True)


@pytest.mark.asyncio
async def test_add_and_delete_tasks(server):

    # Step 1: Add a dummy task and confirm it is added
    await server.mcp.call_tool("add_task", arguments={"description": "Dummy Task"})
    task_lists = await server.mcp.call_tool("list_tasks", arguments={})
    assert len(task_lists) == 1
    assert json.loads(task_lists[0].text)["description"] == "Dummy Task"
    assert json.loads(task_lists[0].text)["task_id"] == server.task_id_generator("Dummy Task")
    assert json.loads(task_lists[0].text)["priority"] == 5

    # Step 2: Delete the dummy task and confirm it is deleted
    await server.mcp.call_tool("delete_tasks", arguments={"task_ids": [json.loads(task_lists[0].text)["task_id"]]})
    task_lists = await server.mcp.call_tool("list_tasks", arguments={})
    assert task_lists[0].text == "No tasks found"


@pytest.mark.asyncio
async def test_mcp_server_list_tools(server):
    all_tools = await server.mcp.list_tools()
    assert len(all_tools) == 3
    tool_names = [tool.name for tool in all_tools]
    assert "add_task" in tool_names
    assert "list_tasks" in tool_names
    assert "delete_tasks" in tool_names
    for tool in all_tools:
        if tool.name == "add_task":
            print(tool)
            assert "description" in tool.inputSchema["properties"]
            assert tool.inputSchema["required"] == ["description"]
            assert "priority" in tool.inputSchema["properties"]
        if tool.name == "delete_tasks":
            assert "task_ids" in tool.inputSchema["properties"]
            assert tool.inputSchema["required"] == ["task_ids"]
        if tool.name == "list_tasks":
            assert "required" not in tool.inputSchema
