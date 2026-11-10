"""Tests for grounded answering, context limits, and source citations."""

from dataclasses import dataclass

import tiktoken

from app.services.answering import ask


@dataclass(frozen=True)
class FakeChunk:
    chunk_id: str
    source: str
    passage: str
    tenant_id: str
    allowed_roles: tuple[str, ...]


@dataclass(frozen=True)
class FakeDraft:
    answer: str
    source_ids: list[str]


class FakeRetriever:
    def __init__(self, chunks):
        self.chunks = chunks
        self.last_request = None

    def search(self, question, *, tenant_id, role, limit):
        self.last_request = {
            "question": question,
            "tenant_id": tenant_id,
            "role": role,
            "limit": limit,
        }
        return self.chunks[:limit]


class FakeGenerator:
    def __init__(self, draft):
        self.draft = draft
        self.last_context = None

    def generate(self, question, context):
        self.last_context = context
        return self.draft


def test_ask_returns_answer_with_only_cited_source_passages():
    chunk = FakeChunk(
        chunk_id="3011",
        source="3011-delivery-window-policy.md",
        passage="A standard parcel is delivered within 3 working days.",
        tenant_id="main",
        allowed_roles=("dispatcher", "driver", "customer"),
    )
    retriever = FakeRetriever([chunk])
    generator = FakeGenerator(FakeDraft("Within 3 working days.", ["3011"]))

    result = ask(
        "How long does delivery take?",
        tenant_id="main",
        role="dispatcher",
        retriever=retriever,
        generator=generator,
    )

    assert result.answer == "Within 3 working days."
    assert len(result.citations) == 1
    assert result.citations[0].source == "3011-delivery-window-policy.md"
    assert result.citations[0].passage == chunk.passage


def test_ask_returns_i_dont_know_when_no_sources_are_found():
    retriever = FakeRetriever([])
    generator = FakeGenerator(FakeDraft("An unsupported answer.", []))

    result = ask(
        "What is the loan limit?",
        tenant_id="main",
        role="dispatcher",
        retriever=retriever,
        generator=generator,
    )

    assert result.answer.startswith("I don't know")
    assert result.citations == []
    assert generator.last_context is None


def test_ask_rejects_a_citation_for_an_unretrieved_source():
    chunk = FakeChunk(
        chunk_id="3011",
        source="3011-delivery-window-policy.md",
        passage="A standard parcel is delivered within 3 working days.",
        tenant_id="main",
        allowed_roles=("dispatcher",),
    )
    retriever = FakeRetriever([chunk])
    generator = FakeGenerator(FakeDraft("It takes 3 days.", ["9999"]))

    result = ask(
        "How long does delivery take?",
        tenant_id="main",
        role="dispatcher",
        retriever=retriever,
        generator=generator,
    )

    assert result.answer.startswith("I don't know")
    assert result.citations == []


def test_ask_passes_tenant_and_role_to_retriever():
    retriever = FakeRetriever([])
    generator = FakeGenerator(FakeDraft("", []))

    ask(
        "A question",
        tenant_id="tenant-a",
        role="dispatcher",
        retriever=retriever,
        generator=generator,
    )

    assert retriever.last_request["tenant_id"] == "tenant-a"
    assert retriever.last_request["role"] == "dispatcher"


def test_ask_does_not_exceed_context_token_budget():
    chunks = [
        FakeChunk(
            chunk_id=str(index),
            source=f"source-{index}.md",
            passage="Delivery policy applies within 3 working days.",
            tenant_id="main",
            allowed_roles=("dispatcher",),
        )
        for index in range(3)
    ]
    retriever = FakeRetriever(chunks)
    generator = FakeGenerator(FakeDraft("I don't know.", []))

    ask(
        "Explain the delivery policy.",
        tenant_id="main",
        role="dispatcher",
        retriever=retriever,
        generator=generator,
        context_token_budget=30,
    )

    assert generator.last_context is not None
    encoding = tiktoken.get_encoding("cl100k_base")
    assert len(encoding.encode(generator.last_context)) <= 30


def test_ask_does_not_send_unauthorized_chunks_to_generator():
    unauthorized_chunk = FakeChunk(
        chunk_id="3081",
        source="3081-hazardous-goods-policy.md",
        passage="Restricted hazardous goods policy.",
        tenant_id="main",
        allowed_roles=("supervisor",),
    )

    retriever = FakeRetriever([unauthorized_chunk])
    generator = FakeGenerator(FakeDraft("Restricted information.", ["3081"]))

    result = ask(
        "Explain the restricted policy.",
        tenant_id="main",
        role="dispatcher",
        retriever=retriever,
        generator=generator,
    )

    assert result.answer.startswith("I don't know")
    assert result.citations == []
    assert generator.last_context is None


def test_ask_refuses_when_generator_cannot_support_an_answer():
    chunk = FakeChunk(
        chunk_id="3011",
        source="3011-delivery-window-policy.md",
        passage="A standard parcel is delivered within 3 working days.",
        tenant_id="main",
        allowed_roles=("dispatcher",),
    )
    retriever = FakeRetriever([chunk])

    # The generator cannot support an answer with a valid source citation.
    generator = FakeGenerator(FakeDraft("The director's favourite colour is blue.", []))

    result = ask(
        "What is the director's favourite colour?",
        tenant_id="main",
        role="dispatcher",
        retriever=retriever,
        generator=generator,
    )

    assert result.answer.startswith("I don't know")
    assert result.citations == []
