# BharatAI Chat - Full App (Scaffold)

This repository is a more complete scaffold for the BharatAI Chat idea:
- FastAPI backend with SQLAlchemy + Postgres (pgvector)
- Simple vector store wrapper and embeddings via sentence-transformers
- React web widget demo
- Docker Compose to run Postgres (+pgvector init), Redis, and backend

IMPORTANT: This scaffold is a developer-friendly starting point — not a turnkey production system.
Read the "Production Notes" section below before deploying to production.

## Quickstart (Linux/macOS)
1. Ensure Docker & Docker Compose are installed.
2. From the repo root run:
   ```bash
   docker compose up --build
   ```
3. Wait for Postgres to initialize (the init SQL creates pgvector and the documents table).
4. Start the widget (you need Node.js & npm):
   ```bash
   cd frontend/widget
   npm install
   npm start
   ```
5. Open http://localhost:1234 and talk to the demo widget (backend at http://localhost:8000).

## Notes / Next steps
- Embeddings: This scaffold uses `sentence-transformers` (all-MiniLM-L6-v2). For scale use a managed embeddings API or dedicated GPU instance.
- Vector store: Uses pgvector + Postgres. Ensure pgvector is installed on the Postgres instance in production.
- Security: Add HTTPS termination, OAuth/JWT auth, secrets in KMS, and rotate credentials.
- Compliance: DPDP, RBI, Aadhaar constraints are NOT implemented — treat all demo data as test-only.
- Scaling: Move to managed Postgres, Redis cluster, and run backend on Kubernetes with autoscaling.
- Language pipeline: Add language detection (fasttext or langid), translation gateway (IndicTrans2 or Bhashini), and ASR/TTS for voice.
- LLM: Replace the simple RAG reply with a proper prompt to an LLM (server-side) that conditions on retrieved docs.

## Structure
- backend/: FastAPI backend and DB models
- frontend/widget: simple React demo widget
- docker-compose.yml: to orchestrate db, redis, backend

## Running locally without Docker (optional)
- Create a Python venv, install backend/requirements.txt, set DATABASE_URL to a running Postgres, and run uvicorn app.main:app --reload

## License
MIT

## LLM integration
This scaffold now includes `backend/app/llm.py`, a small wrapper that will try to call OpenAI
if `OPENAI_API_KEY` is set in the environment. It builds a system prompt, includes the retrieved
documents, and asks the model to synthesize a concise, localized reply. Environment variables:
- `OPENAI_API_KEY` — your OpenAI API key
- `OPENAI_MODEL` — optional; defaults to `gpt-4o-mini` in the scaffold (change to your preferred model)

The `llm.generate_answer` function falls back to a conservative synthesis of the retrieved
documents if no API key or client is configured.

## New features added (streaming, LID/translation, WhatsApp adapter, hardening)
- **Streaming**: `/stream?q=...` SSE endpoint streams LLM tokens when `OPENAI_API_KEY` is set. The demo widget has a "Stream" button that listens to this endpoint.
- **Language detection & translation**: `backend/app/lang_utils.py` contains stubs for LID and translation. Replace stubs with fastText/langid models and IndicTrans2/Bhashini integration for production.
- **WhatsApp adapter**: `backend/app/whatsapp_adapter.py` contains a Twilio-compatible webhook scaffold and sample signature verification. Configure `TWILIO_AUTH_TOKEN` to enable signature checks.
- **Auth & Migrations**: `backend/app/auth.py` provides a simple JWT helper; `backend/alembic` contains migration placeholders. Replace defaults with secure secrets & real migration scripts before production.
- **Kubernetes**: `k8s/` contains basic deployment manifests for backend and postgres as a starting point.

## Run with streaming (dev)
1. Start compose as before: `docker compose up --build`
2. (Optional) Export OpenAI key: `export OPENAI_API_KEY='sk-...'`
3. Start widget: `cd frontend/widget && npm install && npm start`
4. Click "Stream" in the widget to see server-sent events (SSE) streaming tokens.
