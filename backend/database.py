"""
Таблицы:
- User: пользователи (email + хеш пароля)
- Chat: диалоги (привязаны к пользователю)
- Message: сообщения в диалогах (роль + текст + модель + категория)
"""

from datetime import datetime, timezone
from sqlalchemy import (
    create_engine, Column, String, Text, DateTime, ForeignKey, Integer
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = "sqlite:///./alphashrimp.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, default="Новый чат")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    role = Column(String, nullable=False)       # "user"/"assistant"
    content = Column(Text, nullable=False)
    model = Column(String, nullable=True)       # None для user
    category = Column(String, nullable=True)    # None для user
    created_at = Column(DateTime, default=utcnow)

    chat = relationship("Chat", back_populates="messages")


def init_db():
    """Создать все таблицы если их нет."""
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
