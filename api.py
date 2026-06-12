import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any
from dotenv import load_dotenv
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Load environment variables from .env if present
load_dotenv()

# Global state for MCP
mcp_client = None
mcp_session_context = None
mcp_session = None
mcp_tools = None
llm = None
agent_executor = None

server_path = os.path.join(os.path.dirname(__file__), "rag_mcp_server.py")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mcp_client, mcp_session_context, mcp_session, mcp_tools, llm, agent_executor
        
    print("Initializing MCP Client...", flush=True)
    mcp_client = MultiServerMCPClient({
        "mental_health_server": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [server_path],
        }
    })
    
    try:
        mcp_session_context = mcp_client.session("mental_health_server")
        mcp_session = await mcp_session_context.__aenter__()
        mcp_tools = await load_mcp_tools(mcp_session)
        print("MCP Tools loaded successfully.", flush=True)
        
        # Initialize LLM & Agent
        llm = ChatOllama(model="qwen2.5", temperature=0.3)
        system_message = (
            "You are an empathetic, compassionate, and professional mental health assistant. "
            "Your goal is to support the user, analyze their mental state based on their messages, "
            "and provide evidence-based coping strategies. "
            "ALWAYS use the `retrieve_mental_health_resources` tool to find appropriate advice when the user expresses distress, anxiety, or depression. "
            "If you suspect a crisis, urge them to contact emergency services. "
            "Never provide medical diagnoses; offer support and strategies instead."
        )
        agent_executor = create_react_agent(llm, mcp_tools, prompt=system_message)
        print("Agent initialized.", flush=True)
        
    except Exception as e:
        print(f"Failed to initialize MCP Server: {e}", file=sys.stderr)

    yield # Server runs here
    
    # Cleanup
    if mcp_session_context:
        await mcp_session_context.__aexit__(None, None, None)
        
app = FastAPI(lifespan=lifespan)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage]

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if not agent_executor:
        raise HTTPException(status_code=500, detail="Agent is not initialized. Check server logs.")
        
    # Reconstruct history
    chat_history = []
    for msg in request.history:
        if msg.role == "user":
            chat_history.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            chat_history.append(AIMessage(content=msg.content))
            
    chat_history.append(HumanMessage(content=request.message))
    
    try:
        response = await agent_executor.ainvoke({
            "messages": chat_history
        })
        
        output = response["messages"][-1].content
        return {"response": output}
    except Exception as e:
        error_msg = str(e)
        if "connection refused" in error_msg.lower() or "connect" in error_msg.lower():
            return {"response": "⚠️ **Ollama Error:** The local AI server could not be reached. Make sure you have installed [Ollama](https://ollama.com) and it is running in the background."}
            
        print(f"Error during chat: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
