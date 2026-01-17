import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import SystemMessage, HumanMessage
from configs import CHAT_LLM_CONFIG


async def run_chat():
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "task_storage_service"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the tools
            await session.initialize()

            # Load the tools from the MCP server
            tools = await load_mcp_tools(session)

            # Initialize the LLM with the tools
            llm = ChatOllama(model=CHAT_LLM_CONFIG["MODEL"])
            llm_with_tools = llm.bind_tools(tools)

            # Create the graph
            builder = StateGraph(MessagesState)

            # Define the chatbot node
            def chatbot(state: MessagesState):
                return {"messages": [llm_with_tools.invoke(state["messages"])]}

            # Add nodes
            builder.add_node("chatbot", chatbot)
            builder.add_node("tools", ToolNode(tools))

            # Add edges
            builder.add_edge(START, "chatbot")
            builder.add_conditional_edges("chatbot", tools_condition)
            builder.add_edge("tools", "chatbot")

            # Compile the graph
            graph = builder.compile()
            # System message
            messages = [SystemMessage(content=CHAT_LLM_CONFIG["SYSTEM_PROMPT"])]

            # Interactive loop (or simple run as requested, but loop is better for chat)
            print("Chat with AI driven task manager (type 'exit' or 'quit' or 'q' to stop):")
            while True:
                user_input = input("User: ")
                if user_input.lower() in ["exit", "quit", "q"]:
                    break
                messages.append(HumanMessage(content=user_input))

                # Stream the output
                async for event in graph.astream({"messages": messages}, stream_mode="values"):
                    # event["messages"][-1].pretty_print()
                    # print(event["messages"][-1].type)
                    if event["messages"][-1].type == "human":
                        pass
                    elif event["messages"][-1].type == "ai":
                        print(event["messages"][-1].content)
                    elif event["messages"][-1].type == "tool":
                        # for understanding internal working of mcp server
                        # print("tool called: ", event["messages"][-1].name)
                        # print("tool reply: ", event["messages"][-1].content)
                        pass

                # Re-run to just get the final response for simplicity in this loop or use invoke
                final_state = await graph.ainvoke({"messages": messages})
                messages = final_state["messages"]


def run() -> None:
    asyncio.run(run_chat())


if __name__ == "__main__":
    pass
