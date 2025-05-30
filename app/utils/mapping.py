"""
helper, label↔️id-Mapping
"""

import logging
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

# Document type mappings
DOCUMENT_TYPE_MAPPINGS = {
    # Standard document types
    "email": "EMAIL_001",
    "invoice": "INVOICE_001",
    "contract": "CONTRACT_001",
    "report": "REPORT_001",
    "memo": "MEMO_001",
    "letter": "LETTER_001",
    "form": "FORM_001",
    "receipt": "RECEIPT_001",
    "statement": "STATEMENT_001",
    "proposal": "PROPOSAL_001",
    "presentation": "PRESENTATION_001",
    "spreadsheet": "SPREADSHEET_001",
    "unknown": "UNKNOWN_001",
    
    # Aliases and variations
    "e-mail": "EMAIL_001",
    "electronic_mail": "EMAIL_001",
    "bill": "INVOICE_001",
    "billing": "INVOICE_001",
    "agreement": "CONTRACT_001",
    "legal_document": "CONTRACT_001",
    "memorandum": "MEMO_001",
    "formal_letter": "LETTER_001",
    "application_form": "FORM_001",
    "payment_receipt": "RECEIPT_001",
    "account_statement": "STATEMENT_001",
    "business_proposal": "PROPOSAL_001",
    "slide_deck": "PRESENTATION_001",
    "excel_sheet": "SPREADSHEET_001"
}

# Event type mappings
EVENT_TYPE_MAPPINGS = {
    # Core event types
    "general": "EVENT_GEN_001",
    "billing": "EVENT_BILL_001",
    "legal": "EVENT_LEGAL_001",
    "communication": "EVENT_COMM_001",
    "transaction": "EVENT_TRANS_001",
    "compliance": "EVENT_COMP_001",
    "marketing": "EVENT_MARK_001",
    "support": "EVENT_SUPP_001",
    "internal": "EVENT_INT_001",
    "external": "EVENT_EXT_001",
    "urgent": "EVENT_URG_001",
    "routine": "EVENT_ROUT_001",
    "approval": "EVENT_APPR_001",
    "notification": "EVENT_NOTIF_001",
    "request": "EVENT_REQ_001",
    "unknown": "EVENT_UNK_001",
    
    # Aliases and variations
    "payment": "EVENT_BILL_001",
    "financial": "EVENT_BILL_001",
    "legal_matter": "EVENT_LEGAL_001",
    "correspondence": "EVENT_COMM_001",
    "purchase": "EVENT_TRANS_001",
    "sale": "EVENT_TRANS_001",
    "regulatory": "EVENT_COMP_001",
    "advertisement": "EVENT_MARK_001",
    "customer_service": "EVENT_SUPP_001",
    "help_desk": "EVENT_SUPP_001",
    "company_internal": "EVENT_INT_001",
    "third_party": "EVENT_EXT_001",
    "emergency": "EVENT_URG_001",
    "critical": "EVENT_URG_001",
    "standard": "EVENT_ROUT_001",
    "authorization": "EVENT_APPR_001",
    "alert": "EVENT_NOTIF_001",
    "information_request": "EVENT_REQ_001"
}

# Entity type mappings
ENTITY_TYPE_MAPPINGS = {
    # Person and organization
    "person": "ENT_PERSON_001",
    "organization": "ENT_ORG_001",
    "company": "ENT_ORG_001",
    "individual": "ENT_PERSON_001",
    
    # Contact information
    "email": "ENT_EMAIL_001",
    "phone": "ENT_PHONE_001",
    "address": "ENT_ADDRESS_001",
    "url": "ENT_URL_001",
    
    # Financial
    "amount": "ENT_AMOUNT_001",
    "currency": "ENT_CURRENCY_001",
    "account_number": "ENT_ACCOUNT_001",
    "invoice_number": "ENT_INVOICE_001",
    
    # Dates and times
    "date": "ENT_DATE_001",
    "time": "ENT_TIME_001",
    "datetime": "ENT_DATETIME_001",
    
    # Location
    "location": "ENT_LOCATION_001",
    "country": "ENT_COUNTRY_001",
    "city": "ENT_CITY_001",
    
    # Documents and references
    "document_id": "ENT_DOC_ID_001",
    "reference": "ENT_REF_001",
    "contract_id": "ENT_CONTRACT_001",
    
    # Other
    "product": "ENT_PRODUCT_001",
    "service": "ENT_SERVICE_001",
    "misc": "ENT_MISC_001",
    "unknown": "ENT_UNKNOWN_001"
}

