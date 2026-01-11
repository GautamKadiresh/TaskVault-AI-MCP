from mcp.server.fastmcp import FastMCP


class TaskStorageMcpServer:
    def __init__(self):
        self.mcp = FastMCP("task_storage_mcp_server")
        self.task_list_storage = []
        
        @self.mcp.tool()
        def add_task(desc: str = "") -> str:
            """Add a new task to the local to-do list."""
            id = self.id_generator(desc)
            self.task_list_storage.append({"id": id, "desc": desc})
            return f"Successfully added task: {desc} with id: {id}"

        @self.mcp.tool()
        def list_tasks() -> list:
            """Retrieve all current tasks."""
            return self.task_list_storage

    def id_generator(self, desc: str = ""):
            return hash(desc)

    def run(self):
        self.mcp.run(transport="stdio")

if __name__ == '__main__':
    server = TaskStorageMcpServer()
    server.run()