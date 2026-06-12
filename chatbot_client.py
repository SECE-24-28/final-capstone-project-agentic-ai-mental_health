import os
import sys
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

async def main():
    load_dotenv()

    print("Initializing Mental Health Chatbot...", flush=True)
    server_path = os.path.join(os.path.dirname(__file__), "rag_mcp_server.py")
    
    # Configure MCP Client to connect to our local server
    client = MultiServerMCPClient({
        "mental_health_server": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [server_path],
        }
    })

    print("Connecting to MCP server and fetching tools...", flush=True)
    
    async with client.session("mental_health_server") as session:
        try:
            tools = await load_mcp_tools(session)
        except Exception as e:
            print(f"Error fetching tools: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Initialize LLM
        llm = ChatOllama(model="hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest", temperature=0.3)
        
        # Define the system message
        system_message = (
            "You are an empathetic, compassionate, and professional mental health assistant. "
            "Your goal is to support the user, analyze their mental state based on their messages, "
            "and provide evidence-based coping strategies. "
            "ALWAYS use the `retrieve_mental_health_resources` tool to find appropriate advice when the user expresses distress, anxiety, or depression. "
            "If you suspect a crisis, urge them to contact emergency services. "
            "Never provide medical diagnoses; offer support and strategies instead."
        )
        
        # Create the agent
        agent_executor = create_react_agent(llm, tools, prompt=system_message)
        
        print("\n=== Mental Health Assistant Ready ===")
        print("Type 'exit' or 'quit' to end the session.")
        print("---------------------------------------\n")
        
        chat_history = []
        
        while True:
            try:
                user_input = input("You: ")
                if user_input.lower() in ['exit', 'quit']:
                    break
                
                # Run the agent
                chat_history.append(HumanMessage(content=user_input))
                
                response = await agent_executor.ainvoke({
                    "messages": chat_history
                })
                
                output = response["messages"][-1].content
                print(f"\nAssistant: {output}\n")
                
                # Update history with the full message list
                chat_history = response["messages"]
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\nAn error occurred: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())
