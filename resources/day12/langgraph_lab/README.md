# LangGraph lab

Start with `TASK.md`. This folder is a **task**, not a finished app: trainees write the agent
(plain Python, then LangGraph, then a FastAPI wrapper) so that the 13 tests pass.

## What LangGraph is (and is not)
- **Is:** a free, open-source (MIT) Python library to build agents as graphs, with saved state, pauses
  for humans and streaming. Docs: <https://docs.langchain.com/oss/python/langgraph/overview>
- **Is not:** a model, and not a monitoring tool. To watch what an agent did, use LangSmith (hosted,
  free Developer plan) or an open-source tracer: see `../langsmith/` and `../jaeger/`.
- **Hosting:** the vendor's self-hosted server is an Enterprise add-on that needs a licence key (<https://docs.langchain.com/langsmith/self-hosted>), so we host the graph behind our own FastAPI app.

## For mentors
A finished version is in `../../mentor_reference/langgraph_app_solution/` (13 tests pass). Hand it out only after the gate.
