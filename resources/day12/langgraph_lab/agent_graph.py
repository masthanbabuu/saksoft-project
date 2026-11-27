"""LangGraph implementation of the Day 12 agent."""

import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from llm import ChatModel
from tools import Tool, build_tools, validate_arguments


class AgentState(TypedDict):
    """Conversation state and audit trail."""

    messages: Annotated[list[dict], operator.add]
    audit: Annotated[list[str], operator.add]
    pending_calls: list[dict]


def build_graph(model: ChatModel, tools: dict[str, Tool] | None = None):
    """Build and compile the agent graph."""

    available_tools = tools if tools is not None else build_tools()

    def llm_call(state: AgentState) -> dict:
        reply = model.chat(
            state["messages"],
            [tool.schema() for tool in available_tools.values()],
        )
        return {
            "messages": [reply],
            "pending_calls": reply.get("tool_calls", []),
        }

    def tool_node(state: AgentState) -> dict:
        call = state["pending_calls"][0]
        remaining_calls = state["pending_calls"][1:]

        name = call["name"]
        arguments = call.get("arguments", {})
        call_id = call["id"]
        tool = available_tools.get(name)

        if tool is None:
            result = f"Unknown tool: {name}"
            audit_entry = f"{name}: unknown tool"
        else:
            problem = validate_arguments(tool, arguments)

            if problem:
                result = f"Invalid arguments: {problem}"
                audit_entry = f"{name}: invalid arguments - {problem}"
            else:
                approved = True

                if tool.needs_approval:
                    approved = interrupt(
                        {
                            "tool": name,
                            "arguments": arguments,
                            "preview": tool.preview(arguments),
                        }
                    )

                if not approved:
                    result = "Action denied by human."
                    audit_entry = f"{name}: denied by human"
                else:
                    try:
                        result = tool.run(arguments)
                        audit_entry = f"{name}: ran with {arguments}"
                    except Exception as exc:  # noqa: BLE001 - return tool failures to the model
                        result = f"Tool error: {exc}"
                        audit_entry = f"{name}: error - {exc}"

        return {
            "messages": [
                {
                    "role": "tool",
                    "tool_call_id": call_id,
                    "name": name,
                    "content": str(result),
                }
            ],
            "audit": [audit_entry],
            "pending_calls": remaining_calls,
        }

    def should_continue(state: AgentState) -> str:
        return "tool_node" if state["pending_calls"] else END

    def after_tool(state: AgentState) -> str:
        return "tool_node" if state["pending_calls"] else "llm_call"

    builder = StateGraph(AgentState)
    builder.add_node("llm_call", llm_call)
    builder.add_node("tool_node", tool_node)

    builder.add_edge(START, "llm_call")
    builder.add_conditional_edges("llm_call", should_continue)
    builder.add_conditional_edges("tool_node", after_tool)

    return builder.compile(checkpointer=InMemorySaver())


def _result_dict(result: dict) -> dict:
    """Convert a graph result into the public response format."""

    interruptions = result.get("__interrupt__")

    if interruptions:
        return {
            "status": "needs_approval",
            "request": interruptions[0].value,
        }

    messages = result.get("messages", [])
    answer = messages[-1].get("content", "") if messages else ""

    return {
        "status": "done",
        "answer": answer,
        "audit": result.get("audit", []),
    }


def start(graph, question: str, thread_id: str, max_steps: int = 10) -> dict:
    """Start an agent run, pausing if human approval is needed."""

    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": max_steps,
    }

    result = graph.invoke(
        {
            "messages": [{"role": "user", "content": question}],
            "audit": [],
            "pending_calls": [],
        },
        config=config,
    )

    return _result_dict(result)


def resume(graph, thread_id: str, approved: bool, max_steps: int = 10) -> dict:
    """Resume a paused run with the human's approval decision."""

    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": max_steps,
    }

    result = graph.invoke(
        Command(resume=approved),
        config=config,
    )

    return _result_dict(result)
