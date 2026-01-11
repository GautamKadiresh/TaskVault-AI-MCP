from typing import Annotated
from pydantic import Field
from mcp.server.fastmcp import FastMCP


class TaskStorageMcpServer:
    def __init__(self):
        self.mcp = FastMCP("task_storage_mcp_server")
        self.task_list_storage = []

        @self.mcp.tool(name="add_task", description="Add a new task to the local to-do list.")
        def add_task(
            desc: Annotated[str, Field(description="Description of the task to add")],
            priority: Annotated[int, Field(ge=1, le=5, description="Priority of the task (1-5, 1 being highest)")] = 5,
        ) -> str:
            """Add a new task to the local to-do list."""
            id = self.id_generator(desc)
            self.task_list_storage.append({"id": id, "desc": desc, "priority": priority})
            return f"Successfully added task: {desc} with id: {id} and priority: {priority}"

        @self.mcp.tool(name="list_tasks", description="Retrieve all current tasks.")
        def list_tasks() -> list:
            """Retrieve all current tasks."""
            return self.task_list_storage

    def id_generator(self, desc: str = ""):
        return hash(desc)


if __name__ == "__main__":
    server = TaskStorageMcpServer()
    server.mcp.run(transport="stdio")
