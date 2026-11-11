# syntax=docker/dockerfile:1
# Container for the LangGraph agent service. Replace the <PLACEHOLDERS> first
# (see ../../PLACEHOLDERS.md): <PYTHON_IMAGE_TAG>, <PYTHON_IMAGE_DIGEST>, <UV_IMAGE_TAG>.
#
# Build:  docker build -t langgraph-agent:<TAG> .
# Run:    docker run --rm -p 127.0.0.1:8100:8000 --env-file agent.env langgraph-agent:<TAG>
# (agent.env holds LLM_BASE_URL, LLM_MODEL and LLM_API_KEY. Never commit it.)
FROM python:<PYTHON_IMAGE_TAG>@sha256:<PYTHON_IMAGE_DIGEST>

COPY --from=ghcr.io/astral-sh/uv:<UV_IMAGE_TAG> /uv /bin/uv

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
