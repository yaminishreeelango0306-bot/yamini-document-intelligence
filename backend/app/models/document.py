from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from ..core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    document_name = Column(String(512), nullable=False, index=True)
    document_type = Column(String(64), nullable=False)
    processing_status = Column(String(32), nullable=False)
    file_type = Column(String(100))
    page_count = Column(Integer)
    processed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processing_time_ms = Column(Integer)
    result_json = Column(Text, nullable=False)
