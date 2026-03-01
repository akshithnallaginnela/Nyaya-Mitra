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
        field_type=FieldType.TEXTAREA,
        required=True,
        description="Detailed description of what happened, including dates, times, and witnesses if any",
        placeholder="e.g., On 15th January 2024, I was falsely accused by..."
    ),
    TemplateField(
        name="legal_grounds",
        label="Legal Grounds/Applicable Laws",
        field_type=FieldType.TEXTAREA,
        required=True,
        description="Relevant legal provisions, sections, or laws that apply to your case",
        placeholder="e.g., Section 499 IPC (Defamation), Article 21 of Constitution (Right to Life and Personal Liberty)"
    ),
    TemplateField(
        name="demands",
        label="Your Demands/Requests",
        field_type=FieldType.TEXTAREA,
        required=True,
        description="What you want the recipient to do - apology, withdrawal of complaint, compensation, etc.",
        placeholder="e.g., 1. Immediate withdrawal of false allegations\n2. Written apology\n3. Compensation for mental harassment"
    ),
    TemplateField(
        name="date",
        label="Letter Date",
        field_type=FieldType.DATE,
        required=False,
        description="Date of the letter (will use current date if not provided)",
        placeholder="e.g., 20th January 2024"
    ),
    TemplateField(
        name="reference_number",
        label="Reference Number",
        field_type=FieldType.TEXT,
        required=False,
        description="Any reference number if this is in response to a previous communication",
        placeholder="e.g., Ref: ABC/2024/123"
    ),
    TemplateField(
        name="timeline",
        label="Timeline for Response",
        field_type=FieldType.TEXT,
        required=False,
        description="Time period within which you expect a response (default: 15 days)",
        placeholder="e.g., 15 days, 7 days, 30 days"
    ),
    TemplateField(
        name="consequences",
        label="Consequences of Non-Compliance",
        field_type=FieldType.TEXT,
        required=False,
        description="What action you will take if no response is received (default: appropriate legal action)",
        placeholder="e.g., file a police complaint, approach consumer court, file defamation case"
    ),
    TemplateField(
        name="attachments",
        label="List of Attachments",
        field_type=FieldType.LIST,
        required=False,
        description="List of documents you are attaching with this letter",
        placeholder="e.g., Copy of ID proof, Screenshots of messages, Witness statements"
    )
]


# RTI Application Template Configuration
RTI_APPLICATION_FIELDS = [
    TemplateField(
        name="applicant_name",
        label="Your Full Name",
        field_type=FieldType.TEXT,
        required=True,
        description="Your complete legal name as it appears on official documents",
        placeholder="e.g., Priya Sharma"
    ),
    TemplateField(
        name="applicant_address",
        label="Your Complete Address",
        field_type=FieldType.TEXTAREA,
        required=True,
        description="Your full postal address including city, state, and PIN code",
        placeholder="e.g., 456, Park Street, Kolkata, West Bengal - 700016"
    ),
    TemplateField(
        name="applicant_phone",
        label="Your Phone Number",
        field_type=FieldType.PHONE,
        required=True,
        description="Your contact phone number with country code",
        placeholder="e.g., +91-9876543210",
        validation={"pattern": r"^\+?[\d\s\-()]+$"}
    ),
    TemplateField(
        name="applicant_email",
        label="Your Email Address",
        field_type=FieldType.EMAIL,
        required=True,
        description="Your email address for correspondence",
        placeholder="e.g., priya.sharma@email.com"
    ),
    TemplateField(
        name="department_name",
        label="Department/Office Name",
        field_type=FieldType.TEXT,
        required=True,
        description="Name of the government department or public authority",
        placeholder="e.g., Delhi Police, Ministry of Education, Municipal Corporation"
    ),
    TemplateField(
        name="department_address",
        label="Department Address",
        field_type=FieldType.TEXTAREA,
        required=True,
        description="Complete address of the department/office",
        placeholder="e.g., Police Headquarters, ITO, New Delhi - 110002"
    ),
    TemplateField(
        name="information_sought",
        label="Information Requested",
        field_type=FieldType.TEXTAREA,
        required=True,
        description="Detailed description of the information you are seeking. Be specific and clear.",
        placeholder="e.g., 1. Copy of FIR No. 123/2024 registered at XYZ Police Station\n2. Status of investigation in the said FIR\n3. Names of investigating officers"
    ),
    TemplateField(
        name="period_of_information",
        label="Time Period of Information",
        field_type=FieldType.TEXT,
        required=True,
        description="The time period for which you need the information",
        placeholder="e.g., January 2024 to March 2024, Last 6 months, Financial Year 2023-24"
    ),
    TemplateField(
        name="date",
        label="Application Date",
        field_type=FieldType.DATE,
        required=False,
        description="Date of the application (will use current date if not provided)",
        placeholder="e.g., 20th January 2024"
    ),
    TemplateField(
        name="pio_name",
        label="Public Information Officer Name",
        field_type=FieldType.TEXT,
        required=False,
        description="Name of the PIO if known (default: The Public Information Officer)",
        placeholder="e.g., Shri Rajesh Kumar, PIO"
    ),
    TemplateField(
        name="purpose",
        label="Purpose of Information",
        field_type=FieldType.TEXTAREA,
        required=False,
        description="Purpose for which information is sought (optional - not mandatory under RTI Act)",
        placeholder="e.g., To understand the status of my complaint"
    ),
    TemplateField(
        name="preferred_format",
        label="Preferred Format",
        field_type=FieldType.TEXT,
        required=False,
        description="How you want to receive the information (default: Photocopies)",
        placeholder="e.g., Photocopies, Certified Copies, Email, Inspection of Records"
    ),
    TemplateField(
        name="bpl_status",
        label="Below Poverty Line (BPL) Status",
        field_type=FieldType.BOOLEAN,
        required=False,
        description="Check if you belong to BPL category and are exempt from fee",
        placeholder="Yes/No"
    ),
    TemplateField(
        name="application_fee",
        label="Application Fee Amount",
        field_type=FieldType.TEXT,
        required=False,
        description="Fee amount being paid (default: ₹10 for Central Govt, varies for State Govt)",
        placeholder="e.g., ₹10"
    ),
    TemplateField(
        name="attachments",
        label="List of Attachments",
        field_type=FieldType.LIST,
        required=False,
        description="List of documents you are attaching with this application",
        placeholder="e.g., Fee payment receipt, BPL certificate (if applicable)"
    )
]


