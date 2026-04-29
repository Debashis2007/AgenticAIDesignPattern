"""FastAPI backend for chat UI integration."""

from __future__ import annotations

from contextlib import asynccontextmanager
import json
import os
from pathlib import Path
from typing import Iterator

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

from .engine import fallback_chat_response
from .knowledge import VISA_TIMELINES, COMMON_ISSUES, VISA_SELECTION_GUIDE
from .llm import try_llm_prompt
from .memory import append_message, init_db, load_messages

# Load environment variables from .env file
_env_file = Path(__file__).parent.parent.parent / ".env"
if _env_file.exists():
    load_dotenv(_env_file)


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    source: str
    history: list[dict[str, str]]


def _auth_enabled() -> bool:
    return os.getenv("API_AUTH_ENABLED", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not _auth_enabled():
        return

    expected = os.getenv("API_AUTH_KEY", "")
    if not expected or x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


def _build_reply(session_id: str, message: str) -> tuple[str, str, list[dict[str, str]]]:
    prior_messages = load_messages(session_id)
    append_message(session_id, "user", message)

    context_block = "\n".join(f"{m['role']}: {m['content']}" for m in prior_messages[-8:])
    
    system_prompt = """You are an expert immigration and career planning assistant with deep knowledge of:
- U.S. visa categories (H1B, L1, EB green cards, F-1, O-1, NIW, etc.)
- Processing timelines and current USCIS backlogs
- Country-specific consulate requirements
- Common visa application pitfalls and solutions
- Career transition strategies aligned with immigration goals

Your approach:
1. Ask clarifying questions about current visa status, goals, and timeline
2. Provide specific, actionable next steps with realistic timelines
3. Flag potential risks or missing requirements
4. Offer alternative pathways when primary options are blocked
5. Use markdown formatting with headers, lists, and emphasis

IMPORTANT: You do not provide legal advice. Always recommend consulting an immigration attorney for specific cases.
Keep responses concise and practical. Use timelines in months/years. Include confidence levels in predictions."""

    # Add relevant knowledge from knowledge base
    knowledge_context = "\n\nREFERENCE KNOWLEDGE (use to enhance response):"
    if any(word in message.lower() for word in ["h1b", "l1", "green card", "visa", "timeline"]):
        knowledge_context += "\n\nCommon Visa Categories:"
        for visa, info in list(VISA_TIMELINES.items())[:3]:
            knowledge_context += f"\n- {info['name']}: {info['processing_time']} processing"
    
    if any(word in message.lower() for word in ["conflict", "confused", "different", "advice"]):
        knowledge_context += "\n\nCommon Conflicting Info Issues:"
        for issue, details in list(COMMON_ISSUES.items())[:2]:
            knowledge_context += f"\n- {issue}: {details.get('issue', '')}"

    prompt = (
        f"{system_prompt}"
        f"{knowledge_context}\n\n"
        f"Conversation context:\n{context_block}\n\n"
        f"Latest user message: {message}\n\n"
        "Provide a helpful, structured response with clear next steps."
    )

    llm_reply = try_llm_prompt(prompt)
    if llm_reply:
        reply = llm_reply
        source = "llm"
    else:
        reply = fallback_chat_response(message)
        source = "rule_based"

    append_message(session_id, "assistant", reply)
    history = load_messages(session_id)
    return reply, source, history


def _chunk_text(text: str, chunk_size: int = 30) -> Iterator[str]:
    for i in range(0, len(text), chunk_size):
        yield text[i : i + chunk_size]


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Immigration Chatbot API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, _: None = Depends(verify_api_key)) -> ChatResponse:
    reply, source, history = _build_reply(
        session_id=payload.session_id,
        message=payload.message,
    )

    return ChatResponse(
        session_id=payload.session_id,
        reply=reply,
        source=source,
        history=history,
    )


@app.post("/api/chat/stream")
def chat_stream(payload: ChatRequest, _: None = Depends(verify_api_key)) -> StreamingResponse:
    reply, source, history = _build_reply(
        session_id=payload.session_id,
        message=payload.message,
    )

    def event_gen() -> Iterator[str]:
        # stream chunks as SSE
        for chunk in _chunk_text(reply):
            yield f"event: token\ndata: {json.dumps({'chunk': chunk})}\n\n"

        final_event = {
            "session_id": payload.session_id,
            "reply": reply,
            "source": source,
            "history": history,
        }
        yield f"event: done\ndata: {json.dumps(final_event)}\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream")


def run() -> None:
    uvicorn.run("immigration_chatbot.api:app", host="0.0.0.0", port=8000, reload=False)
