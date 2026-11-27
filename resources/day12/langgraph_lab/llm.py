"""A tiny, provider-agnostic chat client, plus a fake model for tests.

WHY HAVE OUR OWN CLIENT?  So the agent code does not depend on one provider (Playbook AI-01).
Anything that speaks the common "chat completions" format works: change three settings
(base URL, model, key) and nothing else.

MESSAGE FORMAT used everywhere in this folder (plain dictionaries, easy to read and test):
    {"role": "user" | "assistant" | "tool", "content": "text",
     "tool_calls": [{"id": "1", "name": "tool_name", "arguments": {...}}]}   # assistant only
    {"role": "tool", "tool_call_id": "1", "name": "tool_name", "content": "result text"}
"""

import json
import os
from collections.abc import Sequence
from typing import Protocol

import httpx


class ChatModel(Protocol):
    """Anything with a `chat` method like this can drive the agent."""

    def chat(self, messages: Sequence[dict], tools: Sequence[dict]) -> dict: ...


class OpenAICompatibleChat:
    """Calls any provider that offers the common /chat/completions endpoint.

    Settings come from the environment (never hard-code keys, Playbook CFG-03):
      LLM_BASE_URL  e.g. the base URL from the provider's documentation
      LLM_MODEL     a model name from the provider's current list
      LLM_API_KEY   your personal key
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = (base_url or os.environ["LLM_BASE_URL"]).rstrip("/")
        self.model = model or os.environ["LLM_MODEL"]
        self.api_key = api_key or os.environ["LLM_API_KEY"]
        self.timeout = timeout  # every outbound call has a timeout (PY-12)

    def chat(self, messages: Sequence[dict], tools: Sequence[dict]) -> dict:
        payload = {
            "model": self.model,
            "messages": [_to_wire(m) for m in messages],
            "tools": [{"type": "function", "function": t} for t in tools],
        }
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]
        calls = [
            {
                "id": c["id"],
                "name": c["function"]["name"],
                "arguments": json.loads(c["function"]["arguments"] or "{}"),
            }
            for c in message.get("tool_calls") or []
        ]
        return {"role": "assistant", "content": message.get("content") or "", "tool_calls": calls}


def _to_wire(message: dict) -> dict:
    """Convert our simple message into the provider's format."""
    if message["role"] == "assistant" and message.get("tool_calls"):
        return {
            "role": "assistant",
            "content": message.get("content") or None,
            "tool_calls": [
                {
                    "id": c["id"],
                    "type": "function",
                    "function": {"name": c["name"], "arguments": json.dumps(c["arguments"])},
                }
                for c in message["tool_calls"]
            ],
        }
    if message["role"] == "tool":
        return {"role": "tool", "tool_call_id": message["tool_call_id"], "content": message["content"]}
    return {"role": message["role"], "content": message["content"]}


class ScriptedChat:
    """A fake model for tests: it replies with the answers you give it, in order.

    Tests must never call a real model (Playbook TST-05): they would be slow, flaky and cost money.
    """

    def __init__(self, replies: list[dict]) -> None:
        self.replies = list(replies)
        self.calls = 0

    def chat(self, messages: Sequence[dict], tools: Sequence[dict]) -> dict:
        self.calls += 1
        # When the script runs out, keep repeating the last reply (useful to test loop limits).
        reply = self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]
        return dict(reply)


def tool_call(name: str, arguments: dict, call_id: str = "1") -> dict:
    """Helper that builds an assistant message asking for one tool."""
    return {
        "role": "assistant",
        "content": "",
        "tool_calls": [{"id": call_id, "name": name, "arguments": arguments}],
    }


def final_answer(text: str) -> dict:
    """Helper that builds a plain assistant answer."""
    return {"role": "assistant", "content": text, "tool_calls": []}
