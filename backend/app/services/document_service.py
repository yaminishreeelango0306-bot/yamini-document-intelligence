import time
import logging
from datetime import datetime

from .document_validation_service import validate_document
from .ocr_service import extract_text
from .extraction_service import extract_document
from .financial_validation_service import validate_financials

logger=logging.getLogger(__name__)


def process_document(path,document_name,document_type):
    started=time.perf_counter()

    validation_started=time.perf_counter()

    validation,_=validate_document(
        path,
        document_name
    )

    validation_time=int(
        (time.perf_counter()-validation_started)*1000
    )

    logger.info(
        "Document validation completed: %s ms",
        validation_time
    )

    if validation["status"]!="PASS":
        return {
            "document_name":document_name,
            "document_type":document_type,
            "processing_status":"FAILED",
            "overall_confidence":None,
            "file_validation":validation,
            "extracted_data":{},
            "validation":{
                "checks":[],
                "overall_status":"NOT_APPLICABLE",
                "issues":[
                    validation.get(
                        "error",
                        "Validation failed."
                    )
                ]
            },
            "processing_metadata":{
                "ocr_used":False,
                "processed_at":None,
                "processing_time_ms":int(
                    (time.perf_counter()-started)*1000
                )
            }
        }

    try:
        logger.info(
            "Document processing started: %s",
            document_name
        )

        ocr_started=time.perf_counter()

        logger.info(
            "OCR started: %s",
            document_name
        )

        texts=extract_text(path)

        ocr_time=int(
            (time.perf_counter()-ocr_started)*1000
        )

        logger.info(
            "OCR completed: %s | %s ms",
            document_name,
            ocr_time
        )

        extraction_started=time.perf_counter()

        logger.info(
            "Extraction started: %s",
            document_name
        )

        extracted=extract_document(
            texts,
            document_type
        )

        extraction_time=int(
            (time.perf_counter()-extraction_started)*1000
        )

        logger.info(
            "Extraction completed: %s | %s ms",
            document_name,
            extraction_time
        )

        detected_type=(
            extracted.get("document_type")
            or document_type
        )

        logger.info(
            "Document type detected: %s",
            detected_type
        )

        validation_started=time.perf_counter()

        logger.info(
            "Financial validation started: %s",
            document_name
        )

        validation_result=validate_financials(
            detected_type,
            extracted["fields"],
            extracted["line_items"]
        )

        financial_validation_time=int(
            (time.perf_counter()-validation_started)*1000
        )

        logger.info(
            "Financial validation completed: %s | %s ms",
            document_name,
            financial_validation_time
        )

        extracted_data={
            k:v
            for k,v in extracted["fields"].items()
        }

        if extracted["line_items"]:
            extracted_data["line_items"]=(
                extracted["line_items"]
            )

        extracted_data["tables"]=(
            extracted["tables"]
        )

        extracted_data["raw_text_by_page"]=(
            extracted["raw_text_by_page"]
            if "raw_text_by_page" in extracted
            else texts
        )

        confidences=[]

        for value in extracted["fields"].values():
            if (
                isinstance(value,dict)
                and isinstance(
                    value.get("confidence"),
                    (int,float)
                )
            ):
                confidences.append(
                    float(value["confidence"])
                )

        overall=(
            sum(confidences)/len(confidences)
            if confidences
            else None
        )

        total_time=int(
            (time.perf_counter()-started)*1000
        )

        logger.info(
            "Document processing completed: %s | total=%s ms | ocr=%s ms | extraction=%s ms | validation=%s ms",
            document_name,
            total_time,
            ocr_time,
            extraction_time,
            financial_validation_time
        )

        return {
            "document_name":document_name,
            "document_type":detected_type,
            "processing_status":"PASS",
            "overall_confidence":(
                round(overall,3)
                if overall is not None
                else None
            ),
            "file_validation":validation,
            "extracted_data":extracted_data,
            "validation":validation_result,
            "processing_metadata":{
                "ocr_used":True,
                "processed_at":(
                    datetime.utcnow().isoformat()+"Z"
                ),
                "processing_time_ms":total_time,
                "ocr_time_ms":ocr_time,
                "extraction_time_ms":extraction_time,
                "financial_validation_time_ms":(
                    financial_validation_time
                )
            }
        }

    except Exception:
        logger.exception(
            "Processing failed for %s",
            document_name
        )
        raise