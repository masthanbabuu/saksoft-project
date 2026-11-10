import csv
import json
import os
import time
from pathlib import Path
from llm_client import generate

def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Cannot read {path}: {exc}")
        return []

cvs = load_json("cv_results.json")
invoices = load_json("invoice_results.json")

cv_ok = sum("data" in item for item in cvs)
invoice_ok = sum("invoice" in item for item in invoices)

# Accuracy review sheet: fill expected values and mark correctness manually.
with open("accuracy_review_10.csv", "w", newline="", encoding="utf-8") as f:
    fields = [
        "file", "expected_name", "extracted_name", "name_correct",
        "expected_email", "extracted_email", "email_correct",
        "expected_phone", "extracted_phone", "phone_correct",
        "review_notes"
    ]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    for item in cvs[:10]:
        data = item.get("data", {})
        writer.writerow({
            "file": item.get("file", ""),
            "extracted_name": data.get("full_name", ""),
            "extracted_email": data.get("email", ""),
            "extracted_phone": data.get("phone", ""),
        })

# Test configurable local model settings and record speed/failures.
benchmarks = []
tests = [
    ("default", {}),
    ("temperature_seed", {"temperature": 0.2, "seed": 42, "max_tokens": 80}),
    ("context_limit", {"temperature": 0, "max_tokens": 80}),
]
for name, options in tests:
    try:
        result = generate(
            "Reply with exactly: DAY5_OK",
            system_prompt="You are a concise test assistant.",
            **options,
        )
        benchmarks.append({
            "test": name,
            "model": result["model"],
            "seconds": result["elapsed_seconds"],
            "usage": result["usage"],
            "success": True,
        })
        print(f"PASS {name}: {result['elapsed_seconds']}s")
    except Exception as exc:
        benchmarks.append({"test": name, "success": False, "error": str(exc)})
        print(f"FAIL {name}: {exc}")

# Optional hosted test, enabled by environment variables.
hosted_url = os.getenv("HOSTED_LLM_BASE_URL")
hosted_key = os.getenv("HOSTED_LLM_API_KEY")
hosted_model = os.getenv("HOSTED_LLM_MODEL")
if hosted_url and hosted_key and hosted_model:
    try:
        from openai import OpenAI
        hosted = OpenAI(api_key=hosted_key, base_url=hosted_url, timeout=45)
        start = time.perf_counter()
        response = hosted.chat.completions.create(
            model=hosted_model,
            messages=[{"role": "user", "content": "Reply with exactly: DAY5_OK"}],
            max_tokens=30,
        )
        benchmarks.append({
            "test": "hosted",
            "model": hosted_model,
            "seconds": round(time.perf_counter() - start, 3),
            "usage": response.usage.model_dump() if response.usage else {},
            "success": True,
        })
        print("PASS hosted benchmark")
    except Exception as exc:
        benchmarks.append({"test": "hosted", "success": False, "error": str(exc)})
        print("FAIL hosted benchmark:", exc)
else:
    print("SKIP hosted benchmark: hosted endpoint credentials not configured")

report = {
    "cv_files": len(cvs),
    "cv_success": cv_ok,
    "invoice_files": len(invoices),
    "invoice_success": invoice_ok,
    "benchmarks": benchmarks,
    "accuracy_review": "Complete accuracy_review_10.csv against source CVs",
}
Path("day5_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

print("\n=== DAY 5 RESULTS ===")
print(f"CV extraction: {cv_ok}/{len(cvs)}")
print(f"Invoice extraction: {invoice_ok}/{len(invoices)}")
print("Created: accuracy_review_10.csv, day5_report.json")
