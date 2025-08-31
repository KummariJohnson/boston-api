from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Import the get_query_engine function from your llm.py
# The path is relative to the 'app' directory, so 'app.core.llm'
from app.core.llm import get_query_engine

# --- APIRouter Initialization ---
router = APIRouter() # You can add tags here if you wish, e.g., tags=["chatbot"]

# --- Global Variable for Query Engine ---
# This will hold the cached query engine instance, initialized once on startup
cached_query_engine = None

# --- Initialization Function ---
# This function is decorated with @router.on_event("startup")
# It will be called automatically by FastAPI when the application starts up.
# This ensures that the LlamaIndex query engine is initialized only once.
@router.on_event("startup")
async def startup_event():
    global cached_query_engine
    print("Startup event triggered: Initializing chatbot components via get_query_engine()...")
    try:
        # Call the cached function from llm.py to get the query engine
        cached_query_engine = get_query_engine()
        print("Chatbot initialization complete on startup.")
    except Exception as e:
        # If initialization fails, print a fatal error and potentially re-raise
        # to prevent the server from starting with a broken chatbot.
        print(f"FATAL ERROR during chatbot initialization: {e}")
        # Depending on your deployment strategy, you might want to raise the exception
        # raise e # Uncomment to prevent server startup on init failure


# --- Request Body Schema for Chat Endpoint ---
# Defines the expected structure of the JSON payload for the /chat endpoint
class ChatRequest(BaseModel):
    query: str # Expects a single string field named 'query'

# --- Chat Endpoint ---
# Defines the POST endpoint for handling chat requests
@router.post("/chat")
async def chat_endpoint(request_body: ChatRequest):
    """
    Receives a user query and returns a chatbot response with source chunks.
    """
    user_query = request_body.query # Extract the query from the request body

    # Check if the query engine has been successfully initialized
    if cached_query_engine is None:
        raise HTTPException(status_code=500, detail="Chatbot not initialized. Server startup failed or is incomplete.")

    try:
        # Use the globally cached query engine to process the user's query
        response = cached_query_engine.query(user_query)
        bot_answer = str(response) # Convert the LlamaIndex Response object to a string for the answer

        # Extract source nodes (chunks) if available
        source_chunks = []
        if response.source_nodes:
            for i, node in enumerate(response.source_nodes):
                source_chunks.append({
                    "chunk_id": i + 1,
                    "score": round(node.score, 2), # Round score for cleaner output
                    "url": node.metadata.get('url', 'N/A'), # Get URL from metadata, default to 'N/A'
                    "title": node.metadata.get('title', 'N/A'), # Get title from metadata, default to 'N/A'
                    "text_snippet": node.text[:200] + "..." # Take first 200 characters as a snippet
                })

        # Return the answer and source chunks as a JSON response
        return {
            "answer": bot_answer,
            "source_chunks": source_chunks
        }

    except Exception as e:
        # Catch any exceptions during query processing and return a 500 error
        print(f"Error during query: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred during query processing: {str(e)}")

