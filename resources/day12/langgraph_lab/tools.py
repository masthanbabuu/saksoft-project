"""The tools an agent may call.

LEAST AGENCY (Playbook AG-02, AG-03): give the agent no more power than the task needs.
  * three tools only read or compute, so they run on their own
  * one tool changes something (`create_ticket`), so it is marked `needs_approval`
    and a human must say yes before it runs
Each tool has a name, a description and a JSON schema for its arguments. The model sees only
the schema; WE validate the arguments again before running anything (never trust model output,
Playbook AI-07).
"""

from collections.abc import Callable
from dataclasses import dataclass, field

# A tiny in-memory "ticket system" so the lab needs no external service.
TICKETS = {
    "T-100": {"title": "Printer jams on floor 2", "status": "open"},
    "T-101": {"title": "Cannot reset password", "status": "closed"},
}
CREATED_TICKETS: list[dict] = []  # filled only by create_ticket (the side effect)

DOCS = [
    {"source": "policy-1", "text": "Priority 1 tickets are answered within 15 minutes."},
    {"source": "policy-2", "text": "A loan laptop may be kept for 10 working days."},
]


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    parameters: dict  # JSON schema of the arguments
    run: Callable[[dict], str]
    needs_approval: bool = False
    required: tuple[str, ...] = field(default_factory=tuple)

    def schema(self) -> dict:
        """What we show to the model."""
        return {"name": self.name, "description": self.description, "parameters": self.parameters}

    def preview(self, arguments: dict) -> str:
        """A plain dry-run text for the human who must approve (AG-03)."""
        return f"Would run {self.name} with {arguments}"


def _ticket_lookup(args: dict) -> str:
    ticket = TICKETS.get(args["ticket_id"])
    return f"{args['ticket_id']}: {ticket['title']} ({ticket['status']})" if ticket else "No such ticket."


def _search_docs(args: dict) -> str:
    words = {w.lower() for w in args["query"].split()}
    hits = [d for d in DOCS if words & {w.strip(".,").lower() for w in d["text"].split()}]
    return "\n".join(f"[{d['source']}] {d['text']}" for d in hits) or "No matching documents."


def _convert_units(args: dict) -> str:
    factors = {("km", "mi"): 0.621371, ("mi", "km"): 1.609344, ("kg", "lb"): 2.204623, ("lb", "kg"): 0.453592}
    key = (args["from_unit"], args["to_unit"])
    if key not in factors:
        return "Unsupported conversion."
    return f"{args['value']} {key[0]} = {args['value'] * factors[key]:.3f} {key[1]}"


def _list_open_tickets(args: dict) -> str:
    open_tickets = [
        f"{ticket_id}: {ticket['title']}"
        for ticket_id, ticket in TICKETS.items()
        if ticket["status"] == "open"
    ]
    return "\\n".join(open_tickets) or "No open tickets."


def _create_ticket(args: dict) -> str:
    ticket = {"id": f"T-{200 + len(CREATED_TICKETS)}", "title": args["title"], "status": "open"}
    CREATED_TICKETS.append(ticket)
    return f"Created {ticket['id']}"


def build_tools() -> dict[str, Tool]:
    obj = lambda props, req: {"type": "object", "properties": props, "required": req}
    tools = [
        Tool(
            "ticket_lookup",
            "Look up one ticket by its ID (read-only).",
            obj({"ticket_id": {"type": "string"}}, ["ticket_id"]),
            _ticket_lookup,
            False,
            ("ticket_id",),
        ),
        Tool(
            "search_docs",
            "Search the policy documents (read-only).",
            obj({"query": {"type": "string"}}, ["query"]),
            _search_docs,
            False,
            ("query",),
        ),
        Tool(
            "convert_units",
            "Convert km/mi or kg/lb (pure calculation).",
            obj(
                {"value": {"type": "number"}, "from_unit": {"type": "string"}, "to_unit": {"type": "string"}},
                ["value", "from_unit", "to_unit"],
            ),
            _convert_units,
            False,
            ("value", "from_unit", "to_unit"),
        ),
        Tool(
            "create_ticket",
            "Create a new ticket. Changes data, so a human must approve.",
            obj({"title": {"type": "string"}}, ["title"]),
            _create_ticket,
            True,
            ("title",),
        ),
        Tool(
            "list_open_tickets",
            "List all open tickets (read-only).",
            obj({}, []),
            _list_open_tickets,
            False,
            (),
        ),
    ]
    return {t.name: t for t in tools}


def validate_arguments(tool: Tool, arguments: dict) -> str | None:
    """Return a problem text, or None when the arguments are acceptable."""
    missing = [k for k in tool.required if k not in arguments]
    if missing:
        return f"Missing arguments: {', '.join(missing)}"
    return None
