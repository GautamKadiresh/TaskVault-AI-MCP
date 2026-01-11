from typing import Annotated
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from configs import VECTOR_DB_CONFIG
import os


class TaskStorageMcpServer:
    def __init__(self, clean_db=False):
        self.mcp = FastMCP("task_storage_mcp_server")
        self.task_list_storage = []
        self.vector_store = Chroma(
            collection_name="task_storage",
            embedding_function=OllamaEmbeddings(model=VECTOR_DB_CONFIG["EMBEDDING_MODEL"]),
            persist_directory=os.path.join(os.getcwd(), VECTOR_DB_CONFIG["DB_LOCATION"]),
        )

        if clean_db:
            # for cleaning db
            ids_to_del = self.vector_store.get()["ids"]
            if len(ids_to_del) > 0:
                self.vector_store.delete(ids=ids_to_del)

        @self.mcp.tool(name="add_task", description="Add a new task to the local to-do list.")
        def add_task(
            description: Annotated[str, Field(description="Description of the task to add")],
            priority: Annotated[int, Field(ge=1, le=5, description="Priority of the task (1-5, 1 being highest)")] = 5,
        ) -> str:
            """Add a new task to the local to-do list."""
            id = self.id_generator(description)
            documents = [
                Document(
                    page_content=description,
                    metadata={"priority": priority},
                    id=id,
                )
            ]
            self.vector_store.add_documents(documents=documents, ids=[id])
            return f"Successfully added task: {description} with id: {id} and priority: {priority}"

        @self.mcp.tool(
            name="delete_task",
            description="Delete a task from the local to-do list using the id. The id for all taks can be fetched using list_tasks tool.",
        )
        def delete_task(
            id: Annotated[str, Field(description="Id of the task to delete")],
        ) -> str:
            """Delete a task from the local to-do list using the id."""
            self.vector_store.delete(ids=[id])
            return f"Successfully deleted task with id: {id}"

        @self.mcp.tool(name="list_tasks", description="Retrieve all current tasks.")
        def list_tasks() -> list:
            """Retrieve all current tasks."""
            result = self.vector_store.get()
            all_tasks = []
            for i in range(len(result["ids"])):
                all_tasks.append(
                    {
                        "description": result["documents"][i],
                        "id": result["ids"][i],
                        "priority": result["metadatas"][i]["priority"],
                    }
                )
            return all_tasks

    def id_generator(self, description: str = ""):
        return str(hash(description))


if __name__ == "__main__":
    server = TaskStorageMcpServer()
    server.mcp.run(transport="stdio")