# Counter-Petition Template Configuration
COUNTER_PETITION_FIELDS = [
    TemplateField(
        name="respondent_name",
        label="Your Full Name (Respondent)",
        field_type=FieldType.TEXT,
        required=True,
        description="Your complete legal name as respondent in the case",
        placeholder="e.g., Amit Kumar Singh"
    ),
    TemplateField(
        name="respondent_address",
        label="Your Complete Address",
        field_type=FieldType.TEXTAREA,
        required=True,
        description="Your full postal address including city, state, and PIN code",
        placeholder="e.g., 789, Civil Lines, Lucknow, Uttar Pradesh - 226001"
    ),
    TemplateField(
        name="respondent_phone",
        label="Your Phone Number",
        field_type=FieldType.PHONE,
        required=True,
        description="Your contact phone number with country code",
        placeholder="e.g., +91-9876543210",
        validation={"pattern": r"^\+?[\d\s\-()]+$"}
    ),
    TemplateField(
        name="respondent_email",
        label="Your Email Address",
        field_type=FieldType.EMAIL,
        required=True,
        description="Your email address for correspondence",
        placeholder="e.g., amit.singh@email.com"
    ),
    TemplateField(
        name="court_name",
        label="Name of Court",
        field_type=FieldType.TEXT,
        required=True,
        description="Full name of the court where the case is filed",
        placeholder="e.g., District Court, Lucknow / High Court of Judicature at Allahabad"
    ),
    TemplateField(
        name="case_number",
        label="Case Number",
        field_type=FieldType.TEXT,
        required=True,
        description="Case number assigned by the court",
        placeholder="e.g., 123"
    ),
    TemplateField(
        name="case_year",
        label="Case Year",
        field_type=FieldType.TEXT,
        required=True,
        description="Year in which the case was filed",
        placeholder="e.g., 2024"
    ),
    TemplateField(
        name="petitioner_name",
        label="Petitioner's Name",
        field_type=FieldType.TEXT,
        required=True,
        description="Full name of the original petitioner",
        placeholder="e.g., Smt. Neha Verma"
    ),
    TemplateField(
        name="case_type",
        label="Type of Case",
        field_type=FieldType.TEXT,
        required=True,
        description="Type of legal case (Civil Suit, Criminal Complaint, Writ Petition, etc.)",
        placeholder="e.g., Civil Suit, Criminal Complaint, Writ Petition"
    ),
    TemplateField(
        name="original_petition_date",
        label="Date of Original Petition",
        field_type=FieldType.DATE,
        required=True,
        description="Date when the original petition was filed",
        placeholder="e.g., 10th January 2024"
    ),
    TemplateField(
        name="facts_of_case",
        label="Facts as per Original Petition",
        field_type=FieldType.TEXTAREA,
        required=True,
        description="Summary of facts as stated in the original petition filed against you",
        placeholder="e.g., The petitioner has alleged that on 5th January 2024..."
    ),
    TemplateField(
        name="counter_facts",
        label="Your Version of Facts",
        field_type=FieldType.TEXTAREA,
        required=True,
        description="Your true version of the facts, countering the allegations",
        placeholder="e.g., The allegations made by the petitioner are completely false. The truth is that..."
    ),
    TemplateField(
        name="legal_objections",
        label="Legal Objections",
        field_type=FieldType.TEXTAREA,
        required=True,
        description="Your legal objections to the petition - why it should be dismissed",
        placeholder="e.g., 1. The petition is barred by limitation\n2. The court lacks jurisdiction\n3. No cause of action exists"
    ),
    TemplateField(
        name="evidence_list",
        label="List of Evidence",
        field_type=FieldType.TEXTAREA,
        required=True,
        description="List of evidence and documents you are relying on",
        placeholder="e.g., 1. Email correspondence dated...\n2. Witness statement of...\n3. CCTV footage showing..."
    ),
    TemplateField(
        name="prayer_relief",
        label="Relief Sought",
        field_type=FieldType.TEXTAREA,
        required=True,
        description="What relief you are seeking from the court",
        placeholder="e.g., Declare the allegations as false and malicious; Award compensation for harassment"
    ),
    TemplateField(
        name="date",
        label="Counter-Petition Date",
        field_type=FieldType.DATE,
        required=False,
        description="Date of filing the counter-petition (will use current date if not provided)",
        placeholder="e.g., 25th January 2024"
    ),
    TemplateField(
        name="advocate_name",
        label="Advocate's Name",
        field_type=FieldType.TEXT,
        required=False,
        description="Name of your advocate/lawyer (if represented)",
        placeholder="e.g., Adv. Ramesh Chandra"
    ),
    TemplateField(
        name="advocate_enrollment",
        label="Advocate's Enrollment Number",
        field_type=FieldType.TEXT,
        required=False,
        description="Bar Council enrollment number of your advocate",
        placeholder="e.g., UP/12345/2010"
    ),
    TemplateField(
        name="attachments",
        label="List of Annexures",
        field_type=FieldType.LIST,
        required=False,
        description="List of documents being annexed with the counter-petition",
        placeholder="e.g., Email correspondence, Witness affidavits, Documentary evidence"
    )
]


