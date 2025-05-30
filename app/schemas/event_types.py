"""
Event type schemas and classifications
Generated from eventTypes.json schema
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class EventType(str, Enum):
    """Enumeration of supported event types"""
    GENERAL = "general"
    BILLING = "billing"
    LEGAL = "legal"
    COMMUNICATION = "communication"
    TRANSACTION = "transaction"
    COMPLIANCE = "compliance"
    MARKETING = "marketing"
    SUPPORT = "support"
    INTERNAL = "internal"
    EXTERNAL = "external"
    URGENT = "urgent"
    ROUTINE = "routine"
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    REQUEST = "request"
    UNKNOWN = "unknown"

class EventTypeInfo(BaseModel):
    """Information about an event type"""
    type_id: str = Field(description="Event type identifier")
    name: str = Field(description="Human-readable type name")
    description: str = Field(description="Type description")
    priority: str = Field(description="Event priority level")
    category: str = Field(description="Event category")
    processing_sla: Optional[int] = Field(None, description="SLA in minutes")
    
class EventPriority(str, Enum):
    """Event priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EventCategory(str, Enum):
    """Event categories for grouping"""
    BUSINESS = "business"
    OPERATIONAL = "operational"
    TECHNICAL = "technical"
    ADMINISTRATIVE = "administrative"
    CUSTOMER = "customer"
    FINANCIAL = "financial"
    REGULATORY = "regulatory"
    OTHER = "other"

class EventClassification(BaseModel):
    """Event classification result"""
    event_type: EventType = Field(description="Classified event type")
    priority: EventPriority = Field(description="Event priority")
    category: EventCategory = Field(description="Event category")
    confidence: float = Field(ge=0.0, le=1.0, description="Classification confidence")
    urgency_score: float = Field(ge=0.0, le=1.0, description="Urgency score")
    keywords: List[str] = Field(default_factory=list, description="Keywords that influenced classification")

# Event type definitions with metadata
EVENT_TYPES = {
    EventType.GENERAL: EventTypeInfo(
        type_id="general",
        name="General",
        description="General purpose event",
        priority=EventPriority.MEDIUM.value,
        category=EventCategory.OTHER.value,
        processing_sla=60
    ),
    EventType.BILLING: EventTypeInfo(
        type_id="billing",
        name="Billing",
        description="Billing and payment related event",
        priority=EventPriority.HIGH.value,
        category=EventCategory.FINANCIAL.value,
        processing_sla=30
    ),
    EventType.LEGAL: EventTypeInfo(
        type_id="legal",
        name="Legal",
        description="Legal document or compliance event",
        priority=EventPriority.HIGH.value,
        category=EventCategory.REGULATORY.value,
        processing_sla=15
    ),
    EventType.COMMUNICATION: EventTypeInfo(
        type_id="communication",
        name="Communication",
        description="Communication or correspondence event",
        priority=EventPriority.MEDIUM.value,
        category=EventCategory.BUSINESS.value,
        processing_sla=120
    ),
    EventType.TRANSACTION: EventTypeInfo(
        type_id="transaction",
        name="Transaction",
        description="Financial transaction event",
        priority=EventPriority.HIGH.value,
        category=EventCategory.FINANCIAL.value,
        processing_sla=15
    ),
    EventType.COMPLIANCE: EventTypeInfo(
        type_id="compliance",
        name="Compliance",
        description="Regulatory compliance event",
        priority=EventPriority.CRITICAL.value,
        category=EventCategory.REGULATORY.value,
        processing_sla=10
    ),
    EventType.MARKETING: EventTypeInfo(
        type_id="marketing",
        name="Marketing",
        description="Marketing and promotional event",
        priority=EventPriority.LOW.value,
        category=EventCategory.BUSINESS.value,
        processing_sla=240
    ),
    EventType.SUPPORT: EventTypeInfo(
        type_id="support",
        name="Support",
        description="Customer support event",
        priority=EventPriority.MEDIUM.value,
        category=EventCategory.CUSTOMER.value,
        processing_sla=60
    ),
    EventType.INTERNAL: EventTypeInfo(
        type_id="internal",
        name="Internal",
        description="Internal company event",
        priority=EventPriority.MEDIUM.value,
        category=EventCategory.ADMINISTRATIVE.value,
        processing_sla=120
    ),
    EventType.EXTERNAL: EventTypeInfo(
        type_id="external",
        name="External",
        description="External stakeholder event",
        priority=EventPriority.MEDIUM.value,
        category=EventCategory.BUSINESS.value,
        processing_sla=60
    ),
    EventType.URGENT: EventTypeInfo(
        type_id="urgent",
        name="Urgent",
        description="Time-sensitive urgent event",
        priority=EventPriority.CRITICAL.value,
        category=EventCategory.OPERATIONAL.value,
        processing_sla=5
    ),
    EventType.ROUTINE: EventTypeInfo(
        type_id="routine",
        name="Routine",
        description="Regular routine event",
        priority=EventPriority.LOW.value,
        category=EventCategory.OPERATIONAL.value,
        processing_sla=480
    ),
    EventType.APPROVAL: EventTypeInfo(
        type_id="approval",
        name="Approval",
        description="Approval request event",
        priority=EventPriority.HIGH.value,
        category=EventCategory.ADMINISTRATIVE.value,
        processing_sla=30
    ),
    EventType.NOTIFICATION: EventTypeInfo(
        type_id="notification",
        name="Notification",
        description="Information notification event",
        priority=EventPriority.LOW.value,
        category=EventCategory.OPERATIONAL.value,
        processing_sla=240
    ),
    EventType.REQUEST: EventTypeInfo(
        type_id="request",
        name="Request",
        description="Service or information request",
        priority=EventPriority.MEDIUM.value,
        category=EventCategory.BUSINESS.value,
        processing_sla=120
    ),
    EventType.UNKNOWN: EventTypeInfo(
        type_id="unknown",
        name="Unknown",
        description="Unclassified event type",
        priority=EventPriority.MEDIUM.value,
        category=EventCategory.OTHER.value,
        processing_sla=60
    )
}

