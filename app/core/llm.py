import os
import pickle
from functools import lru_cache

from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import StorageContext, VectorStoreIndex, Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.core.settings import Settings

# Import configuration variables directly from config.py
# This assumes app/core/config.py exists and defines these variables.
from .config import (
    PINECONE_API_KEY,
    PINECONE_ENV,
    PINECONE_INDEX,
    GOOGLE_API_KEY
)

# Define the path to scraped_data.pkl relative to the project root
# This script is in CHATBOT_API/app/core/llm.py
# scraped_data.pkl is in CHATBOT_API/data/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SCRAPED_DATA_PATH = os.path.join(BASE_DIR, 'data', 'scraped_data.pkl')


@lru_cache(maxsize=1)
def get_query_engine():
    """Return (and cache) a LlamaIndex query engine for RAG."""
    print("Initializing LlamaIndex components in llm.py...")

    # Validate environment variables are loaded via config.py
    if not all([PINECONE_API_KEY, PINECONE_ENV, PINECONE_INDEX, GOOGLE_API_KEY]):
        raise ValueError(
            "One or more environment variables (PINECONE_API_KEY, PINECONE_ENV, "
            "PINECONE_INDEX, GOOGLE_API_KEY) are not set. "
            "Please check your .env file and config.py."
        )

    # --- 1. Load documents from pickle file ---
    documents = []
    try:
        with open(SCRAPED_DATA_PATH, "rb") as f:
            raw_data = pickle.load(f)
        print(f"Loaded {len(raw_data)} raw data entries from '{SCRAPED_DATA_PATH}'.")
    except FileNotFoundError:
        print(f"Warning: scraped_data.pkl not found at {SCRAPED_DATA_PATH}. "
              "Proceeding assuming Pinecone index is fully populated.")
        raw_data = []
    except Exception as e:
        raise IOError(f"Error loading scraped_data.pkl: {e}")

    for item in raw_data:
        content = item.get("content")
        if content:
            documents.append(
                Document(
                    text=content,
                    metadata={
                        "url": item.get("url", "N/A"),
                        "title": item.get("title", "N/A")
                    }
                )
            )
    print(f"Converted {len(documents)} entries into LlamaIndex Documents (if scraped_data.pkl was found).")


    # --- 2. Connect to Pinecone (v3 client) ---
    pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
    pinecone_index = pc.Index(PINECONE_INDEX)
    print(f"Successfully connected to existing Pinecone index: {PINECONE_INDEX}")

    # --- 3. Wrap Pinecone index for LlamaIndex ---
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # --- 4. Embedding model (CPU-friendly) ---
    embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    print(f"Using embedding model: {embed_model.model_name}")

    # --- 5. Set up Google Generative AI LLM ---
    llm = GoogleGenAI(
        model="models/gemini-1.5-pro-latest",
        api_key=GOOGLE_API_KEY,
        temperature=0.3,
        max_output_tokens=512
    )
    print(f"Using LLM: {llm.model}")

    # --- 6. Apply LLM and Embedding Model to LlamaIndex global settings ---
    Settings.llm = llm
    Settings.embed_model = embed_model
    print("LlamaIndex global settings configured (LLM and Embedding Model).")

    # --- 7. Re-create the VectorStoreIndex and QueryEngine ---
    vector_index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context,
        embed_model=embed_model
    )
    print("Index loaded from Pinecone.")

    query_engine = vector_index.as_query_engine(
        response_mode="tree_summarize",
        llm=llm
    )
    print("RAG Query engine created.")

    return query_engine
