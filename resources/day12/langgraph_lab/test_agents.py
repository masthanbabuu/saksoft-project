"""Tests for both versions of the agent. No network, no real model (Playbook TST-05).

Run:  python -m pytest -q   (from this folder)
"""

import pytest
from langgraph.errors import GraphRecursionError

import tools
from agent_graph import build_graph, resume, start
from agent_plain import run_agent
from llm import ScriptedChat, final_answer, tool_call


@pytest.fixture(autouse=True)
def clean_tickets():
    tools.CREATED_TICKETS.clear()


# ----------------------------------------------------------------------------- plain version
def test_plain_read_only_tool_then_answer():
    model = ScriptedChat([tool_call("ticket_lookup", {"ticket_id": "T-100"}), final_answer("It is open.")])
    result = run_agent("Status of T-100?", model, approve=lambda preview: False)
    assert result.answer == "It is open."
    assert result.stopped_by == "answer"
    assert result.audit == ["ticket_lookup: ran with {'ticket_id': 'T-100'}"]


def test_plain_step_limit_stops_a_runaway_loop():
    model = ScriptedChat([tool_call("ticket_lookup", {"ticket_id": "T-100"})])  # asks for a tool forever
    result = run_agent("loop", model, approve=lambda p: True, max_steps=3)
    assert result.stopped_by == "step_limit"
    assert result.steps == 3


def test_plain_side_effect_needs_approval_and_denial_blocks_it():
    model = ScriptedChat([tool_call("create_ticket", {"title": "Broken chair"}), final_answer("Not done.")])
    run_agent("Create a ticket", model, approve=lambda preview: False)
    assert tools.CREATED_TICKETS == []  # nothing was created


def test_plain_approved_side_effect_runs_once():
    model = ScriptedChat([tool_call("create_ticket", {"title": "Broken chair"}), final_answer("Done.")])
    previews = []
    run_agent("Create a ticket", model, approve=lambda preview: previews.append(preview) or True)
    assert len(tools.CREATED_TICKETS) == 1
    assert "create_ticket" in previews[0]  # the human saw a dry-run preview


def test_plain_bad_arguments_go_back_to_the_model_not_crash():
    model = ScriptedChat([tool_call("ticket_lookup", {}), final_answer("Could not.")])
    result = run_agent("x", model, approve=lambda p: True)
    assert result.answer == "Could not."
    assert "invalid arguments" in result.audit[0]


# ----------------------------------------------------------------------------- LangGraph version
def test_graph_read_only_tool_then_answer():
    model = ScriptedChat(
        [
            tool_call("convert_units", {"value": 10, "from_unit": "km", "to_unit": "mi"}),
            final_answer("About 6.2 miles."),
        ]
    )
    out = start(build_graph(model), "10 km in miles?", "t1")
    assert out["status"] == "done"
    assert out["answer"] == "About 6.2 miles."


def test_graph_recursion_limit_stops_a_runaway_loop():
    model = ScriptedChat([tool_call("ticket_lookup", {"ticket_id": "T-100"})])  # never answers
    with pytest.raises(GraphRecursionError):
        start(build_graph(model), "loop", "t2", max_steps=5)


def test_graph_side_effect_pauses_for_approval_and_nothing_runs_yet():
    model = ScriptedChat([tool_call("create_ticket", {"title": "Broken chair"}), final_answer("Created.")])
    graph = build_graph(model)
    out = start(graph, "Create a ticket", "t3")
    assert out["status"] == "needs_approval"
    assert out["request"]["tool"] == "create_ticket"
    assert tools.CREATED_TICKETS == []


def test_graph_resume_with_yes_runs_the_side_effect_once():
    model = ScriptedChat([tool_call("create_ticket", {"title": "Broken chair"}), final_answer("Created.")])
    graph = build_graph(model)
    start(graph, "Create a ticket", "t4")
    out = resume(graph, "t4", approved=True)
    assert out["status"] == "done"
    assert len(tools.CREATED_TICKETS) == 1


def test_graph_resume_with_no_blocks_the_side_effect():
    model = ScriptedChat(
        [tool_call("create_ticket", {"title": "Broken chair"}), final_answer("Not created.")]
    )
    graph = build_graph(model)
    start(graph, "Create a ticket", "t5")
    out = resume(graph, "t5", approved=False)
    assert out["status"] == "done"
    assert tools.CREATED_TICKETS == []
    assert "denied by human" in out["audit"][0]


def test_list_open_tickets_tool_is_read_only():
    tool = tools.build_tools()["list_open_tickets"]

    assert tool.needs_approval is False

    result = tool.run({})

    assert "T-100" in result
    assert "Printer jams on floor 2" in result
    assert "T-101" not in result
