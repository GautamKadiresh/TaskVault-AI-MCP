import pytest
import asyncio
import json
from taskvault_ai_mcp.mcp_server.task_storage_service import TaskStorageMcpServer


@pytest.fixture
def server():
    # start server with no tasks stored
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
async def test_search_task_by_priority(server):
    # Step 1: Add a dummy task and confirm it is added
    await server.mcp.call_tool("add_task", arguments={"description": "Dummy Task", "priority": 1})
    await server.mcp.call_tool("add_task", arguments={"description": "Dummy Task 2", "priority": 5})

    # Step 2: Search all task by priority 1
    task_lists = await server.mcp.call_tool("search_tasks_by_priority", arguments={"priority": 1})
    assert len(task_lists) == 1
    assert json.loads(task_lists[0].text)["description"] == "Dummy Task"
    assert json.loads(task_lists[0].text)["task_id"] == server.task_id_generator("Dummy Task")
    assert json.loads(task_lists[0].text)["priority"] == 1

    # Step 3: cleanup after the test
    await server.mcp.call_tool(
        "delete_tasks",
        arguments={"task_ids": [server.task_id_generator("Dummy Task"), server.task_id_generator("Dummy Task 2")]},
    )
    task_lists = await server.mcp.call_tool("list_tasks", arguments={})
    assert task_lists[0].text == "No tasks found"


@pytest.mark.asyncio
async def test_search_tasks_by_similarity(server):
    # Step 1: Add task to make pasta. This is a cooking related task.
    await server.mcp.call_tool("add_task", arguments={"description": "Make some pasta"})

    # Step 2: Search all task related to cooking.
    task_lists = await server.mcp.call_tool("search_tasks_by_similarity", arguments={"query": "cooking"})
    assert len(task_lists) == 1
    assert json.loads(task_lists[0].text)["description"] == "Make some pasta"
    assert json.loads(task_lists[0].text)["task_id"] == server.task_id_generator("Make some pasta")

    # Step 3: cleanup after the test
    await server.mcp.call_tool("delete_tasks", arguments={"task_ids": [server.task_id_generator("Make some pasta")]})
    task_lists = await server.mcp.call_tool("list_tasks", arguments={})
    assert task_lists[0].text == "No tasks found"


@pytest.mark.asyncio
async def test_mcp_server_list_tools(server):
    all_tools = await server.mcp.list_tools()
    assert len(all_tools) == 5
    tool_names = [tool.name for tool in all_tools]
    assert "add_task" in tool_names
    assert "list_tasks" in tool_names
    assert "delete_tasks" in tool_names
    assert "search_tasks_by_priority" in tool_names
    assert "search_tasks_by_similarity" in tool_names
    for tool in all_tools:
        # test the input schema, required fields and accepted values of each tool
        if tool.name == "add_task":
            # test the input schema of add task. mandatory is description. optional is priority
            assert "description" in tool.inputSchema["properties"]
            assert tool.inputSchema["required"] == ["description"]
            assert "priority" in tool.inputSchema["properties"]
            assert tool.inputSchema["properties"]["priority"]["type"] == "integer"
            assert tool.inputSchema["properties"]["priority"]["minimum"] == 1
            assert tool.inputSchema["properties"]["priority"]["maximum"] == 5

        if tool.name == "delete_tasks":
            assert "task_ids" in tool.inputSchema["properties"]
            assert tool.inputSchema["required"] == ["task_ids"]

        if tool.name == "list_tasks":
            assert "required" not in tool.inputSchema

        if tool.name == "search_tasks_by_priority":
            # test the input schema of search_tasks_by_priority. mandatory is priority
            assert "priority" in tool.inputSchema["properties"]
            assert tool.inputSchema["required"] == ["priority"]
            assert tool.inputSchema["properties"]["priority"]["type"] == "integer"
            assert tool.inputSchema["properties"]["priority"]["minimum"] == 1
            assert tool.inputSchema["properties"]["priority"]["maximum"] == 5

        if tool.name == "search_tasks_by_similarity":
            # test the input schema of search_tasks_by_similarity. mandatory is query
            assert "query" in tool.inputSchema["properties"]
            assert tool.inputSchema["required"] == ["query"]
