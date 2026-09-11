import re
from typing import Optional

NUMBER = r"[-(]?[₹$€£]?\s*[\d,]+(?:\.\d+)?[)]?"

def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def parse_number(value: str) -> Optional[float]:
    if value is None:
        return None
    s = value.strip().replace(",", "").replace("₹", "").replace("$", "").replace("€", "").replace("£", "")
    negative = s.startswith("(") and s.endswith(")") or s.startswith("-")
    s = re.sub(r"[^0-9.]", "", s)
    if not s:
        return None
    try:
        n = float(s)
        return -n if negative else n
    except ValueError:
        return None

def all_numbers(s: str):
    return [parse_number(x) for x in re.findall(NUMBER, s) if parse_number(x) is not None]
