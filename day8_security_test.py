import json
import psycopg

data = json.load(open("day6/vector_store.json"))
query_vector = "[" + ",".join(map(str, data["records"][0]["embedding"])) + "]"

with psycopg.connect(
    "host=127.0.0.1 port=5432 dbname=parcels user=postgres password=postgres123"
) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT title, allowed_roles, COUNT(*)
            FROM document_chunks
            GROUP BY title, allowed_roles
            ORDER BY title
        """)
        print("\n=== DOCUMENT ACCESS ===")
        for row in cur.fetchall():
            print(row)

        print("\n=== SIMILARITY SEARCH BY ROLE ===")
        for role in ["agent", "supervisor", "admin"]:
            cur.execute("""
                SELECT doc_id, title, allowed_roles,
                       ROUND((embedding <=> %s::vector)::numeric, 4)
                FROM document_chunks
                WHERE tenant = %s
                  AND %s = ANY(allowed_roles)
                ORDER BY embedding <=> %s::vector
                LIMIT 5
            """, (query_vector, "parcel_demo", role, query_vector))
            rows = cur.fetchall()
            print(f"\n{role}: {len(rows)} results")
            for row in rows:
                print(row)

        cur.execute("""
            SELECT COUNT(*) FROM document_chunks
            WHERE tenant = %s AND %s = ANY(allowed_roles)
        """, ("other_tenant", "admin"))
        assert cur.fetchone()[0] == 0
        print("\nPASS: tenant isolation")

        cur.execute("""
            SELECT COUNT(*) FROM document_chunks
            WHERE tenant = 'parcel_demo'
              AND NOT ('agent' = ANY(allowed_roles))
        """)
        restricted = cur.fetchone()[0]
        print(f"Restricted chunks excluded from agent: {restricted}")
        assert restricted > 0, "No restricted chunks found; review document classification"

print("\nPASS: security checks")
