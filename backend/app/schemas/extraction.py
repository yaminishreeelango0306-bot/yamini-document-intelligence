from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class Evidence(BaseModel):
    source_text: str
    page_number: Optional[int] = None

class ExtractedField(BaseModel):
    value: Any = None
    confidence: Optional[float] = None
    page_number: Optional[int] = None
    evidence: Optional[Evidence] = None

class LineItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None
    source_text: Optional[str] = None
    page_number: Optional[int] = None

class ExtractionResult(BaseModel):
    document_type: str
    fields: Dict[str, ExtractedField] = Field(default_factory=dict)
    line_items: List[LineItem] = Field(default_factory=list)
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    raw_text_by_page: Dict[str, str] = Field(default_factory=dict)
