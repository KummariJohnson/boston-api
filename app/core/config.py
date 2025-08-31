"""Centralised configuration, loaded from .env"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY: str | None = os.getenv("PINECONE_API_KEY")
PINECONE_ENV: str | None = os.getenv("PINECONE_ENV")
PINECONE_INDEX: str | None = os.getenv("PINECONE_INDEX")