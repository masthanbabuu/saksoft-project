import json, math, re, time
from pathlib import Path
import httpx
import tiktoken
from openai import OpenAI

OUT = Path(".")
OLLAMA = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
CHAT_MODEL = "llama3.2"
enc = tiktoken.get_encoding("cl100k_base")

# 20 synthetic parcel-logistics policy documents.
topics = [
("P01","Delivery attempts","Drivers make two delivery attempts. After the second failed attempt, the parcel is held at the local depot for five calendar days."),
("P02","Delivery delays","A parcel delayed beyond its estimated delivery date should be checked using its tracking ID. Customers receive an updated estimate when available."),
("P03","Damaged parcels","Customers should report visible parcel damage within 48 hours of delivery and provide photographs of the packaging and damaged contents."),
("P04","Lost parcels","A parcel with no tracking scan for seven consecutive days is eligible for a missing-parcel investigation."),
("P05","Address correction","Address changes are allowed before the parcel reaches the destination hub. Changes after dispatch may incur a redirection fee."),
("P06","Tracking updates","Tracking events may take up to 24 hours to appear after a physical scan. The tracking ID is required for a status enquiry."),
("P07","Delivery proof","Proof of delivery includes delivery timestamp and recipient confirmation. A photograph may be available for eligible doorstep deliveries."),
("P08","Recipient unavailable","If the recipient is unavailable, the driver records the attempt and may leave a delivery notice with redelivery instructions."),
("P09","Redelivery","Customers can request one free redelivery within five days of a failed delivery attempt. Further attempts may incur a fee."),
("P10","Parcel cancellation","A shipment can be cancelled before pickup. Once collected by the carrier, cancellation requires a return-to-sender request."),
("P11","Prohibited items","Explosives, illegal drugs, firearms, live animals and hazardous chemicals are prohibited. Restricted goods require prior written approval."),
("P12","Packaging standards","Fragile items must use a rigid outer box, protective cushioning and a fragile label. The sender is responsible for suitable packaging."),
("P13","Weight limits","Standard parcels may weigh up to 30 kilograms. Heavier shipments require freight service and advance approval."),
("P14","Delivery coverage","Remote-area deliveries may require additional time. The serviceability check uses the destination postal code."),
("P15","Refund eligibility","Shipping fees may be refunded when the carrier confirms a service failure attributable to the carrier. Requests must include the shipment ID."),
("P16","Claims process","Damage and loss claims require the shipment ID, purchase invoice and supporting photographs where applicable. Claims are reviewed within ten business days."),
("P17","Cash on delivery","Cash-on-delivery amounts must match the amount recorded on the shipment label. Payment is collected before parcel handover."),
("P18","International shipping","International shipments require an accurate customs declaration, item description and declared value. Customs authorities may inspect or delay parcels."),
("P19","Customer support","Support requests should include the tracking ID, registered phone number and a short description of the issue."),
("P20","Return to sender","Undeliverable parcels are returned to the sender after the five-day depot holding period unless the customer arranges redelivery.")
]
docs = [{"id": i, "title": title, "text": f"{title}. {body}"} for i,title,body in topics]
(OUT/"policy_documents.json").write_text(json.dumps(docs, indent=2))

# Six token-count examples: prose, code, JSON and three languages.
samples = {
    "prose": "A parcel may be delayed because of weather, traffic, or operational issues.",
    "code": 'def track(parcel_id):\n    return {"status": "in_transit", "id": parcel_id}',
    "json": '{"tracking_id":"PKG102","status":"delayed","attempts":2}',
    "Spanish": "¿Dónde está mi paquete? La entrega está retrasada.",
    "Hindi": "मेरा पार्सल कहाँ है? डिलीवरी में देरी हो रही है।",
    "Telugu": "నా పార్సెల్ ఎక్కడ ఉంది? డెలివరీ ఆలస్యం అవుతోంది."
}
token_results = {k: {"tokens": len(enc.encode(v)), "characters": len(v)} for k,v in samples.items()}
(OUT/"token_lab.json").write_text(json.dumps(token_results, indent=2))
print("Token counts:", token_results)

# Three distinct chunking methods.
def chunks_fixed(text, size=105, overlap=20):
    return [text[i:i+size] for i in range(0, len(text), size-overlap)]

def chunks_paragraph(text):
    return [p.strip() for p in re.split(r'(?<=[.!?])\s+', text) if p.strip()]

def chunks_sentence_window(text, window=2):
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    return [" ".join(sentences[i:i+window]) for i in range(0, len(sentences), window)]

