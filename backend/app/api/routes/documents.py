import json
import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.config import UPLOAD_DIR, ALLOWED_EXTENSIONS
from ...repositories.document_repository import (
    save_document,
    get_document,
    list_documents
)
from ...services.document_service import process_document

router=APIRouter(
    prefix="/api/v1/documents",
    tags=["documents"]
)

logger=logging.getLogger(__name__)

VALID_TYPES={
    "invoice",
    "balance_sheet",
    "profit_and_loss",
    "cash_flow_statement"
}


@router.post("/process")
async def process(
    file: UploadFile=File(...),
    document_type: str=Form(...),
    db: Session=Depends(get_db)
):
    if document_type not in VALID_TYPES:
        raise HTTPException(
            status_code=422,
            detail={
                "code":"INVALID_DOCUMENT_TYPE",
                "message":"Unsupported document_type."
            }
        )

    original_name=file.filename or "uploaded_document"

    suffix=Path(original_name).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        return JSONResponse(
            status_code=415,
            content={
                "error":{
                    "code":"UNSUPPORTED_FILE_TYPE",
                    "message":"Only PDF / JPG / PNG documents are supported."
                }
            }
        )

    safe_name=f"{uuid.uuid4().hex}{suffix}"
    path=UPLOAD_DIR/safe_name

    logger.info(
        "Upload received: %s",
        original_name
    )

    logger.info(
        "Temporary file path: %s",
        path
    )

    try:
        data=await file.read()

        if not data:
            return JSONResponse(
                status_code=400,
                content={
                    "error":{
                        "code":"EMPTY_FILE",
                        "message":"The uploaded file is empty."
                    }
                }
            )

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        path.write_bytes(data)

        logger.info(
            "File saved successfully: %s bytes",
            len(data)
        )

        logger.info(
            "Starting document processing: %s",
            original_name
        )

        result=process_document(
            str(path),
            original_name,
            document_type
        )

        logger.info(
            "Document processing completed: %s",
            original_name
        )

        save_document(
            db,
            result
        )

        logger.info(
            "Document saved to database: %s",
            original_name
        )

        if result["processing_status"]=="FAILED":
            return JSONResponse(
                status_code=422,
                content=result
            )

        return result

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Unhandled document processing error: %s",
            original_name
        )

        raise HTTPException(
            status_code=500,
            detail={
                "code":"PROCESSING_ERROR",
                "message":"The document could not be processed.",
                "details":str(exc)
            }
        )

    finally:
        logger.info(
            "Temporary file retained for debugging: %s",
            path
        )


@router.get("")
def documents(
    db: Session=Depends(get_db)
):
    rows=list_documents(db)

    return [
        {
            "document_name":x.document_name,
            "document_type":x.document_type,
            "processing_status":x.processing_status,
            "processed_at":x.processed_at.isoformat()+"Z",
            "page_count":x.page_count,
            "processing_time_ms":x.processing_time_ms
        }
        for x in rows
    ]


@router.get("/{document_name}")
def document_by_name(
    document_name: str,
    db: Session=Depends(get_db)
):
    row=get_document(
        db,
        document_name
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail={
                "code":"DOCUMENT_NOT_FOUND",
                "message":"Document not found."
            }
        )

    return json.loads(
        row.result_json
    )