[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/s7J27iqd)

# Agentic AI Mental Health Chatbot

An empathetic, local, and fully private AI Mental Health Chatbot powered by LangGraph, FastAPI, and local LLMs (Qwen 2.5 via Ollama). This application uses RAG (Retrieval-Augmented Generation) combined with the Model Context Protocol (MCP) to provide evidence-based mental health resources.

## Features
- **100% Local & Private:** Runs entirely on your own machine using Ollama. No API keys or external data sending required.
- **Agentic RAG Pipeline:** Uses LangGraph to intelligently trigger RAG lookups when users discuss anxiety or depression.
- **Model Context Protocol (MCP):** Cleanly separates the backend vector store tools from the main agent executor.
- **Premium Web UI:** A beautiful, responsive glassmorphism web interface built with pure HTML/CSS/JS.

## Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) (to run the local LLM)

## Installation & Setup

1. **Clone the repository and install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Download the local model (Qwen 2.5):**
   Ensure Ollama is running in the background, then pull the model:
   ```bash
   ollama pull qwen2.5
   ```

3. **Start the Web Application:**
   ```bash
   python api.py
   ```
   Open your browser to `http://localhost:8000` to chat with the bot!

## Architecture
- `api.py`: FastAPI backend that hosts the LangGraph agent and serves the frontend.
- `rag_mcp_server.py`: Local MCP server that handles FAISS vector store creation and the RAG tools.
- `static/`: HTML/CSS/JS files for the premium glassmorphism frontend.