def map_label_to_id(label: str, mapping_type: str = "document") -> str:
    """
    Map a human-readable label to an internal ID
    
    Args:
        label: The label to map
        mapping_type: Type of mapping ("document", "event", "entity")
        
    Returns:
        Internal ID string
    """
    if not label:
        return ""
    
    # Normalize label
    normalized_label = label.lower().strip().replace(" ", "_").replace("-", "_")
    
    # Select appropriate mapping
    if mapping_type == "document":
        mapping = DOCUMENT_TYPE_MAPPINGS
    elif mapping_type == "event":
        mapping = EVENT_TYPE_MAPPINGS
    elif mapping_type == "entity":
        mapping = ENTITY_TYPE_MAPPINGS
    else:
        logger.warning(f"Unknown mapping type: {mapping_type}")
        return f"UNKNOWN_{normalized_label.upper()}"
    
    # Get mapped ID
    mapped_id = mapping.get(normalized_label)
    
    if mapped_id:
        logger.debug(f"Mapped {label} -> {mapped_id}")
        return mapped_id
    else:
        # Generate a fallback ID
        fallback_id = f"CUSTOM_{normalized_label.upper()}_001"
        logger.warning(f"No mapping found for '{label}', using fallback: {fallback_id}")
        return fallback_id

def map_id_to_label(internal_id: str, mapping_type: str = "document") -> str:
    """
    Map an internal ID back to a human-readable label
    
    Args:
        internal_id: The internal ID to map
        mapping_type: Type of mapping ("document", "event", "entity")
        
    Returns:
        Human-readable label
    """
    if not internal_id:
        return ""
    
    # Select appropriate mapping
    if mapping_type == "document":
        mapping = DOCUMENT_TYPE_MAPPINGS
    elif mapping_type == "event":
        mapping = EVENT_TYPE_MAPPINGS
    elif mapping_type == "entity":
        mapping = ENTITY_TYPE_MAPPINGS
    else:
        logger.warning(f"Unknown mapping type: {mapping_type}")
        return internal_id
    
    # Reverse lookup
    for label, mapped_id in mapping.items():
        if mapped_id == internal_id:
            logger.debug(f"Reverse mapped {internal_id} -> {label}")
            return label.replace("_", " ").title()
    
    # Handle custom IDs
    if internal_id.startswith("CUSTOM_"):
        custom_label = internal_id.replace("CUSTOM_", "").replace("_001", "").replace("_", " ").lower()
        logger.warning(f"Custom ID reverse mapped: {internal_id} -> {custom_label}")
        return custom_label.title()
    
    logger.warning(f"No reverse mapping found for ID: {internal_id}")
    return internal_id

def get_all_mappings(mapping_type: str = "document") -> Dict[str, str]:
    """
    Get all mappings for a specific type
    
    Args:
        mapping_type: Type of mapping ("document", "event", "entity")
        
    Returns:
        Dictionary of label -> ID mappings
    """
    if mapping_type == "document":
        return DOCUMENT_TYPE_MAPPINGS.copy()
    elif mapping_type == "event":
        return EVENT_TYPE_MAPPINGS.copy()
    elif mapping_type == "entity":
        return ENTITY_TYPE_MAPPINGS.copy()
    else:
        logger.warning(f"Unknown mapping type: {mapping_type}")
        return {}

def find_similar_labels(label: str, mapping_type: str = "document", threshold: float = 0.6) -> List[Tuple[str, float]]:
    """
    Find similar labels using string similarity
    
    Args:
        label: Label to find similarities for
        mapping_type: Type of mapping to search in
        threshold: Minimum similarity threshold (0.0 to 1.0)
        
    Returns:
        List of (similar_label, similarity_score) tuples
    """
    from difflib import SequenceMatcher
    
    mappings = get_all_mappings(mapping_type)
    similarities = []
    
    normalized_input = label.lower().strip()
    
    for existing_label in mappings.keys():
        similarity = SequenceMatcher(None, normalized_input, existing_label).ratio()
        if similarity >= threshold:
            similarities.append((existing_label, similarity))
    
    # Sort by similarity score (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities

