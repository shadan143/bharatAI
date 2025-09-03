from . import models
from .db import SessionLocal
from sqlalchemy.orm import Session

def get_or_create_conversation(db: Session, conv_id, lang):
    if conv_id:
        c = db.query(models.Conversation).filter(models.Conversation.id==conv_id).first()
        if c:
            return c
    c = models.Conversation(lang=lang)
    db.add(c); db.commit(); db.refresh(c)
    return c

def create_message(db: Session, conv_id, role, content, lang):
    m = models.Message(conversation_id=conv_id, role=role, content=content, lang=lang)
    db.add(m); db.commit(); db.refresh(m)
    return m

def create_consent(db: Session, user_id, purpose, lang, consent):
    c = models.Consent(user_id=user_id, purpose=purpose, lang=lang, consent=str(consent))
    db.add(c); db.commit(); db.refresh(c)
    return c
