import os
import asyncio

from langchain_core.messages import AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

def get_env_or_default(var_name: str, default: str) -> str:
    val = os.environ.get(var_name, default)
    if val.endswith("/"):
        val = val.rstrip("/")
    return val

async def main():
    ollama_base = get_env_or_default("OLLAMA_BASE_URL", "http://localhost:11434")
    mcp_server_url = get_env_or_default("MCP_SERVER_URL", "http://localhost:8160/mcp")
    ollama_model = get_env_or_default("OLLAMA_MODEL_NAME", "qwen3:8b")

    client = MultiServerMCPClient(
        {
            "geonames": {
                "url": mcp_server_url,
                "transport": "streamable_http",
            }
        }
    )

    llm = ChatOllama(model=ollama_model, reasoning=False, base_url=ollama_base)

    tools = await client.get_tools()
    agent = create_react_agent(llm, tools)

    sysmsg = {
        "role": "system",
        "content": (
            "You are a helpful for find countries and citis. "
            "respond briefly and concisely and in the language of the request"
        ),
    }

    msgs = [sysmsg, {"role": "user", "content": "give me city name of  E3Y on Canada"}]
    print("👤: give me city name of  E3Y on Canada")
    response = await agent.ainvoke({"messages": msgs})
    for res in response["messages"]:
        if isinstance(res, AIMessage):
            if res.content:
                print(f"🤖: {res.content}")
    print("-"*50)
    msgs = [
        sysmsg,
        {"role": "user", "content": "Cerca la label indirizzo per strada dele cacce 91 con cap 10135"},
    ]
    print("👤: Cerca la label indirizzo per strada dele cacce 91 con cap 10135")
    response = await agent.ainvoke({"messages": msgs})
    for res in response["messages"]:
        if isinstance(res, AIMessage):
            if res.content:
                print(f"🤖: {res.content}")
    print("-"*50)
    msgs = [
        sysmsg,
        {"role": "user", "content": "Cerca il codice postale di Alba in Italia"},
    ]
    print("👤: Cerca il codice postale di Alba in Italia, rispondi in inglese")
    response = await agent.ainvoke({"messages": msgs})
    for res in response["messages"]:
        if isinstance(res, AIMessage):
            if res.content:
                print(f"🤖: {res.content}")
    print("-" * 50)

    msgs = [
        sysmsg,
        {
            "role": "user",
            "content": "Cerca il codice postale di tute le citta' che iniziano con Alba in Italia",
        },
    ]
    print("👤: Cerca il codice postale di tute le citta' che iniziano con Alba in Italia")
    response = await agent.ainvoke({"messages": msgs})
    for res in response["messages"]:
        if isinstance(res, AIMessage):
            if res.content:
                print(f"🤖: {res.content}")
    print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
