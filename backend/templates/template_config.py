"""
Document Template Configuration
Defines required and optional fields for each document template
"""

from typing import Dict, List, Any
from enum import Enum


class FieldType(str, Enum):
    """Field data types"""
    TEXT = "text"
    EMAIL = "email"
    PHONE = "phone"
    DATE = "date"
    TEXTAREA = "textarea"
    BOOLEAN = "boolean"
    LIST = "list"


class DocumentType(str, Enum):
    """Available document types"""
    LEGAL_LETTER = "legal_letter"
    RTI_APPLICATION = "rti_application"
    COUNTER_PETITION = "counter_petition"


class TemplateField:
    """Template field definition"""
    def __init__(
        self,
        name: str,
        label: str,
        field_type: FieldType,
        required: bool = True,
        description: str = "",
        placeholder: str = "",
        validation: Dict[str, Any] = None
    ):
        self.name = name
        self.label = label
        self.field_type = field_type
        self.required = required
        self.description = description
        self.placeholder = placeholder
        self.validation = validation or {}


# Legal Letter Template Configuration
LEGAL_LETTER_FIELDS = [
    TemplateField(
        name="sender_name",
        label="Your Full Name",
        field_type=FieldType.TEXT,
        required=True,
        description="Your complete legal name as it appears on official documents",
        placeholder="e.g., Rajesh Kumar Sharma"
    ),
    TemplateField(
        name="sender_address",
        label="Your Complete Address",
        field_type=FieldType.TEXTAREA,
        required=True,
        description="Your full postal address including city, state, and PIN code",
        placeholder="e.g., 123, MG Road, Bangalore, Karnataka - 560001"
    ),
    TemplateField(
        name="sender_phone",
        label="Your Phone Number",
        field_type=FieldType.PHONE,
        required=True,
        description="Your contact phone number with country code",
        placeholder="e.g., +91-9876543210",
        validation={"pattern": r"^\+?[\d\s\-()]+$"}
    ),
    TemplateField(
        name="sender_email",
        label="Your Email Address",
        field_type=FieldType.EMAIL,
        required=True,
        description="Your email address for correspondence",
        placeholder="e.g., rajesh.sharma@email.com"
    ),
    TemplateField(
        name="recipient_name",
        label="Recipient's Name",
        field_type=FieldType.TEXT,
        required=True,
        description="Full name of the person/authority you are addressing",
        placeholder="e.g., Dr. Priya Mehta"
    ),
    TemplateField(
        name="recipient_designation",
        label="Recipient's Designation",
        field_type=FieldType.TEXT,
        required=True,
        description="Official designation or title of the recipient",
        placeholder="e.g., Principal, ABC College"
    ),
    TemplateField(
        name="recipient_address",
        label="Recipient's Address",
        field_type=FieldType.TEXTAREA,
        required=True,
        description="Complete address of the recipient",
        placeholder="e.g., ABC College, College Road, Mumbai, Maharashtra - 400001"
    ),
    TemplateField(
        name="subject",
        label="Subject of Letter",
        field_type=FieldType.TEXT,
        required=True,
        description="Brief subject line describing the purpose of the letter",
        placeholder="e.g., Complaint regarding false allegations and harassment"
    ),
    TemplateField(
        name="incident_date",
        label="Date of Incident",
        field_type=FieldType.DATE,
        required=True,
        description="Date when the incident occurred",
        placeholder="e.g., 15th January 2024"
    ),
    TemplateField(
        name="incident_description",
        label="Description of Incident",
     