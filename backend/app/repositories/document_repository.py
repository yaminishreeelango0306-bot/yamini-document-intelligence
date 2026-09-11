import json
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.orm import Session
from ..models.document import Document

def save_document(db, result):
    name=result["document_name"]
    existing=db.query(Document).filter(Document.document_name==name).first()
    if existing:
        existing.document_type=result["document_type"]
        existing.processing_status=result["processing_status"]
        existing.file_type=result["file_validation"]["file_type"]
        existing.page_count=result["file_validation"]["page_count"]
        existing.processed_at=datetime.utcnow()
        existing.processing_time_ms=result["processing_metadata"].get("processing_time_ms")
        existing.result_json=json.dumps(result)
        doc=existing
    else:
        doc=Document(document_name=name,document_type=result["document_type"],
                     processing_status=result["processing_status"],
                     file_type=result["file_validation"]["file_type"],
                     page_count=result["file_validation"]["page_count"],
                     processed_at=datetime.utcnow(),
                     processing_time_ms=result["processing_metadata"].get("processing_time_ms"),
                     result_json=json.dumps(result))
        db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_document(db,name):
    return db.query(Document).filter(Document.document_name==name).order_by(desc(Document.processed_at)).first()

def list_documents(db):
    return db.query(Document).order_by(desc(Document.processed_at)).all()
