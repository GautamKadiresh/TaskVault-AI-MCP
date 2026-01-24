import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.messages import SystemMessage, HumanMessage
from configs import CHAT_LLM_CONFIG
from constants import (
    BOLD_RED,
    BOLD_GREEN,
    BOLD_YELLOW,
    BOLD_MAGENTA,
    DIM_CYAN,
    RESET_FONT,
)


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
            print(f"{BOLD_MAGENTA}Hello from TASK VAULT AI!{RESET_FONT}\n")

            # Interactive loop

            while True:
                print(f"\n{BOLD_RED}{'_'*100}{RESET_FONT}")
                print(
                    f"{BOLD_GREEN}Chat with AI driven task manager (type 'exit' or 'quit' or 'q' to stop){RESET_FONT}"
                )
                user_input = input()
                if user_input.lower() in ["exit", "quit", "q"]:
                    print(f"\n{BOLD_YELLOW}BYE!!{RESET_FONT}\n")
                    break
                messages.append(HumanMessage(content=user_input))

                # Stream the output. for debugging or internal monitoring
                async for event in graph.astream({"messages": messages}, stream_mode="values"):
                    messages.append(event["messages"][-1])
                    if event["messages"][-1].type == "human":
                        pass
                    elif event["messages"][-1].type == "ai":
                        if (
                            tools_condition(event["messages"]) != "tools"
                        ):  # only print ai messages which are meant for user and not tool calls
                            print(f"\n{BOLD_RED}{'_'*100}{RESET_FONT}")
                            print(f"{BOLD_MAGENTA}TASK VAULT AI:{RESET_FONT}")
                            print(event["messages"][-1].content)
                    # ## for understanding internal working of mcp server ###
                    #     else:
                    #         print(f"\n{BOLD_RED}{'_'*100}{RESET_FONT}")
                    #         tool_call_basic = lambda x: [{"name": i["name"], "args": i["args"]} for i in x]
                    #         print(
                    #             f"{DIM_CYAN}ai internal tool call message: {tool_call_basic(event['messages'][-1].tool_calls)}{RESET_FONT}"
                    #         )
                    # elif event["messages"][-1].type == "tool":
                    #     print(f"{DIM_CYAN}mcp tool called: {event['messages'][-1].name}{RESET_FONT}")
                    #     print(f"{DIM_CYAN}mcp server reply:\n {event['messages'][-1].content}{RESET_FONT}")


def run() -> None:
    asyncio.run(run_chat())


if __name__ == "__main__":
    pass
