"""FastAPI service for the LangGraph agent."""

from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agent_graph import build_graph, start, resume
from llm import ChatModel, OpenAICompatibleChat

app = FastAPI(title="LangGraph agent service")

_graph = None


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class ApprovalRequest(BaseModel):
    thread_id: str
    approved: bool


def get_model() -> ChatModel:
    return OpenAICompatibleChat()


def get_graph() -> Any:
    global _graph
    if _graph is None:
        _graph = build_graph(get_model())
    return _graph


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, Any]:
    thread_id = str(uuid4())
    result = start(get_graph(), request.question, thread_id)
    return {"thread_id": thread_id, **result}


@app.post("/approve")
def approve(request: ApprovalRequest) -> dict[str, Any]:
    graph = get_graph()
    config = {"configurable": {"thread_id": request.thread_id}}
    state = graph.get_state(config)

    if not state.values:
        raise HTTPException(404, "Unknown thread ID")

    if not any(task.interrupts for task in state.tasks):
        raise HTTPException(409, "No pending approval")

    result = resume(graph, request.thread_id, request.approved)
    return {"thread_id": request.thread_id, **result}
