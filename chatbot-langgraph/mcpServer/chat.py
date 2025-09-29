from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()

async def main():
    client = MultiServerMCPClient({
        "math": {
            "command": "python",
            "args": ["mathserver.py"],
            "transport": "stdio"
        },
        "weather": {
            "url": "http://127.0.0.1:8000/mcp",
            "transport": "streamable-http"
        }
    })

    openai_api_key = os.getenv("OPENAI_API_KEY")
    tools = await client.get_tools()
    llm = ChatOpenAI(model="gpt-4o-mini",
                    api_key=openai_api_key,
                    temperature=0.2,
                    streaming=True)
    agent = create_react_agent(llm, tools)
    
    math_response = agent.ainvoke({"messages": [{"role": "user", "content": "What's (3+5)*12 ?"}]})
    print("Math response is : ", math_response["messages"][-1].content)
    
asyncio.run(main())