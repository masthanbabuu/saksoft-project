
"""YOUR TASK, part 1 (day 12): build the agent loop in plain Python."""

import time
from collections.abc import Callable
from dataclasses import dataclass, field

from llm import ChatModel
from tools import Tool, build_tools, validate_arguments


@dataclass
class AgentResult:
    answer: str
    steps: int
    stopped_by: str = "answer"
    audit: list[str] = field(default_factory=list)


def run_agent(
    question: str,
    model: ChatModel,
    approve: Callable[[str], bool],
    tools: dict[str, Tool] | None = None,
    max_steps: int = 6,
    max_seconds: float = 30.0,
) -> AgentResult:
    available_tools = tools if tools is not None else build_tools()
    messages = [{"role": "user", "content": question}]
    audit = []
    start_time = time.monotonic()

    for step in range(1, max_steps + 1):
        if time.monotonic() - start_time >= max_seconds:
            return AgentResult(
                answer="Stopped because the time limit was reached.",
                steps=step - 1,
                stopped_by="time_limit",
                audit=audit,
            )

        reply = model.chat(
            messages,
            [tool.schema() for tool in available_tools.values()],
        )
        messages.append(reply)

        tool_calls = reply.get("tool_calls", [])

        if not tool_calls:
            return AgentResult(
                answer=reply.get("content", ""),
                steps=step,
                stopped_by="answer",
                audit=audit,
            )

        for call in tool_calls:
            name = call["name"]
            arguments = call.get("arguments", {})
            call_id = call["id"]
            tool = available_tools.get(name)

            if tool is None:
                result = f"Unknown tool: {name}"
                audit.append(f"{name}: unknown tool")
            else:
                problem = validate_arguments(tool, arguments)

                if problem:
                    result = f"Invalid arguments: {problem}"
                    audit.append(f"{name}: invalid arguments - {problem}")
                elif tool.needs_approval and not approve(tool.preview(arguments)):
                    result = "Action denied by human."
                    audit.append(f"{name}: denied by human")
                else:
                    try:
                        result = tool.run(arguments)
                        audit.append(f"{name}: ran with {arguments}")
                    except Exception as exc:
                        result = f"Tool error: {exc}"
                        audit.append(f"{name}: error - {exc}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": name,
                    "content": str(result),
                }
            )

    return AgentResult(
        answer="Stopped because the step limit was reached.",
        steps=max_steps,
        stopped_by="step_limit",
        audit=audit,
    )
