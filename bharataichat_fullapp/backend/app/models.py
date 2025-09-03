from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid, datetime

from .db import Base

def gen_uuid():
    return str(uuid.uuid4())

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String, primary_key=True, default=gen_uuid)
    lang = Column(String, default="hi")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=gen_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    role = Column(String)
    lang = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Consent(Base):
    __tablename__ = "consents"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, index=True)
    purpose = Column(String)
    lang = Column(String)
    consent = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
