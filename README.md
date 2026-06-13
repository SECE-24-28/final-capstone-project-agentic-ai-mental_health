# Serenity AI: Agentic Mental Health Assistant

An empathetic, local, and fully private AI Mental Health Chatbot powered by LangChain, FastAPI, and local LLMs (Llama 3.2 / Qwen via Ollama). This application uses Retrieval-Augmented Generation (RAG) combined with the Model Context Protocol (MCP) to provide evidence-based mental health coping strategies and resources.

![Serenity AI Chat UI Screen](https://github.com/SECE-24-28/final-capstone-project-agentic-ai-mental_health/raw/main/static/index.html) *Note: Run the server and navigate to http://localhost:8000 to interact with the web interface.*

## Features

- **100% Local & Private:** Runs entirely on your own machine using Ollama. No API keys or external data transmission required.
- **RAG via FastMCP:** The backend connects to a local MCP server running a FAISS vector database to retrieve context-relevant mental health advice dynamically.
- **Robust Model Integration:** Clean LangChain configuration using local GGUF models. It handles input schemas and cleans output structures automatically to prevent raw parameter bleeding.
- **ChatGPT-Style Dark Theme UI:**
  - **Collapsible Sidebar:** "New chat" button, chat history management (Recents), and user details.
  - **Centered Input & Welcome Area:** Minimalist layout matching ChatGPT's design aesthetic.
  - **Responsive Input Bar:** Auto-resizing textarea with intuitive controls, custom suggestion pills, and typing status indicators.

---

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) (installed and running in the background)

---

## Installation & Setup

1. **Clone the Repository & Navigate to Workspace:**
   ```bash
   cd final-capstone-project-agentic-ai-mental_health
   ```

2. **Install Dependencies:**
   Ensure your virtual environment is active, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Pull the Local LLM:**
   Make sure Ollama is running in your taskbar/background, then download the model:
   ```bash
   ollama pull hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest
   ```

4. **Start the Web Application:**
   Run the following single-line command in your terminal:
   ```bash
   python api.py
   ```

5. **Open the App:**
   Navigate to [http://localhost:8000](http://localhost:8000) in your web browser. 
   *(If your browser shows the old style, do a hard refresh with `Ctrl + F5` or `Ctrl + Shift + R` to clear the cache).*

---

## Architecture & Codebase

- `api.py`: FastAPI server hosting the chat API endpoint, handling system prompts, connecting to the MCP client, and serving the static files.
- `rag_mcp_server.py`: FastMCP server that splits, embeds, and indexes the local documentation (`data/sample_mental_health_docs.txt`) into a FAISS vector database and exposes the `retrieve_mental_health_resources` tool.
- `chatbot_client.py`: An alternate CLI terminal client for chatting with the agent directly from the command line.
- `static/`:
  - `index.html`: UI structure containing sidebar navigation, chat container, welcome viewport, and inputs.
  - `style.css`: Modern ChatGPT-style dark theme styling.
  - `script.js`: Client-side logic for markdown formatting, local chat history, suggestions, and auto-resizing textareas.
