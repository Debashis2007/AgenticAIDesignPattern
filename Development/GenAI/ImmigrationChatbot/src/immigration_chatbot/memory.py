"""Simple persistent memory layer for chat history.

Default storage is SQLite for local development.
`DATABASE_URL` can be switched to Postgres without API changes.
Set `MEMORY_BACKEND=firebase` to use Firestore.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import os
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    """Base SQLAlchemy model class."""


class ChatMessage(Base):
    """Persisted chat message."""

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(100), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(String(4000))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )


class MemoryBackend(ABC):
    @abstractmethod
    def init(self) -> None:
        pass

    @abstractmethod
    def append_message(self, session_id: str, role: str, content: str) -> None:
        pass

    @abstractmethod
    def load_messages(self, session_id: str, limit: int = 12) -> list[dict[str, str]]:
        pass


def _normalize_db_url(db_url: str) -> str:
    if db_url.startswith("postgres://"):
        return db_url.replace("postgres://", "postgresql+psycopg://", 1)
    if db_url.startswith("postgresql://"):
        return db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return db_url


def get_database_url() -> str:
    return _normalize_db_url(os.getenv("DATABASE_URL", "sqlite:///./chatbot.db"))


def get_engine():
    db_url = get_database_url()
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    return create_engine(db_url, future=True, connect_args=connect_args)


def get_session_factory():
    return sessionmaker(bind=get_engine(), class_=Session, expire_on_commit=False)


class SqlMemoryBackend(MemoryBackend):
    def init(self) -> None:
        Base.metadata.create_all(get_engine())

    def append_message(self, session_id: str, role: str, content: str) -> None:
        session_factory = get_session_factory()
        with session_factory() as db:
            db.add(ChatMessage(session_id=session_id, role=role, content=content))
            db.commit()

    def load_messages(self, session_id: str, limit: int = 12) -> list[dict[str, str]]:
        session_factory = get_session_factory()
        with session_factory() as db:
            stmt = (
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
                .limit(limit)
            )
            rows = list(db.scalars(stmt))

        return [{"role": r.role, "content": r.content} for r in rows]


class FirebaseMemoryBackend(MemoryBackend):
    def __init__(self) -> None:
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client

        try:
            from google.cloud import firestore  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Firebase backend requested but google-cloud-firestore is not installed"
            ) from exc

        project_id = os.getenv("FIREBASE_PROJECT_ID", "")
        if project_id:
            self._client = firestore.Client(project=project_id)
        else:
            self._client = firestore.Client()
        return self._client

    def init(self) -> None:
        # Firestore is schema-less; ensure client can be created.
        self._get_client()

    def append_message(self, session_id: str, role: str, content: str) -> None:
        client = self._get_client()
        collection = os.getenv("FIREBASE_COLLECTION", "chat_messages")
        client.collection(collection).add(
            {
                "session_id": session_id,
                "role": role,
                "content": content,
                "created_at": datetime.now(UTC),
            }
        )

    def load_messages(self, session_id: str, limit: int = 12) -> list[dict[str, str]]:
        client = self._get_client()
        collection = os.getenv("FIREBASE_COLLECTION", "chat_messages")
        query = (
            client.collection(collection)
            .where("session_id", "==", session_id)
            .order_by("created_at")
            .limit(limit)
        )
        docs = list(query.stream())
        messages: list[dict[str, str]] = []
        for doc in docs:
            data: dict[str, Any] = doc.to_dict() or {}
            messages.append(
                {
                    "role": str(data.get("role", "assistant")),
                    "content": str(data.get("content", "")),
                }
            )
        return messages


_backend_instance: MemoryBackend | None = None


def _get_backend() -> MemoryBackend:
    global _backend_instance
    if _backend_instance is not None:
        return _backend_instance

    backend_name = os.getenv("MEMORY_BACKEND", "sql").strip().lower()
    if backend_name == "firebase":
        _backend_instance = FirebaseMemoryBackend()
    else:
        _backend_instance = SqlMemoryBackend()

    return _backend_instance


def reset_backend_cache() -> None:
    """Test helper: force backend re-evaluation after env changes."""
    global _backend_instance
    _backend_instance = None


def init_db() -> None:
    _get_backend().init()


def append_message(session_id: str, role: str, content: str) -> None:
    _get_backend().append_message(session_id=session_id, role=role, content=content)


def load_messages(session_id: str, limit: int = 12) -> list[dict[str, str]]:
    return _get_backend().load_messages(session_id=session_id, limit=limit)
