from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the router from your endpoints file
# This path assumes your file structure is:
# CHATBOT_API/
# ├── app/
# │   ├── api/
# │   │   ├── v1/
# │   │   │   └── endpoints.py
# │   │   └── __init__.py
# │   └── __init__.py
# └── main.py (this file)
from app.api.v1.endpoints import router as api_router

# Initialize the FastAPI application
app = FastAPI(title="Boston Chatbot API", version="1.0.0")

# Configure CORS middleware
# This allows your frontend (even if served from a different origin) to
# make requests to your backend API.
# In a production environment, you should replace "*" with the specific
# origin(s) of your frontend application(s) for security.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include the API router
# All endpoints defined in api_router (e.g., /chat) will be prefixed with /api/v1
# So, your chat endpoint will be accessible at /api/v1/chat
app.include_router(api_router, prefix="/api/v1")

# You can add a simple root endpoint for testing if needed
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Boston Chatbot API! Access /docs for API documentation."}

