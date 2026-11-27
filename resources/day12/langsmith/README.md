# LangSmith (day 12 and day 33)

## What it is
LangSmith is a **hosted tool for seeing what an AI app did**: every model call, tool call and
step is recorded as a *trace* you can open and read. It is made by the LangChain company and works
very smoothly with LangGraph. It is not LangGraph itself: LangGraph builds the agent, LangSmith watches it.

## Is it free?
There is a free **Developer** plan: one seat, up to **5,000 base traces a month**, then
pay as you go; base traces are kept 14 days. The paid plan is priced per seat. Check the current
numbers on the pricing page before you rely on them: <https://www.langchain.com/pricing>.
Read the terms of service before using it for anything beyond training:
<https://www.langchain.com/terms-of-service>.

## Data rule (important)
Traces go to LangChain's cloud. In this programme only **synthetic or public data** is sent
(Playbook OBS-13). For customer data, self-host a tracing tool or have a contract and redact first.
Free plans have limits: set a sampling rate and check your usage weekly (OBS-14).

## Set it up (10 minutes)
1. Create a free account and an API key in the LangSmith settings (official page for tracing a LangGraph app:
   <https://docs.langchain.com/langsmith/trace-with-langgraph>).
2. In your terminal set two variables (never write the key into a file):
   ```bash
   export LANGSMITH_TRACING=true
   export LANGSMITH_API_KEY=<your key>
   # Only if your account is outside the US region, also set LANGSMITH_ENDPOINT to the URL for your region (no trailing slash).
   ```
   Windows PowerShell: `$env:LANGSMITH_TRACING="true"` and `$env:LANGSMITH_API_KEY="<your key>"`.
3. Run `python trace_demo.py` in `../langgraph_lab/` (it uses a fake model: no model key, no cost).
4. Open LangSmith, open the project, click the newest trace and read it: model call, tool call, model call.

## What to look for (day 33)
- Which step is slowest? Which step costs the most tokens?
- Can you find the exact tool arguments the model chose?
- Compare with Jaeger (`../jaeger/`): Jaeger shows timing across services, LangSmith shows what the model and tools did. Write two sentences on what each adds.

## Langfuse in words (no lab)
Langfuse is an **open-source** alternative that you can run yourself, so customer data stays in
your environment. Self-hosting needs several services (PostgreSQL, ClickHouse, Redis and blob
storage) and the official guide asks for a machine with 4 cores and 16 GiB for the VM route, so it is
too heavy for a trainee laptop. It also has a free cloud Hobby plan (50k units a month, 30 days of
data, 2 users). Know when to propose it: when a customer's data must not leave. Pages:
<https://langfuse.com/self-hosting> and <https://langfuse.com/pricing>.
