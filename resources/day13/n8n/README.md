# n8n (days 13 and 15)

## What it is
n8n is a **workflow automation tool**: boxes (called nodes) connected by lines. A workflow starts
with a *trigger* (a webhook call, a schedule, a chat message), passes data through nodes
(call an API, check a condition, run a small piece of code, ask a model) and ends with a result.
The COE uses it to receive a message, call the Python service for decisions, and reply.

## Licence in one line
n8n uses the **Sustainable Use License**: internal business, non-commercial or personal use. It is
not an open-source licence. Before you deploy it at a customer, confirm the position with n8n or
your legal team and write it in the docs (Playbook N8N-14, ORCH-02). Langflow (MIT) has no such limit.

## The rule that matters most
**n8n orchestrates; your Python service decides** (N8N-01, ORCH-03). Access checks, PII handling
and calculations live in tested Python. n8n calls them.

## Start it
1. Replace the placeholders in `docker-compose.yml` (see `../../PLACEHOLDERS.md`).
2. `cp .env.example .env`, fill it in, and **back up the encryption key** in a password manager.
3. `docker compose up -d`, then open `http://127.0.0.1:5678` and create the owner account.
4. Learning aid: the official courses at <https://learn.n8n.io/> (N8N101 Essentials, N8N102 Integrations, N8N103 In Practice).

Docker pages (n8n itself points to the Compose page first): <https://docs.n8n.io/hosting/installation/server-setups/docker-compose/> and
<https://docs.n8n.io/hosting/installation/docker/>.

## Day 13: the first workflow
1. **Webhook** node. Turn on header authentication. Keep the secret in n8n's credentials.
2. Validate the payload (an *If* or *Code* node: required fields, length limit). Reject bad input early with a clear status.
3. **HTTP Request** node: call your FastAPI `/ask` (credentials from the credential store, a timeout set, the request ID passed on).
4. **Respond to Webhook** node: return the answer and its citations.
5. Add an **error workflow** (Error Trigger node) that logs and alerts. Make writes idempotent.
6. Test with `webhook_simulator.py` in this folder. Every "reject" row must reject.
7. Export the workflow JSON into Git (after a secret search).

## Day 15: the AI agent
1. Replace step 3 by an **AI Agent** node: a chat model (your own key in credentials), Postgres chat memory scoped per user and session, and your `/ask` service as a tool.
2. Harden the system prompt with the Playbook AI rules (grounding, scope, refusal, no tool names, no executable output).
3. Set a maximum number of agent iterations and prune execution data.
4. Re-run `webhook_simulator.py`, including the "injection attempt" case, and read what the agent did.

## Check yourself
- Is the workflow's secret header really required (test the "missing secret" case)?
- Is there any logic in a Code node that should be a tested Python function?
- Is the encryption key backed up?
