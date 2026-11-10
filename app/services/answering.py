"""Grounded answering logic with tenant/role checks and source citations."""

import tiktoken

from app.models.schemas import AskResponse, Citation

_ENCODING = tiktoken.get_encoding("cl100k_base")


def _build_context(chunks, token_budget: int):
    """Build context from complete passages within the token budget."""
    selected = []
    context_parts = []

    for chunk in chunks:
        passage = f"[Source ID: {chunk.chunk_id} | Source: {chunk.source}]\n{chunk.passage}"
        candidate = "\n\n".join([*context_parts, passage])

        if len(_ENCODING.encode(candidate)) <= token_budget:
            selected.append(chunk)
            context_parts.append(passage)

    return "\n\n".join(context_parts), selected


def ask(
    question: str,
    *,
    tenant_id: str,
    role: str,
    retriever,
    generator,
    context_token_budget: int = 1200,
    retrieval_limit: int = 5,
) -> AskResponse:
    """Answer using only authorized retrieved passages and valid citations."""
    if context_token_budget <= 0:
        raise ValueError("context_token_budget must be greater than zero")

    if retrieval_limit <= 0:
        raise ValueError("retrieval_limit must be greater than zero")

    retrieved_chunks = retriever.search(
        question,
        tenant_id=tenant_id,
        role=role,
        limit=retrieval_limit,
    )

    # Defense in depth: exclude unauthorized chunks before building context.
    allowed_chunks = [
        chunk
        for chunk in retrieved_chunks
        if chunk.tenant_id == tenant_id and role in chunk.allowed_roles
    ]

    if not allowed_chunks:
        return AskResponse(
            answer="I don't know. No authorized sources support this answer.",
            citations=[],
        )

    context, selected_chunks = _build_context(
        allowed_chunks,
        context_token_budget,
    )

    if not selected_chunks:
        return AskResponse(
            answer="I don't know. No sources fit within the context budget.",
            citations=[],
        )

    draft = generator.generate(question, context)

    selected_by_id = {chunk.chunk_id: chunk for chunk in selected_chunks}
    cited_ids = draft.source_ids

    # Fail closed if the draft has no answer, no citations, or an invalid citation.
    if (
        not draft.answer.strip()
        or not cited_ids
        or any(source_id not in selected_by_id for source_id in cited_ids)
    ):
        return AskResponse(
            answer="I don't know. The available sources do not support a reliable answer.",
            citations=[],
        )

    unique_cited_ids = list(dict.fromkeys(cited_ids))
    citations = [
        Citation(
            source=selected_by_id[source_id].source,
            passage=selected_by_id[source_id].passage,
        )
        for source_id in unique_cited_ids
    ]

    return AskResponse(answer=draft.answer.strip(), citations=citations)


def answer_question(question: str) -> AskResponse:
    """Keep the existing API route safe until real dependencies are connected."""
    return AskResponse(
        answer="I don't know. No sources are available yet.",
        citations=[],
    )
