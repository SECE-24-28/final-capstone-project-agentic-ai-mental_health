import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Load environment variables from .env if present
load_dotenv()

# Global state
mcp_client = None
mcp_session_context = None
mcp_session = None
mcp_tools = None
llm = None
retrieve_tool = None

server_path = os.path.join(os.path.dirname(__file__), "rag_mcp_server.py")

SYSTEM_PROMPT = """You are Serenity, an empathetic, compassionate, and professional mental health assistant.

Your role:
- Listen carefully and validate the user's feelings.
- Provide evidence-based coping strategies using the CONTEXT provided below.
- Never provide medical diagnoses; offer emotional support and practical strategies instead.
- If you suspect a crisis or self-harm, urge them to contact emergency services (988 Suicide & Crisis Lifeline).
- Keep responses warm, human, and conversational. Use bullet points or numbered lists for actionable advice.

CONTEXT (use this information to support your response):
{context}

If the context is not relevant, rely on your general knowledge to provide compassionate support."""

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mcp_client, mcp_session_context, mcp_session, mcp_tools, llm, retrieve_tool
        
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
        
        # Find the retrieve tool
        for tool in mcp_tools:
            if tool.name == "retrieve_mental_health_resources":
                retrieve_tool = tool
                break
        
        print(f"MCP Tools loaded: {[t.name for t in mcp_tools]}", flush=True)
        
        # Initialize LLM (no agent/tool-calling needed — we call the tool ourselves)
        llm = ChatOllama(model="hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest", temperature=0.3)
        print("LLM initialized.", flush=True)
        
    except Exception as e:
        print(f"Failed to initialize: {e}", file=sys.stderr)

    yield

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
    if not llm:
        raise HTTPException(status_code=500, detail="LLM is not initialized. Check server logs.")
    
    # Step 1: Always retrieve relevant context from the MCP RAG tool
    context = "No additional context available."
    if retrieve_tool:
        try:
            context = await retrieve_tool.ainvoke({"query": request.message})
            print(f"Retrieved context ({len(context)} chars)", flush=True)
        except Exception as e:
            print(f"RAG retrieval failed: {e}", file=sys.stderr)
    
    # Step 2: Build the messages with context injected into the system prompt
    system_msg = SystemMessage(content=SYSTEM_PROMPT.format(context=context))
    
    messages = [system_msg]
    for msg in request.history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))
    messages.append(HumanMessage(content=request.message))
    
    # Step 3: Call the LLM directly (no agent, no tool-calling issues)
    try:
        response = await llm.ainvoke(messages)
        output = response.content
        
        # Safety: if the model accidentally outputs JSON/tool-call text, clean it
        if output.strip().startswith('{"name"') or output.strip().startswith('[{"'):
            output = ("I hear you, and I want you to know that your feelings are completely valid. "
                      "It sounds like you're going through a really tough time. "
                      "Please take a moment to breathe deeply. "
                      "Consider talking to a trusted friend or a mental health professional who can provide personalized support. "
                      "You are not alone in this.")
        
        return {"response": output}
    except Exception as e:
        error_msg = str(e)
        if "connection refused" in error_msg.lower() or "connect" in error_msg.lower():
            return {"response": "⚠️ **Ollama Error:** The local AI server could not be reached. Make sure Ollama is installed and running."}
            
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
