import io
import re
import logging
from typing import Dict

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

logger = logging.getLogger(__name__)


def extract_text_from_bytes(file_bytes: bytes) -> str:
    """Extract raw text from image bytes using pytesseract. Returns empty string if not available."""
    if not OCR_AVAILABLE:
        logger.warning("Tesseract OCR or Pillow not installed; OCR not available")
        return ""

    try:
        img = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        logger.error("OCR extraction failed: %s", e, exc_info=True)
        return ""


def parse_key_fields(text: str) -> Dict[str, str]:
    """Attempt to parse a few common fields (name, PAN, amount, salary) from OCR text."""
    if not text:
        return {}

    fields: Dict[str, str] = {}

    # PAN pattern (India): 5 letters, 4 digits, 1 letter
    pan_match = re.search(r"[A-Z]{5}[0-9]{4}[A-Z]", text)
    if pan_match:
        fields["pan_number"] = pan_match.group(0)

    # Look for amounts like 50000 or 50,000
    amt_match = re.search(r"\b(?:Rs\.?\s*)?([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?|[0-9]{4,})\b", text)
    if amt_match:
        fields["amount_mention"] = amt_match.group(0)

    # Look for keywords that commonly precede name lines
    name_match = None
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for i, line in enumerate(lines[:8]):
        if re.search(r"name|applicant|candidate", line, re.I):
            # take next token or the same line after ':'
            parts = re.split(r":|-", line)
            if len(parts) > 1 and len(parts[-1].strip()) > 2:
                name_match = parts[-1].strip()
                break
            elif i + 1 < len(lines):
                name_match = lines[i + 1].strip()
                break

    if name_match:
        fields["name"] = name_match

    return fields
