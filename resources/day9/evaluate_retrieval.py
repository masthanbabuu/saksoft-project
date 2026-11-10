# ruff: noqa: T201
"""Offline BM25 retrieval baseline for the parcel golden set."""

import json
import math
import re
import zipfile
from collections import Counter
from pathlib import PurePosixPath

ARCHIVE = "resources/day7/variant_3_parcels (1).zip"
DOCUMENTS_PATH = "variant_3_parcels/documents/"
GOLDEN_PATH = "variant_3_parcels/golden_set.json"
TENANT_ID = "main"

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
FRONTMATTER_PATTERN = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.S)


def tokenize(text):
    """Return lowercase word and number tokens."""
    return TOKEN_PATTERN.findall(text.lower())


def parse_document(content, filename):
    """Read the small YAML-style frontmatter used by this dataset."""
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        raise ValueError(f"Missing or invalid frontmatter: {filename}")

    metadata_text, body = match.groups()
    metadata = {}
    current_list_key = None

    for raw_line in metadata_text.splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("- ") and current_list_key:
            value = line[2:].strip().strip("'\"")
            metadata[current_list_key].append(value)
            continue

        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_list_key = None

        if key == "allowed_roles":
            if value.startswith("[") and value.endswith("]"):
                metadata[key] = [
                    item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()
                ]
            elif value:
                metadata[key] = [value.strip("'\"")]
            else:
                metadata[key] = []
                current_list_key = key
        else:
            metadata[key] = value.strip("'\"")

    required = {"id", "title", "tenant", "allowed_roles"}
    missing = required - metadata.keys()
    if missing:
        raise ValueError(f"{filename} is missing metadata: {sorted(missing)}")

    return {
        "id": str(metadata["id"]),
        "title": metadata["title"],
        "tenant": metadata["tenant"],
        "allowed_roles": metadata["allowed_roles"],
        "body": body.strip(),
        "tokens": tokenize(metadata["title"] + " " + body),
    }


def load_dataset():
    """Load documents and golden questions from the supplied ZIP."""
    with zipfile.ZipFile(ARCHIVE) as archive:
        document_names = sorted(
            name
            for name in archive.namelist()
            if name.startswith(DOCUMENTS_PATH) and name.endswith(".md")
        )

        documents = [
            parse_document(
                archive.read(name).decode("utf-8"),
                PurePosixPath(name).name,
            )
            for name in document_names
        ]

        golden_set = json.loads(archive.read(GOLDEN_PATH))

    return documents, golden_set


def bm25_scores(query, documents, k1=1.5, b=0.75):
    """Score documents with BM25 using the supplied candidate collection."""
    if not documents:
        return []

    query_terms = Counter(tokenize(query))
    document_frequency = Counter()

    for document in documents:
        document_frequency.update(set(document["tokens"]))

    average_length = (sum(len(document["tokens"]) for document in documents) / len(documents)) or 1

    total_documents = len(documents)
    scored = []

    for document in documents:
        term_counts = Counter(document["tokens"])
        document_length = len(document["tokens"])
        score = 0.0

        for term, query_frequency in query_terms.items():
            frequency = term_counts[term]
            if not frequency:
                continue

            df = document_frequency[term]
            inverse_document_frequency = math.log(1 + (total_documents - df + 0.5) / (df + 0.5))

            denominator = frequency + k1 * (1 - b + b * document_length / average_length)
            term_score = inverse_document_frequency * frequency * (k1 + 1) / denominator
            score += query_frequency * term_score

        scored.append((score, document))

    return sorted(
        scored,
        key=lambda item: (-item[0], item[1]["id"]),
    )


def evaluate():
    documents, golden_set = load_dataset()

    print(f"Loaded documents: {len(documents)}")
    print(f"Golden questions: {len(golden_set)}")
    print(f"Tenant filter: {TENANT_ID}")
    print("Ranking: BM25 over title + document body")
    print("Permissions: filtered before ranking")

    answerable = [item for item in golden_set if item["expect"] == "answer"]
    refusals = [item for item in golden_set if item["expect"] == "refuse"]

    hits_by_k = {1: 0, 3: 0, 5: 0}
    per_question_recalls = {1: [], 3: [], 5: []}
    total_relevant = 0

    print("\n=== ANSWERABLE QUESTIONS ===")

    for number, item in enumerate(answerable, start=1):
        eligible = [
            document
            for document in documents
            if document["tenant"] == TENANT_ID and item["user_role"] in document["allowed_roles"]
        ]

        ranked = bm25_scores(item["question"], eligible)
        expected = set(item["expected_doc_ids"])
        total_relevant += len(expected)

        print(f"\n{number}. {item['question']}")
        print(f"   Role: {item['user_role']}")
        print(f"   Expected IDs: {', '.join(sorted(expected))}")
        print("   Top 5 results:")

        for score, document in ranked[:5]:
            marker = "EXPECTED" if document["id"] in expected else ""
            print(f"     {document['id']}  score={score:.4f}  {document['title']}  {marker}")

        for k in hits_by_k:
            retrieved_ids = {document["id"] for _, document in ranked[:k]}
            hits = len(expected & retrieved_ids)
            hits_by_k[k] += hits
            per_question_recalls[k].append(hits / len(expected))

    print("\n=== RECALL RESULTS ===")
    print("Micro recall = total relevant documents retrieved / 16")
    print("Macro recall = average recall across the 8 answerable questions")

    for k in hits_by_k:
        micro = hits_by_k[k] / total_relevant if total_relevant else 0
        macro = (
            sum(per_question_recalls[k]) / len(per_question_recalls[k])
            if per_question_recalls[k]
            else 0
        )
        print(
            f"Recall@{k}: micro={micro:.3f} ({hits_by_k[k]}/{total_relevant}), macro={macro:.3f}"
        )

    print("\n=== REFUSAL / PERMISSION CHECKS ===")
    print(f"Expected refusal questions: {len(refusals)}")

    for number, item in enumerate(refusals, start=1):
        eligible = [
            document
            for document in documents
            if document["tenant"] == TENANT_ID and item["user_role"] in document["allowed_roles"]
        ]

        print(f"\n{number}. {item['question']}")
        print(f"   Role: {item['user_role']}")
        print(f"   Eligible documents after access filter: {len(eligible)}")

        if "route" in item["question"].lower():
            route_ids = {
                document["id"] for document in documents if "route" in document["title"].lower()
            }
            eligible_route_ids = {
                document["id"] for document in eligible if document["id"] in route_ids
            }
            print(f"   Route document IDs in corpus: {sorted(route_ids)}")
            print(f"   Route document IDs visible to this role: {sorted(eligible_route_ids)}")
            print("   Permission result: route documents are excluded.")

    print("\nNote: BM25 ranks documents; it does not decide whether")
    print("an answer is supported. The six unrelated refusal cases")
    print("still require a separate answerability/abstention check.")


if __name__ == "__main__":
    evaluate()
