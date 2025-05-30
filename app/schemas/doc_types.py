"""
Document type schemas and classifications
Generated from docTypes.json schema
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class DocumentType(str, Enum):
    """Enumeration of supported document types"""
    EMAIL = "email"
    INVOICE = "invoice"
    CONTRACT = "contract"
    REPORT = "report"
    MEMO = "memo"
    LETTER = "letter"
    FORM = "form"
    RECEIPT = "receipt"
    STATEMENT = "statement"
    PROPOSAL = "proposal"
    PRESENTATION = "presentation"
    SPREADSHEET = "spreadsheet"
    UNKNOWN = "unknown"

class DocumentTypeInfo(BaseModel):
    """Information about a document type"""
    type_id: str = Field(description="Document type identifier")
    name: str = Field(description="Human-readable type name")
    description: str = Field(description="Type description")
    category: str = Field(description="Type category")
    confidence_threshold: float = Field(0.7, description="Minimum confidence for classification")
    
class DocumentCategory(str, Enum):
    """Document categories for grouping"""
    COMMUNICATION = "communication"
    FINANCIAL = "financial"
    LEGAL = "legal"
    ADMINISTRATIVE = "administrative"
    TECHNICAL = "technical"
    MARKETING = "marketing"
    OTHER = "other"

class DocumentClassification(BaseModel):
    """Document classification result"""
    doc_type: DocumentType = Field(description="Classified document type")
    category: DocumentCategory = Field(description="Document category")
    confidence: float = Field(ge=0.0, le=1.0, description="Classification confidence")
    alternative_types: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Alternative classifications with confidence scores"
    )
    features: Optional[Dict[str, Any]] = Field(
        None,
        description="Features used for classification"
    )

# Document type definitions with metadata
DOCUMENT_TYPES = {
    DocumentType.EMAIL: DocumentTypeInfo(
        type_id="email",
        name="Email",
        description="Electronic mail message",
        category=DocumentCategory.COMMUNICATION.value,
        confidence_threshold=0.8
    ),
    DocumentType.INVOICE: DocumentTypeInfo(
        type_id="invoice",
        name="Invoice",
        description="Bill for goods or services",
        category=DocumentCategory.FINANCIAL.value,
        confidence_threshold=0.85
    ),
    DocumentType.CONTRACT: DocumentTypeInfo(
        type_id="contract",
        name="Contract",
        description="Legal agreement between parties",
        category=DocumentCategory.LEGAL.value,
        confidence_threshold=0.9
    ),
    DocumentType.REPORT: DocumentTypeInfo(
        type_id="report",
        name="Report",
        description="Formal document presenting information",
        category=DocumentCategory.ADMINISTRATIVE.value,
        confidence_threshold=0.75
    ),
    DocumentType.MEMO: DocumentTypeInfo(
        type_id="memo",
        name="Memorandum",
        description="Internal communication document",
        category=DocumentCategory.COMMUNICATION.value,
        confidence_threshold=0.7
    ),
    DocumentType.LETTER: DocumentTypeInfo(
        type_id="letter",
        name="Letter",
        description="Formal written communication",
        category=DocumentCategory.COMMUNICATION.value,
        confidence_threshold=0.75
    ),
    DocumentType.FORM: DocumentTypeInfo(
        type_id="form",
        name="Form",
        description="Structured document for data collection",
        category=DocumentCategory.ADMINISTRATIVE.value,
        confidence_threshold=0.8
    ),
    DocumentType.RECEIPT: DocumentTypeInfo(
        type_id="receipt",
        name="Receipt",
        description="Proof of payment document",
        category=DocumentCategory.FINANCIAL.value,
        confidence_threshold=0.85
    ),
    DocumentType.STATEMENT: DocumentTypeInfo(
        type_id="statement",
        name="Statement",
        description="Account or financial statement",
        category=DocumentCategory.FINANCIAL.value,
        confidence_threshold=0.8
    ),
    DocumentType.PROPOSAL: DocumentTypeInfo(
        type_id="proposal",
        name="Proposal",
        description="Business or project proposal",
        category=DocumentCategory.ADMINISTRATIVE.value,
        confidence_threshold=0.75
    ),
    DocumentType.PRESENTATION: DocumentTypeInfo(
        type_id="presentation",
        name="Presentation",
        description="Slide deck or presentation document",
        category=DocumentCategory.ADMINISTRATIVE.value,
        confidence_threshold=0.7
    ),
    DocumentType.SPREADSHEET: DocumentTypeInfo(
        type_id="spreadsheet",
        name="Spreadsheet",
        description="Tabular data document",
        category=DocumentCategory.TECHNICAL.value,
        confidence_threshold=0.8
    ),
    DocumentType.UNKNOWN: DocumentTypeInfo(
        type_id="unknown",
        name="Unknown",
        description="Unclassified document type",
        category=DocumentCategory.OTHER.value,
        confidence_threshold=0.0
    )
}

def get_document_type_info(doc_type: DocumentType) -> DocumentTypeInfo:
    """Get information for a document type"""
    return DOCUMENT_TYPES.get(doc_type, DOCUMENT_TYPES[DocumentType.UNKNOWN])

def get_types_by_category(category: DocumentCategory) -> List[DocumentType]:
    """Get all document types in a category"""
    return [
        doc_type for doc_type, info in DOCUMENT_TYPES.items()
        if info.category == category.value
    ]

def classify_document_type(features: Dict[str, Any]) -> DocumentClassification:
    """
    Simple rule-based document type classification
    This would be replaced with ML model predictions in production
    """
    text = features.get("text", "").lower()
    
    # Simple heuristic classification
    if "invoice" in text or "bill" in text or "amount due" in text:
        return DocumentClassification(
            doc_type=DocumentType.INVOICE,
            category=DocumentCategory.FINANCIAL,
            confidence=0.85
        )
    elif "contract" in text or "agreement" in text or "terms and conditions" in text:
        return DocumentClassification(
            doc_type=DocumentType.CONTRACT,
            category=DocumentCategory.LEGAL,
            confidence=0.80
        )
    elif "from:" in text and "to:" in text and "subject:" in text:
        return DocumentClassification(
            doc_type=DocumentType.EMAIL,
            category=DocumentCategory.COMMUNICATION,
            confidence=0.90
        )
    elif "memorandum" in text or "memo" in text:
        return DocumentClassification(
            doc_type=DocumentType.MEMO,
            category=DocumentCategory.COMMUNICATION,
            confidence=0.75
        )
    elif "receipt" in text or "paid" in text or "transaction" in text:
        return DocumentClassification(
            doc_type=DocumentType.RECEIPT,
            category=DocumentCategory.FINANCIAL,
            confidence=0.80
        )
    else:
        return DocumentClassification(
            doc_type=DocumentType.UNKNOWN,
            category=DocumentCategory.OTHER,
            confidence=0.5
        )