def get_event_type_info(event_type: EventType) -> EventTypeInfo:
    """Get information for an event type"""
    return EVENT_TYPES.get(event_type, EVENT_TYPES[EventType.UNKNOWN])

def get_types_by_priority(priority: EventPriority) -> List[EventType]:
    """Get all event types with a specific priority"""
    return [
        event_type for event_type, info in EVENT_TYPES.items()
        if info.priority == priority.value
    ]

def get_types_by_category(category: EventCategory) -> List[EventType]:
    """Get all event types in a category"""
    return [
        event_type for event_type, info in EVENT_TYPES.items()
        if info.category == category.value
    ]

def classify_event_type(features: Dict[str, Any]) -> EventClassification:
    """
    Simple rule-based event type classification
    This would be replaced with ML model predictions in production
    """
    text = features.get("text", "").lower()
    urgency_keywords = ["urgent", "asap", "immediately", "critical", "emergency"]
    
    urgency_score = 0.0
    keywords = []
    
    # Calculate urgency score
    for keyword in urgency_keywords:
        if keyword in text:
            urgency_score += 0.2
            keywords.append(keyword)
    
    urgency_score = min(urgency_score, 1.0)
    
    # Classification logic
    if "invoice" in text or "payment" in text or "bill" in text:
        return EventClassification(
            event_type=EventType.BILLING,
            priority=EventPriority.HIGH,
            category=EventCategory.FINANCIAL,
            confidence=0.85,
            urgency_score=urgency_score,
            keywords=keywords + ["billing", "payment"]
        )
    elif "contract" in text or "legal" in text or "compliance" in text:
        return EventClassification(
            event_type=EventType.LEGAL,
            priority=EventPriority.HIGH,
            category=EventCategory.REGULATORY,
            confidence=0.80,
            urgency_score=urgency_score,
            keywords=keywords + ["legal", "compliance"]
        )
    elif "email" in text or "message" in text or "communication" in text:
        return EventClassification(
            event_type=EventType.COMMUNICATION,
            priority=EventPriority.MEDIUM,
            category=EventCategory.BUSINESS,
            confidence=0.75,
            urgency_score=urgency_score,
            keywords=keywords + ["communication"]
        )
    elif "transaction" in text or "purchase" in text or "sale" in text:
        return EventClassification(
            event_type=EventType.TRANSACTION,
            priority=EventPriority.HIGH,
            category=EventCategory.FINANCIAL,
            confidence=0.80,
            urgency_score=urgency_score,
            keywords=keywords + ["transaction"]
        )
    elif "support" in text or "help" in text or "issue" in text:
        return EventClassification(
            event_type=EventType.SUPPORT,
            priority=EventPriority.MEDIUM,
            category=EventCategory.CUSTOMER,
            confidence=0.75,
            urgency_score=urgency_score,
            keywords=keywords + ["support", "help"]
        )
    elif "approval" in text or "authorize" in text or "approve" in text:
        return EventClassification(
            event_type=EventType.APPROVAL,
            priority=EventPriority.HIGH,
            category=EventCategory.ADMINISTRATIVE,
            confidence=0.80,
            urgency_score=urgency_score,
            keywords=keywords + ["approval"]
        )
    elif urgency_score > 0.4:
        return EventClassification(
            event_type=EventType.URGENT,
            priority=EventPriority.CRITICAL,
            category=EventCategory.OPERATIONAL,
            confidence=0.70,
            urgency_score=urgency_score,
            keywords=keywords
        )
    else:
        return EventClassification(
            event_type=EventType.GENERAL,
            priority=EventPriority.MEDIUM,
            category=EventCategory.OTHER,
            confidence=0.60,
            urgency_score=urgency_score,
            keywords=keywords
        )
