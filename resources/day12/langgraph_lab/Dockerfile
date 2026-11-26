# syntax=docker/dockerfile:1
# Container for the LangGraph agent service. Replace the <PLACEHOLDERS> first
# (see ../../PLACEHOLDERS.md): 3.14.4-slim, 2ca02f32b4d9d893863367ce07ec1972819f476dd38d8612f2a9cb6a41cbb727, 0.13.7.
#
# Build:  docker build -t langgraph-agent:<TAG> .
# Run:    docker run --rm -p 127.0.0.1:8100:8000 --env-file agent.env langgraph-agent:<TAG>
# (agent.env holds LLM_BASE_URL, LLM_MODEL and LLM_API_KEY. Never commit it.)
FROM python:3.14.4-slim@sha256:2ca02f32b4d9d893863367ce07ec1972819f476dd38d8612f2a9cb6a41cbb727

COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /bin/uv

RUN useradd --create-home --uid 1000 --shell /bin/sh appuser
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY llm.py tools.py agent_plain.py agent_graph.py api.py ./
ENV PATH="/app/.venv/bin:$PATH"
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=4)"
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
