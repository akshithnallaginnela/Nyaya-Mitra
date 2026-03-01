"""
Attachment Checklist Generator
Defines attachment requirements for each document type and generates checklists
"""

from typing import Dict, List, Any
from templates.template_config import DocumentType


class AttachmentItem:
    """Represents a single attachment item in the checklist"""
    
    def __init__(
        self,
        name: str,
        description: str,
        required: bool = True,
        condition: str = None
    ):
        self.name = name
        self.description = description
        self.required = required
        self.condition = condition  # Condition under which this attachment is needed


# Attachment requirements for Legal Letter
LEGAL_LETTER_ATTACHMENTS = [
    AttachmentItem(
        name="Copy of Identity Proof",
        description="Photocopy of Aadhaar Card, PAN Card, or Passport",
        required=True
    ),
    AttachmentItem(
        name="Address Proof",
        description="Utility bill, bank statement, or rental agreement showing current address",
        required=True
    ),
    AttachmentItem(
        name="Evidence of Incident",
        description="Screenshots, photographs, or documents related to the incident",
        required=True
    ),
    AttachmentItem(
        name="Previous Correspondence",
        description="Copies of any previous letters, emails, or communications related to this matter",
        required=False,
        condition="reference_number"
    ),
    AttachmentItem(
        name="Witness Statements",
        description="Written statements from witnesses (if any)",
        required=False
    ),
    AttachmentItem(
        name="Medical Records",
        description="Medical certificates or reports (if applicable to your case)",
        required=False
    ),
    AttachmentItem(
        name="Police Complaint Copy",
        description="Copy of FIR or police complaint (if filed)",
        required=False
    )
]


# Attachment requirements for RTI Application
RTI_APPLICATION_ATTACHMENTS = [
    AttachmentItem(
        name="Application Fee Payment Receipt",
        description="Demand Draft, IPO, or online payment receipt for ₹10 (or applicable state fee)",
        required=True,
        condition="not_bpl"
    ),
    AttachmentItem(
        name="BPL Certificate",
        description="Valid Below Poverty Line certificate issued by competent authority",
        required=True,
        condition="bpl_status"
    ),
    AttachmentItem(
        name="Copy of Identity Proof",
        description="Photocopy of Aadhaar Card, PAN Card, Voter ID, or Passport",
        required=True
    ),
    AttachmentItem(
        name="Address Proof",
        description="Utility bill, bank statement, or Aadhaar card showing current address",
        required=True
    ),
    AttachmentItem(
        name="Self-Attested Copy of Previous RTI Application",
        description="If this is a first appeal or follow-up application",
        required=False
    ),
    AttachmentItem(
        name="Proof of Relationship",
        description="If seeking information on behalf of another person (legal heir, guardian, etc.)",
        required=False
    )
]


# Attachment requirements for Counter-Petition
COUNTER_PETITION_ATTACHMENTS = [
    AttachmentItem(
        name="Copy of Original Petition",
        description="Certified copy of the petition filed against you",
        required=True
    ),
    AttachmentItem(
        name="Court Notice/Summons",
        description="Copy of the court notice or summons received",
        required=True
    ),
    AttachmentItem(
        name="Identity Proof",
        description="Photocopy of Aadhaar Card, PAN Card, or Passport",
        required=True
    ),
    AttachmentItem(
        name="Address Proof",
        description="Utility bill, bank statement, or rental agreement",
        required=True
    ),
    AttachmentItem(
        name="Documentary Evidence",
        description="All documents supporting your version of facts (emails, contracts, receipts, etc.)",
        required=True
    ),
    AttachmentItem(
        name="Witness Affidavits",
        description="Sworn affidavits from witnesses supporting your case",
        required=False
    ),
    AttachmentItem(
        name="Expert Reports",
        description="Technical, medical, or forensic reports (if applicable)",
        required=False
    ),
    AttachmentItem(
        name="Vakalatnama",
        description="Power of attorney authorizing your advocate to represent you",
        required=False,
        condition="advocate_name"
    ),
    AttachmentItem(
        name="Court Fee Receipt",
        description="Receipt of court fee payment as per applicable rules",
        required=True
    ),
    AttachmentItem(
        name="Previous Court Orders",
        description="Copies of any previous orders in the same case (if applicable)",
        required=False
    )
]


