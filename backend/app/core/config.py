import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'document_intelligence.db'}")
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads")))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "15"))
MAX_PAGES = int(os.getenv("MAX_PAGES", "3"))
OCR_DPI = int(os.getenv("OCR_DPI", "220"))
OCR_LANG = os.getenv("OCR_LANG", "eng")
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png"}
TOLERANCE = float(os.getenv("FINANCIAL_TOLERANCE", "0.02"))
CORS_ORIGINS = [x.strip() for x in os.getenv("CORS_ORIGINS", "*").split(",") if x.strip()]

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
