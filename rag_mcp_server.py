import os
import sys

# Optional: Disable huggingface symlink warnings on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from mcp.server.fastmcp import FastMCP

# Initialize vector store
data_path = os.path.join(os.path.dirname(__file__), "data", "sample_mental_health_docs.txt")
retriever = None

try:
    if os.path.exists(data_path):
        loader = TextLoader(data_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)
        
        # Use a small, fast local embedding model
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(docs, embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    else:
        print(f"Warning: Data file not found at {data_path}", file=sys.stderr)
except Exception as e:
    print(f"Error initializing vector store: {e}", file=sys.stderr)

# Create MCP server
mcp = FastMCP("mental_health_rag")

@mcp.tool()
def retrieve_mental_health_resources(query: str) -> str:
    """
    Retrieve relevant mental health context, coping strategies, and guidelines based on the user's query.
    Use this tool when you need evidence-based strategies or specific advice for a given mental state.
    """
    if not retriever:
        return "Error: RAG system is not initialized."
    
    results = retriever.invoke(query)
    if not results:
        return "No relevant information found."
    
    formatted_results = "\n\n---\n\n".join([doc.page_content for doc in results])
    return formatted_results

if __name__ == "__main__":
    mcp.run()
