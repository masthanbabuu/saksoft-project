import os
import time
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "ollama"),
    base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
    max_retries=1,
    timeout=45,
)

MODEL = os.getenv("LLM_MODEL", "llama3.2")
FALLBACK_MODEL = os.getenv("LLM_FALLBACK_MODEL", "")

def generate(prompt, system_prompt="You are a helpful assistant.",
             temperature=None, seed=None, max_tokens=None):
    models = [MODEL] + ([FALLBACK_MODEL] if FALLBACK_MODEL and FALLBACK_MODEL != MODEL else [])
    last_error = None
    for model in models:
        for attempt in range(2):
            try:
                options = {}
                if temperature is not None:
                    options["temperature"] = temperature
                if seed is not None:
                    options["seed"] = seed
                if max_tokens is not None:
                    options["max_tokens"] = max_tokens

                started = time.perf_counter()
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    **options,
                )
                return {
                    "text": response.choices[0].message.content or "",
                    "model": model,
                    "usage": response.usage.model_dump() if response.usage else {},
                    "elapsed_seconds": round(time.perf_counter() - started, 3),
                }
            except Exception as exc:
                last_error = exc
                time.sleep(1)
    raise RuntimeError(f"LLM request failed: {last_error}")