# Template Registry
TEMPLATE_REGISTRY = {
    DocumentType.LEGAL_LETTER: {
        "name": "Legal Letter",
        "description": "Formal legal letter for complaints, demands, or legal notices",
        "template_file": "legal_letter.j2",
        "fields": LEGAL_LETTER_FIELDS,
        "category": "correspondence"
    },
    DocumentType.RTI_APPLICATION: {
        "name": "RTI Application",
        "description": "Right to Information application under RTI Act, 2005",
        "template_file": "rti_application.j2",
        "fields": RTI_APPLICATION_FIELDS,
        "category": "government"
    },
    DocumentType.COUNTER_PETITION: {
        "name": "Counter-Petition / Reply",
        "description": "Counter-petition or reply to be filed in court in response to a petition",
        "template_file": "counter_petition.j2",
        "fields": COUNTER_PETITION_FIELDS,
        "category": "court"
    }
}


def get_template_config(document_type: DocumentType) -> Dict[str, Any]:
    """
    Get template configuration for a specific document type
    
    Args:
        document_type: Type of document template
        
    Returns:
        Dictionary containing template configuration
    """
    return TEMPLATE_REGISTRY.get(document_type)


def get_required_fields(document_type: DocumentType) -> List[TemplateField]:
    """
    Get list of required fields for a document type
    
    Args:
        document_type: Type of document template
        
    Returns:
        List of required TemplateField objects
    """
    config = get_template_config(document_type)
    if not config:
        return []
    return [field for field in config["fields"] if field.required]


def get_optional_fields(document_type: DocumentType) -> List[TemplateField]:
    """
    Get list of optional fields for a document type
    
    Args:
        document_type: Type of document template
        
    Returns:
        List of optional TemplateField objects
    """
    config = get_template_config(document_type)
    if not config:
        return []
    return [field for field in config["fields"] if not field.required]


def get_all_fields(document_type: DocumentType) -> List[TemplateField]:
    """
    Get all fields (required + optional) for a document type
    
    Args:
        document_type: Type of document template
        
    Returns:
        List of all TemplateField objects
    """
    config = get_template_config(document_type)
    if not config:
        return []
    return config["fields"]


def validate_template_inputs(document_type: DocumentType, inputs: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate user inputs against template requirements
    
    Args:
        document_type: Type of document template
        inputs: Dictionary of user-provided inputs
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    required_fields = get_required_fields(document_type)
    
    # Check for missing required fields
    for field in required_fields:
        if field.name not in inputs or not inputs[field.name]:
            errors.append(f"Required field '{field.label}' is missing")
    
    # Validate field types and patterns
    all_fields = get_all_fields(document_type)
    for field in all_fields:
        if field.name in inputs and inputs[field.name]:
            value = inputs[field.name]
            
            # Email validation
            if field.field_type == FieldType.EMAIL:
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, value):
                    errors.append(f"Invalid email format for '{field.label}'")
            
            # Phone validation
            if field.field_type == FieldType.PHONE and field.validation.get("pattern"):
                import re
                if not re.match(field.validation["pattern"], value):
                    errors.append(f"Invalid phone format for '{field.label}'")
            
            # List validation
            if field.field_type == FieldType.LIST and not isinstance(value, list):
                errors.append(f"Field '{field.label}' must be a list")
    
    return (len(errors) == 0, errors)