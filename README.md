# Boston Chatbot FastAPI

Small FastAPI service that exposes your Retrieval‑Augmented Generation chatbot at `/api/v1/chat`.

## Quick start

```bash
# Create virtual‑env
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make sure `.env` contains your keys
cp main.env .env  # if you haven't already

# Launch server (reload for dev)
uvicorn app.main:app --reload
```

POST a JSON payload:

```json
{
  "message": "Tell me about the 2024 Boston Marathon winners"
}
```

and you'll get:

```jsonc
{
  "response": "..."
}
```

## Project layout
```
chatbot_api/
├── app/               # FastAPI application
│   ├── core/          # config & LlamaIndex helpers
│   └── api/v1/        # versioned REST endpoints
├── data/              # auxiliary data (e.g. scraped_data.pkl)
└── .env               # API keys (never commit!)
```

## Notes
* The LlamaIndex query engine is initialised lazily and cached, so the first request might be slower.
* Adjust CORS settings in `app/main.py` for production.