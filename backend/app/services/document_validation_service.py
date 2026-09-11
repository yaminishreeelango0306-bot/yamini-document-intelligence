import mimetypes
from pathlib import Path
from typing import Dict,Tuple

from pypdf import PdfReader
from PIL import Image

from ..core.config import (
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    MAX_FILE_SIZE_MB,
    MAX_PAGES
)


def _get_mime_type(path:Path,original_name:str)->str:
    suffix=path.suffix.lower()

    if suffix in (".jpg",".jpeg"):
        return "image/jpeg"

    if suffix==".png":
        return "image/png"

    if suffix==".pdf":
        return "application/pdf"

    return mimetypes.guess_type(original_name)[0] or "application/octet-stream"


def _failed_validation(
    mime:str,
    error:str,
    page_count:int=0,
    readable:bool=False
)->Dict:
    return {
        "file_type":mime,
        "is_supported":mime in ALLOWED_MIME_TYPES,
        "is_readable":readable,
        "page_count":page_count,
        "status":"FAILED",
        "error":error
    }


def _passed_validation(
    mime:str,
    page_count:int
)->Dict:
    return {
        "file_type":mime,
        "is_supported":True,
        "is_readable":True,
        "page_count":page_count,
        "status":"PASS"
    }


def validate_document(
    path:str,
    original_name:str
)->Tuple[Dict,object]:
    p=Path(path)

    suffix=p.suffix.lower()
    mime=_get_mime_type(p,original_name)

    if suffix not in ALLOWED_EXTENSIONS:
        return (
            _failed_validation(
                mime,
                "Only PDF / JPG / PNG documents are supported."
            ),
            None
        )

    if mime not in ALLOWED_MIME_TYPES:
        return (
            _failed_validation(
                mime,
                "The uploaded file type is not supported."
            ),
            None
        )

    if not p.exists():
        return (
            _failed_validation(
                mime,
                "The uploaded file is empty or missing."
            ),
            None
        )

    try:
        file_size=p.stat().st_size
    except OSError:
        return (
            _failed_validation(
                mime,
                "The uploaded file could not be accessed."
            ),
            None
        )

    if file_size==0:
        return (
            _failed_validation(
                mime,
                "The uploaded file is empty or missing."
            ),
            None
        )

    max_file_size=MAX_FILE_SIZE_MB*1024*1024

    if file_size>max_file_size:
        return (
            _failed_validation(
                mime,
                f"File exceeds the {MAX_FILE_SIZE_MB} MB limit."
            ),
            None
        )

    try:
        if suffix==".pdf":
            reader=PdfReader(str(p))

            page_count=len(reader.pages)

            if page_count<1:
                return (
                    _failed_validation(
                        mime,
                        "PDF contains no pages."
                    ),
                    None
                )

            if page_count>MAX_PAGES:
                return (
                    _failed_validation(
                        mime,
                        f"Maximum supported page count is {MAX_PAGES}.",
                        page_count,
                        True
                    ),
                    None
                )

            return (
                _passed_validation(
                    mime,
                    page_count
                ),
                reader
            )

        with Image.open(p) as image:
            image.verify()

        return (
            _passed_validation(
                mime,
                1
            ),
            None
        )

    except Exception:
        return (
            _failed_validation(
                mime,
                "File is corrupted or unreadable."
            ),
            None
        )