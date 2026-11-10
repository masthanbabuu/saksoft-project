import json
import psycopg
from datetime import datetime, timezone

data = json.load(open("day6/vector_store.json"))

with psycopg.connect(
    "host=127.0.0.1 port=5432 dbname=parcels user=postgres password=postgres123"
) as conn:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM document_chunks WHERE tenant = 'parcel_demo'")

        for r in data["records"]:
            title = r["title"]
            restricted = any(
                word in title.lower()
                for word in ["damage", "insurance", "hazardous", "claims"]
            )
            roles = ["supervisor", "admin"] if restricted else [
                "agent", "supervisor", "admin"
            ]

            cur.execute(
                """
                INSERT INTO document_chunks
                (doc_id, title, content, tenant, allowed_roles,
                 source, updated_at, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::vector)
                """,
                (
                    r["doc_id"], title, r["text"], "parcel_demo",
                    roles, r["doc_id"],
                    datetime.now(timezone.utc),
                    "[" + ",".join(map(str, r["embedding"])) + "]"
                )
            )

    conn.commit()

print(f"Loaded {len(data['records'])} document chunks")
