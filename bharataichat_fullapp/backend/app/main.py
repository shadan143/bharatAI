    import os
    from fastapi import FastAPI, Depends, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    from typing import Optional, List
    import uuid, datetime

    from .db import SessionLocal, engine, Base
    from . import crud, schemas, embeddings, vector_store, llm\nfrom .lang_utils import detect_language, translate_to_english, translate_from_english\nfrom .stream import router as stream_router\nfrom .whatsapp_adapter import router as whatsapp_router

    # create DB tables (for dev)
    Base.metadata.create_all(bind=engine)

    app = FastAPI(title="BharatAI Chat - Full App")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class MessageIn(BaseModel):
        conversation_id: Optional[str]
        text: str
        lang: Optional[str] = "hi"

    @app.post("/v1/messages")
    async def post_message(msg: MessageIn):
        db = SessionLocal()
        try:
            detected = detect_language(msg.text)\n        # translate to English for embeddings/LLM pipeline if needed\n        text_en = translate_to_english(msg.text, detected)\n        conv = crud.get_or_create_conversation(db, msg.conversation_id, detected)
            # store user message
            m = crud.create_message(db, conv.id, "user", msg.text, msg.lang)
            # Basic pipeline: detect if FAQ or RAG
            if any(k in msg.text.lower() for k in ["balance","balanc","बैलेंस","बैलेंस?"]):
                reply = "आपका खाता बैलेंस: ₹12,345.67 (डेमो उत्तर)।"
            else:
                # RAG: embed, search, and craft reply (simple template)
                emb = embeddings.get_embedding(text_en)
                docs = vector_store.search_similar(emb, top_k=3)
                if docs:
                    joined = "\n---\n".join([d['content'] for d in docs])
                    reply = f"मैंने इन दस्तावेज़ों में पाया:\n{joined}\n
(यह उत्तर डेमो है — customize the LLM prompt in backend)"
                else:
                    reply = "नमस्ते — कैसे मदद कर सकता हूँ? / Hello — how can I help?"
            bot = crud.create_message(db, conv.id, "bot", reply, msg.lang)
            return {"conversation_id": conv.id, "reply": {"id": bot.id, "text": reply}}
        finally:
            db.close()

    @app.post("/v1/consents")
    async def post_consent(item: schemas.ConsentCreate):
        db = SessionLocal()
        try:
            c = crud.create_consent(db, item.user_id, item.purpose, item.lang, item.consent)
            return {"consent_id": c.id}
        finally:
            db.close()

    @app.get("/v1/health")
    def health():
        return {"status":"ok", "time": datetime.datetime.utcnow().isoformat()}
\n\n# Streaming endpoint router\napp.include_router(stream_router, prefix='')\n\n# WhatsApp adapter router\napp.include_router(whatsapp_router, prefix='/api')\n