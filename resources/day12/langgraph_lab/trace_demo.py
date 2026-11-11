"""Day 12 and day 33: see your agent in LangSmith without paying for a model.

The demo runs the agent with a SCRIPTED fake model, so it needs no model key and costs nothing.
If LangSmith tracing is switched on, one trace appears in your LangSmith project.

STEPS
  1. Create a free LangSmith account (the free Developer plan, see starter_kit/orchestration/langsmith/README.md).
  2. Create an API key in the LangSmith settings.
  3. Set two environment variables in the terminal where you run this file:
        LANGSMITH_TRACING=true
        LANGSMITH_API_KEY=<your key>          (never write the key into a file)
     Linux, macOS, Git Bash:   export LANGSMITH_TRACING=true
     Windows PowerShell:       $env:LANGSMITH_TRACING="true"
  4. Run:  python trace_demo.py
  5. Open LangSmith, open your project, and click the newest trace. You will see each step:
     the model call, the tool call, the model call again.

DATA RULE: only synthetic text goes to a hosted tracing service (Playbook OBS-13).
"""

import os

from agent_graph import build_graph, start
from llm import ScriptedChat, final_answer, tool_call


def main() -> None:
    model = ScriptedChat(
        [
            tool_call("search_docs", {"query": "priority tickets"}),
            final_answer("Priority 1 tickets are answered within 15 minutes (policy-1)."),
        ]
    )
    result = start(build_graph(model), "How fast are priority 1 tickets answered?", thread_id="trace-demo")
    print(result["answer"])
    tracing = os.environ.get("LANGSMITH_TRACING", "false").lower() == "true"
    print(
        "LangSmith tracing is",
        "ON: look for the trace in your project."
        if tracing
        else "OFF: set LANGSMITH_TRACING=true to see a trace.",
    )


if __name__ == "__main__":
    main()