# Registry mapping document types to their attachment requirements
ATTACHMENT_REGISTRY = {
    DocumentType.LEGAL_LETTER: LEGAL_LETTER_ATTACHMENTS,
    DocumentType.RTI_APPLICATION: RTI_APPLICATION_ATTACHMENTS,
    DocumentType.COUNTER_PETITION: COUNTER_PETITION_ATTACHMENTS
}


def get_attachment_checklist(
    document_type: DocumentType,
    user_inputs: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """
    Generate attachment checklist based on document type and user inputs
    
    Args:
        document_type: Type of document being generated
        user_inputs: Dictionary of user-provided inputs (used to determine conditional attachments)
        
    Returns:
        List of attachment items with their details
    """
    if document_type not in ATTACHMENT_REGISTRY:
        return []
    
    attachments = ATTACHMENT_REGISTRY[document_type]
    checklist = []
    user_inputs = user_inputs or {}
    
    for attachment in attachments:
        # Check if conditional attachment should be included
        if attachment.condition:
            # Handle special conditions
            if attachment.condition == "not_bpl":
                # Include if NOT BPL status
                if user_inputs.get("bpl_status", False):
                    continue
            elif attachment.condition == "bpl_status":
                # Include only if BPL status is True
                if not user_inputs.get("bpl_status", False):
                    continue
            else:
                # For other conditions, check if the field exists and has a value
                if attachment.condition not in user_inputs or not user_inputs[attachment.condition]:
                    continue
        
        checklist.append({
            "name": attachment.name,
            "description": attachment.description,
            "required": attachment.required,
            "status": "pending"  # Can be: pending, attached, not_applicable
        })
    
    return checklist


def format_checklist_for_document(checklist: List[Dict[str, Any]]) -> str:
    """
    Format checklist as text for inclusion in generated document
    
    Args:
        checklist: List of attachment items
        
    Returns:
        Formatted text string for document inclusion
    """
    if not checklist:
        return "[NO ATTACHMENTS REQUIRED]"
    
    lines = []
    lines.append("ATTACHMENT CHECKLIST")
    lines.append("=" * 50)
    lines.append("")
    lines.append("Please ensure the following documents are attached:")
    lines.append("")
    
    # Group by required/optional
    required_items = [item for item in checklist if item["required"]]
    optional_items = [item for item in checklist if not item["required"]]
    
    if required_items:
        lines.append("REQUIRED ATTACHMENTS:")
        for idx, item in enumerate(required_items, 1):
            lines.append(f"{idx}. {item['name']}")
            lines.append(f"   {item['description']}")
            lines.append(f"   [ ] Attached")
            lines.append("")
    
    if optional_items:
        lines.append("OPTIONAL ATTACHMENTS (if applicable):")
        for idx, item in enumerate(optional_items, 1):
            lines.append(f"{idx}. {item['name']}")
            lines.append(f"   {item['description']}")
            lines.append(f"   [ ] Attached / [ ] Not Applicable")
            lines.append("")
    
    lines.append("=" * 50)
    lines.append("")
    lines.append("NOTE: Please tick the boxes above as you attach each document.")
    lines.append("Keep copies of all attachments for your records.")
    
    return "\n".join(lines)


def get_attachment_summary(document_type: DocumentType) -> Dict[str, Any]:
    """
    Get summary of attachment requirements for a document type
    
    Args:
        document_type: Type of document
        
    Returns:
        Dictionary with summary information
    """
    if document_type not in ATTACHMENT_REGISTRY:
        return {
            "total_attachments": 0,
            "required_count": 0,
            "optional_count": 0,
            "attachments": []
        }
    
    attachments = ATTACHMENT_REGISTRY[document_type]
    required_count = sum(1 for att in attachments if att.required)
    optional_count = len(attachments) - required_count
    
    return {
        "total_attachments": len(attachments),
        "required_count": required_count,
        "optional_count": optional_count,
        "attachments": [
            {
                "name": att.name,
                "description": att.description,
                "required": att.required
            }
            for att in attachments
        ]
    }
