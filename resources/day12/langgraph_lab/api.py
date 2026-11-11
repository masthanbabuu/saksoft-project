"""YOUR TASK, part 3 (day 18): host the graph behind YOUR OWN FastAPI app.

WHY NOT LangGraph's own server?  Hosting the vendor's server yourself needs a licence key (an
Enterprise add-on, see the official self-hosting page). A normal FastAPI app that calls your
graph is free, under your control, and follows the same Docker, health check and logging rules
as every other service (Playbook ORCH-07).

Endpoints to build (the tests in test_api.py describe them):
  GET  /health                                            -> {"status": "ok"}
  POST /chat     {"question": "..."}                      -> {"thread_id": ..., "status": "done" | "needs_approval", ...}
  POST /approve  {"thread_id": "...", "approved": true}   -> carries on after the human's decision

Hints:
  * One new thread ID (a UUID string) for every conversation; return it so the caller can approve later.
  * Validate input with Pydantic (a question is 1 to 2000 characters).
  * Build the graph once, on first use, from `get_model()` so tests can swap in a fake model.
  * An unknown thread ID on /approve should give a 404 with a plain message, not a crash.
"""

from fastapi import FastAPI

from llm import ChatModel, OpenAICompatibleChat

app = FastAPI(title="LangGraph agent service")

_graph = None  # built on first use (tests reset it)


def get_model() -> ChatModel:
    """Create the real model client from the environment. Tests replace this function."""
    return OpenAICompatibleChat()


def get_graph():
    """Build the graph once and reuse it."""
    raise NotImplementedError("Build the graph from get_model() on first use and keep it in _graph.")


# TODO: add the request models, then the three endpoints described above.
