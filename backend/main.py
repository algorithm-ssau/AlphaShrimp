"""FastAPI сервер AlphaShrimp."""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import init_db, get_db, User, Chat, Message
from router.router import route, classify, get_available_models

app = FastAPI(title="AlphaShrimp API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    classify("warmup")



class ChatRequest(BaseModel):
    message: str
    model: str | None = None       # None = автовыбор через роутер
    mode: str = "quality"          # quality / balanced / economy
    chat_id: int | None = None     # None = новый чат

class RouteRequest(BaseModel):
    message: str
    mode: str = "quality"


@app.post("/api/route")
def route_query(req: RouteRequest):
    """Маршрутизировать запрос (без отправки модели)."""
    return route(req.message, mode=req.mode)


@app.get("/api/models")
def list_models():
    """Список доступных моделей."""
    return get_available_models()



@app.post("/api/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    """Отправить сообщение в чат."""

    if req.model:
        chosen_model = req.model
        category = None
    else:
        routing = route(req.message, mode=req.mode)
        chosen_model = routing["best_model"]
        category = routing["category"]

    if req.chat_id:
        chat_obj = db.query(Chat).filter(Chat.id == req.chat_id).first()
        if not chat_obj:
            raise HTTPException(status_code=404, detail="Чат не найден")
    else:
        chat_obj = Chat(title=req.message[:50], user_id=1)
        db.add(chat_obj)
        db.flush()

    user_msg = Message(
        chat_id=chat_obj.id,
        role="user",
        content=req.message,
    )
    db.add(user_msg)

    # Заглушка
    stub_reply = f"[{chosen_model}] Это заглушка. Реальный ответ появится после подключения API."

    assistant_msg = Message(
        chat_id=chat_obj.id,
        role="assistant",
        content=stub_reply,
        model=chosen_model,
        category=category,
    )
    db.add(assistant_msg)
    db.commit()

    return {
        "chat_id": chat_obj.id,
        "model": chosen_model,
        "category": category,
        "reply": stub_reply,
    }


@app.get("/api/chats")
def list_chats(db: Session = Depends(get_db)):
    """Список чатов."""
    chats = db.query(Chat).order_by(Chat.updated_at.desc()).all()
    return [
        {"id": c.id, "title": c.title, "updated_at": str(c.updated_at)}
        for c in chats
    ]


@app.get("/api/chats/{chat_id}/messages")
def get_messages(chat_id: int, db: Session = Depends(get_db)):
    """Сообщения конкретного чата."""
    messages = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at)
        .all()
    )
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "model": m.model,
            "category": m.category,
            "created_at": str(m.created_at),
        }
        for m in messages
    ]
