from typing import Annotated
from pydantic import Field
from mcp.server.fastmcp import FastMCP
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from configs import VECTOR_DB_CONFIG
import os
import hashlib


class TaskStorageMcpServer:
    def __init__(self, clean_db=False):
        print(__name__)
        self.mcp = FastMCP("task_storage_mcp_server")
        self.task_list_storage = []
        self.vector_store = Chroma(
            collection_name="task_storage",
            embedding_function=OllamaEmbeddings(model=VECTOR_DB_CONFIG["EMBEDDING_MODEL"]),
            persist_directory=os.path.join(os.getcwd(), VECTOR_DB_CONFIG["DB_LOCATION"]),
        )

        if clean_db:
            # for cleaning db
            task_ids_to_del = self.vector_store.get()["ids"]
            if len(task_ids_to_del) > 0:
                self.vector_store.delete(ids=task_ids_to_del)

        @self.mcp.tool(
            name="add_task",
            description="Add a new task to the local to-do list. input is description and (optional)priority",
        )
        def add_task(
            description: Annotated[str, Field(description="Description of the task to add")],
            priority: Annotated[
                int,
                Field(ge=1, le=5, description="Priority of the task (1 to 5, 1 assigned for highest priority tasks)"),
            ] = 5,
        ) -> str:
            """Add a new task to the local to-do list."""
            task_id = self.task_id_generator(description)
            documents = [
                Document(
                    page_content=description,
                    metadata={"priority": priority},
                    task_id=task_id,
                )
            ]
            self.vector_store.add_documents(documents=documents, ids=[task_id])
            return f'Successfully added task: "{description}" with task_id: {task_id} and priority: {priority}'

        @self.mcp.tool(
            name="delete_tasks",
            description="Delete a task from the local to-do list using the task_id. The task_id for all tasks can be fetched using list_tasks tool.",
        )
        def delete_tasks(
            task_ids: Annotated[list[str], Field(description="List of task_ids of the tasks to delete")],
        ) -> str:
            """Delete a task from the local to-do list using the task_id."""
            self.vector_store.delete(ids=task_ids)
            return f"Successfully deleted tasks with task_ids: {task_ids}"

        @self.mcp.tool(name="list_tasks", description="Retrieve all current tasks.")
        def list_tasks() -> list:
            """Retrieve all current tasks."""
            result = self.vector_store.get()
            all_tasks = []
            for i in range(len(result["ids"])):
                all_tasks.append(
                    {
                        "description": result["documents"][i],
                        "task_id": result["ids"][i],
                        "priority": result["metadatas"][i]["priority"],
                    }
                )
            if len(all_tasks) == 0:
                return ["No tasks found"]
            return all_tasks

        @self.mcp.tool(name="search_tasks_by_priority", description="Retrieve all tasks with the given priority.")
        def search_tasks_by_priority(
            priority: Annotated[
                int,
                Field(
                    ge=1,
                    le=5,
                    description="List tasks with the given priority (1 to 5, 1 assigned for highest priority tasks)",
                ),
            ],
        ) -> list:
            """Retrieve all tasks with the given priority."""
            result = self.vector_store.get(where={"priority": priority})
            all_tasks = []
            for i in range(len(result["ids"])):
                all_tasks.append(
                    {
                        "description": result["documents"][i],
                        "task_id": result["ids"][i],
                        "priority": result["metadatas"][i]["priority"],
                    }
                )
            if len(all_tasks) == 0:
                return ["No tasks found"]
            return all_tasks

        @self.mcp.tool(name="search_tasks_by_similarity", description="Search tasks with similar words.")
        def search_tasks_by_similarity(
            query: Annotated[
                str, Field(description="Query words to search for tasks. Tasks will be fetched using vector search")
            ],
        ) -> list:
            """Search tasks with similar words."""
            result = self.vector_store.similarity_search(query)
            all_tasks = []
            for i in range(len(result)):
                all_tasks.append(
                    {
                        "description": result[i].page_content,
                        "task_id": result[i].id,
                        "priority": result[i].metadata["priority"],
                    }
                )
            if len(all_tasks) == 0:
                return ["No tasks found"]
            return all_tasks

    def task_id_generator(self, description: str = ""):
        """Generate a unique task_id for a given description."""
        return hashlib.shake_256(description.encode("utf8")).hexdigest(5)


def main():
    server = TaskStorageMcpServer()
    server.mcp.run(transport="stdio")


if __name__ == "__main__":
    print("Running task storage service as a standalone mcp server")
    main()
