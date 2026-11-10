import json
from pathlib import Path
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from pydantic import BaseModel, Field
from llm_client import generate


class Invoice(BaseModel):
    invoice_number: str | None = None
    invoice_date: str | None = None
    vendor: str | None = None
    customer: str | None = None
    subtotal: float | None = None
    tax: float | None = None
    total: float | None = None
    currency: str | None = None
    line_items: list[dict] = Field(default_factory=list)


def extract_text(path):
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        pages = convert_from_path(str(path), dpi=250)
        return "\n".join(pytesseract.image_to_string(p) for p in pages)
    return pytesseract.image_to_string(Image.open(path))


def extract_invoice(path):
    text = extract_text(path)
    result = generate(
        "Extract invoice facts from this OCR text. Return JSON only with "
        "invoice_number, invoice_date, vendor, customer, subtotal, tax, "
        "total, currency, line_items. Use null for unknown values. "
        "Do not invent facts.\n\n" + text
    )
    raw = result["text"]
    start, end = raw.find("{"), raw.rfind("}") + 1
    if start < 0 or end <= start:
        raise ValueError("Model did not return JSON")
    data = Invoice.model_validate_json(raw[start:end])
    return {
        "file": Path(path).name,
        "model": result["model"],
        "usage": result["usage"],
        "ocr_text": text,
        "invoice": data.model_dump()
    }


if __name__ == "__main__":
    files = [
        Path("../day5_samples/invoice_image/invoice.png"),
        Path("../day5_samples/scanned_page/invoice_scan.pdf")
    ]
    results = []
    for file in files:
        try:
            results.append(extract_invoice(file))
            print("Processed:", file.name)
        except Exception as e:
            results.append({"file": file.name, "error": str(e)})
            print("Failed:", file.name, str(e))

    Path("invoice_results.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    print("Saved invoice_results.json")
