# Task: the same agent twice, then host it (days 12 and 18)

**You build this.** The folder gives you the tools, a model client, a fake model for tests, and 13
tests that fail until your code is right. Work test by test.

## Files
| File | Whose job |
|---|---|
| `llm.py` | Given. A model client for any provider with the common chat endpoint, plus `ScriptedChat`, a fake model for tests |
| `tools.py` | Given. Four tools: three read-only or pure, one (`create_ticket`) that changes data and needs a human yes |
| `agent_plain.py` | **You write it** (part 1): the agent loop in plain Python |
| `agent_graph.py` | **You write it** (part 2): the same agent as a LangGraph graph |
| `api.py` | **You write it** (part 3): host the graph behind your own FastAPI app |
| `test_agents.py`, `test_api.py` | The target. Read each test before you write the code for it |
| `trace_demo.py` | Run it when everything passes, with LangSmith tracing on |
| `Dockerfile` | Replace the placeholders, then host the service (see `../../docker_hosting/HOSTING_GUIDE.md`) |

## Steps
1. `uv sync`, then `uv run pytest -q`. All 13 fail. Good: that is your to-do list.
2. **Part 1 (about 2 hours).** Make the five `plain` tests pass in `agent_plain.py`. Rules to keep: a step limit and a time limit, tool errors go back to the model as text, anything that changes data needs a human yes, every call is written to the audit list.
3. **Part 2 (about 2 hours).** Make the five `graph` tests pass in `agent_graph.py`. Read the three official pages named at the top of that file first. Set `recursion_limit` on every call. Put the approval in an `interrupt`.
4. Switch on LangSmith tracing (see `../langsmith/README.md`) and run `trace_demo.py`. Find the tool call in the trace.
5. **Part 3 (day 18).** Make the three API tests pass in `api.py`, then put the service in a container.
6. Add a **fifth tool** of your own (for example "list open tickets") with its test first. Does it need approval? Why or why not? Write two sentences.

## Rules that apply (Playbook ORCH-04 to ORCH-07, AG-02 to AG-05)
Limits on every call. Side effects behind an approval. No secrets in state. Host the graph behind your own
FastAPI image.

## Stuck?
Ask your mentor a clear question after 20 minutes (VIBE-16). If AI helps, it explains; you type (week 1) or
it drafts under the seven rules (from week 2), and every use goes in your AI-assist log.