def add_custom_mapping(label: str, mapping_type: str = "document", custom_id: Optional[str] = None) -> str:
    """
    Add a custom mapping for a new label
    
    Args:
        label: New label to add
        mapping_type: Type of mapping to add to
        custom_id: Optional custom ID (will be generated if not provided)
        
    Returns:
        The ID assigned to the label
    """
    if not label:
        raise ValueError("Label cannot be empty")
    
    normalized_label = label.lower().strip().replace(" ", "_").replace("-", "_")
    
    # Select appropriate mapping
    if mapping_type == "document":
        mapping = DOCUMENT_TYPE_MAPPINGS
        prefix = "DOC"
    elif mapping_type == "event":
        mapping = EVENT_TYPE_MAPPINGS
        prefix = "EVENT"
    elif mapping_type == "entity":
        mapping = ENTITY_TYPE_MAPPINGS
        prefix = "ENT"
    else:
        raise ValueError(f"Unknown mapping type: {mapping_type}")
    
    # Check if label already exists
    if normalized_label in mapping:
        logger.info(f"Label '{label}' already exists with ID: {mapping[normalized_label]}")
        return mapping[normalized_label]
    
    # Generate custom ID if not provided
    if not custom_id:
        custom_id = f"CUSTOM_{prefix}_{normalized_label.upper()}_001"
    
    # Add to mapping
    mapping[normalized_label] = custom_id
    logger.info(f"Added custom mapping: {label} -> {custom_id}")
    
    return custom_id

def validate_mapping_consistency() -> Dict[str, List[str]]:
    """
    Validate mapping consistency and find potential issues
    
    Returns:
        Dictionary of issue_type -> list of issues
    """
    issues = {
        "duplicates": [],
        "missing_reverse": [],
        "invalid_ids": []
    }
    
    all_mappings = {
        "document": DOCUMENT_TYPE_MAPPINGS,
        "event": EVENT_TYPE_MAPPINGS,
        "entity": ENTITY_TYPE_MAPPINGS
    }
    
    for mapping_type, mappings in all_mappings.items():
        # Check for duplicate IDs
        id_counts = {}
        for label, mapped_id in mappings.items():
            if mapped_id in id_counts:
                id_counts[mapped_id].append(label)
            else:
                id_counts[mapped_id] = [label]
        
        for mapped_id, labels in id_counts.items():
            if len(labels) > 1:
                issues["duplicates"].append(f"{mapping_type}: ID {mapped_id} maps to {labels}")
        
        # Check for invalid ID formats
        for label, mapped_id in mappings.items():
            if not mapped_id or not isinstance(mapped_id, str):
                issues["invalid_ids"].append(f"{mapping_type}: Invalid ID for '{label}': {mapped_id}")
    
    return issues

def export_mappings_to_json() -> Dict[str, Any]:
    """
    Export all mappings to a JSON-serializable format
    
    Returns:
        Dictionary containing all mappings
    """
    return {
        "document_types": DOCUMENT_TYPE_MAPPINGS,
        "event_types": EVENT_TYPE_MAPPINGS,
        "entity_types": ENTITY_TYPE_MAPPINGS,
        "metadata": {
            "version": "1.0",
            "total_mappings": (
                len(DOCUMENT_TYPE_MAPPINGS) + 
                len(EVENT_TYPE_MAPPINGS) + 
                len(ENTITY_TYPE_MAPPINGS)
            )
        }
    }

def import_mappings_from_json(data: Dict[str, Any]) -> bool:
    """
    Import mappings from JSON data
    
    Args:
        data: Dictionary containing mapping data
        
    Returns:
        True if successful, False otherwise
    """
    try:
        global DOCUMENT_TYPE_MAPPINGS, EVENT_TYPE_MAPPINGS, ENTITY_TYPE_MAPPINGS
        
        if "document_types" in data:
            DOCUMENT_TYPE_MAPPINGS.update(data["document_types"])
        
        if "event_types" in data:
            EVENT_TYPE_MAPPINGS.update(data["event_types"])
        
        if "entity_types" in data:
            ENTITY_TYPE_MAPPINGS.update(data["entity_types"])
        
        logger.info("Successfully imported mappings from JSON")
        return True
        
    except Exception as e:
        logger.error(f"Failed to import mappings: {e}")
        return False
