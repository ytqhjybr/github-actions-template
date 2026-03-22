from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    role = Column(String)  # 'user' или 'assistant'
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CommercialProposal(Base):
    __tablename__ = "commercial_proposals"
    id = Column(Integer, primary_key=True, index=True)
    client_inn = Column(String, index=True)
    file_path = Column(String)  # путь к сгенерированному DOC
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    version = Column(Integer, default=1)