strategies = {
    "fixed_overlap": chunks_fixed,
    "sentence": chunks_paragraph,
    "sentence_window": chunks_sentence_window,
}

client = httpx.Client(timeout=90)
def embed(texts):
    response = client.post(
        f"{OLLAMA}/api/embed",
        json={"model": EMBED_MODEL, "input": texts}
    )
    response.raise_for_status()
    return response.json()["embeddings"]

def cosine(a,b):
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    return dot/(na*nb) if na and nb else 0.0

questions = [
("Where are parcels held after two failed delivery attempts?", "P01"),
("When should customers report visible damage?", "P03"),
("When can a missing parcel investigation begin?", "P04"),
("Until when can a customer change the delivery address?", "P05"),
("How long can tracking events take to appear?", "P06"),
("What evidence is needed for a damage claim?", "P16"),
("What is the maximum standard parcel weight?", "P13"),
("How many free redelivery requests are allowed?", "P09"),
("What documents are needed for international customs?", "P18"),
("When are parcels returned to the sender?", "P20"),
]

all_results = {}
best_name, best_score = None, -1
best_index = None

for name, splitter in strategies.items():
    records = []
    for doc in docs:
        for part in splitter(doc["text"]):
            records.append({"doc_id":doc["id"], "title":doc["title"], "text":part})
    vectors = embed([r["text"] for r in records])
    for record, vector in zip(records, vectors):
        record["embedding"] = vector

    hits = 0
    for question, expected in questions:
        qv = embed([question])[0]
        ranked = sorted(records, key=lambda r: cosine(qv,r["embedding"]), reverse=True)
        if any(r["doc_id"] == expected for r in ranked[:3]):
            hits += 1

    score = hits / len(questions)
    all_results[name] = {
        "chunks": len(records),
        "top3_hits": hits,
        "top3_accuracy": round(score, 3)
    }
    print(f"{name}: {hits}/10 top-3 hits, {len(records)} chunks")
    if score > best_score:
        best_name, best_score, best_index = name, score, records

# Save the best strategy's simple JSON vector store.
(OUT/"vector_store.json").write_text(json.dumps({
    "embedding_model": EMBED_MODEL,
    "chunking_strategy": best_name,
    "records": best_index
}, indent=2))

# Answer ten questions using top-3 retrieval and the local LLM.
chat = OpenAI(api_key="ollama", base_url=f"{OLLAMA}/v1", timeout=90)
answers = []
for question, expected in questions:
    qv = embed([question])[0]
    ranked = sorted(best_index, key=lambda r: cosine(qv,r["embedding"]), reverse=True)
    context = "\n".join(r["text"] for r in ranked[:3])
    prompt = (
        "Answer using ONLY the policy context. If the answer is absent, say "
        "'The policy does not specify'. Do not invent details.\n\n"
        f"Context:\n{context}\n\nQuestion: {question}"
    )
    try:
        start = time.perf_counter()
        response = chat.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role":"user","content":prompt}],
            temperature=0
        )
        answer = response.choices[0].message.content
        elapsed = round(time.perf_counter()-start, 2)
    except Exception as exc:
        answer, elapsed = f"LLM error: {exc}", None
    answers.append({
        "question":question,
        "answer":answer,
        "expected_policy":expected,
        "retrieved_policy":ranked[0]["doc_id"],
        "top3_contains_expected":any(r["doc_id"]==expected for r in ranked[:3]),
        "seconds":elapsed
    })
    print("Answered:", question)

(OUT/"retrieval_answers.json").write_text(json.dumps(answers, indent=2))
(OUT/"chunking_comparison.json").write_text(json.dumps(all_results, indent=2))

best = max(all_results, key=lambda x: all_results[x]["top3_accuracy"])
(OUT/"chunking_analysis.md").write_text(f"""# Chunking strategy evaluation

| Strategy | Chunks | Top-3 hits | Accuracy |
|---|---:|---:|---:|
""" + "\n".join(
    f"| {n} | {v['chunks']} | {v['top3_hits']}/10 | {v['top3_accuracy']:.0%} |"
    for n,v in all_results.items()
) + f"""

## Result
Best strategy in this small synthetic test: **{best}**.

The winning strategy retrieves the expected policy most often within the top three results. Fixed-size chunks are simple but can split related facts; sentence chunks preserve meaning but may be too short; sentence windows retain nearby context at the cost of larger chunks. Results depend on document length, embedding model and question wording.
""")

print("\nDAY 6 RETRIEVAL COMPLETE")
print("Best strategy:", best_name)
print("Created token_lab.json, policy_documents.json, vector_store.json,")
print("retrieval_answers.json, chunking_comparison.json, chunking_analysis.md")
