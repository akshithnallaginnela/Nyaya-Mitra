"""
Evidence Guide Generator
Generates customized evidence guides based on case type with step-by-step instructions,
visual aid references, and evidence type checklists.

Requirements: 7.4, 7.5
"""

from typing import Dict, List, Any, Optional
from evidence_guide_content import CaseType, EvidenceGuideContent


class EvidenceGuideGenerator:
    """
    Generator for customized evidence guides.
    
    Requirements:
    - 7.4: Step-by-step format with visuals
    - 7.5: Evidence type checklists
    """
    
    # Visual aid references for different evidence types
    VISUAL_AIDS = {
        "screenshot": {
            "icon": "📱",
            "description": "Screenshot guide",
            "reference": "See visual guide for proper screenshot capture"
        },
        "photo": {
            "icon": "📸",
            "description": "Photo documentation",
            "reference": "See visual guide for evidence photography"
        },
        "document": {
            "icon": "📄",
            "description": "Document preservation",
            "reference": "See visual guide for document handling"
        },
        "video": {
            "icon": "🎥",
            "description": "Video recording",
            "reference": "See visual guide for video evidence"
        },
        "audio": {
            "icon": "🎤",
            "description": "Audio recording",
            "reference": "See visual guide for audio evidence"
        },
        "digital": {
            "icon": "💾",
            "description": "Digital evidence",
            "reference": "See visual guide for digital preservation"
        },
        "physical": {
            "icon": "📦",
            "description": "Physical evidence",
            "reference": "See visual guide for physical evidence handling"
        }
    }
    
    # Evidence type checklists (minimum 5 items per type as per requirement 7.5)
    EVIDENCE_CHECKLISTS = {
        "digital_communication": {
            "title": "Digital Communication Evidence Checklist",
            "icon": "💬",
            "items": [
                {
                    "item": "Take full-screen screenshots including date and time",
                    "required": True,
                    "visual_aid": "screenshot"
                },
                {
                    "item": "Capture sender/receiver information clearly",
                    "required": True,
                    "visual_aid": "screenshot"
                },
                {
                    "item": "Save original message files or exports",
                    "required": True,
                    "visual_aid": "digital"
                },
                {
                    "item": "Document platform used (WhatsApp, Email, SMS, etc.)",
                    "required": True,
                    "visual_aid": None
                },
                {
                    "item": "Preserve metadata and message headers",
                    "required": True,
                    "visual_aid": "digital"
                },
                {
                    "item": "Create multiple backups in different locations",
                    "required": True,
                    "visual_aid": "digital"
                },
                {
                    "item": "Note phone numbers or email addresses involved",
                    "required": True,
                    "visual_aid": None
                }
            ]
        },
        "physical_evidence": {
            "title": "Physical Evidence Checklist",
            "icon": "📦",
            "items": [
                {
                    "item": "Photograph evidence from multiple angles",
                    "required": True,
                    "visual_aid": "photo"
                },
                {
                    "item": "Include scale reference in photos (ruler, coin, etc.)",
                    "required": True,
                    "visual_aid": "photo"
                },
                {
                    "item": "Store in protective container or bag",
                    "required": True,
                    "visual_aid": "physical"
                },
                {
                    "item": "Label with date, time, and location found",
                    "required": True,
                    "visual_aid": None
                },
                {
                    "item": "Document chain of custody (who handled it and when)",
                    "required": True,
                    "visual_aid": None
                },
                {
                    "item": "Avoid contamination - use gloves if possible",
                    "required": True,
                    "visual_aid": "physical"
                },
                {
                    "item": "Store in secure location away from tampering",
                    "required": True,
                    "visual_aid": None
                }
            ]
        },
        "documentary_evidence": {
            "title": "Documentary Evidence Checklist",
            "icon": "📄",
            "items": [
                {
                    "item": "Collect original documents whenever possible",
                    "required": True,
                    "visual_aid": "document"
                },
                {
                    "item": "Make certified copies of important documents",
                    "required": True,
                    "visual_aid": "document"
                },
                {
                    "item": "Scan documents at high resolution (300 DPI minimum)",
                    "required": True,
                    "visual_aid": "document"
                },
                {
                    "item": "Preserve documents in protective sleeves",
                    "required": True,
                    "visual_aid": "document"
                },
                {
                    "item": "Organize chronologically with index",
                    "required": True,
                    "visual_aid": None
                },
                {
                    "item": "Note source and date of each document",
                    "required": True,
                    "visual_aid": None
                },
                {
                    "item": "Keep digital and physical backups",
                    "required": True,
                    "visual_aid": "digital"
                }
            ]
        },
        "witness_evidence": {
            "title": "Witness Evidence Checklist",
            "icon": "👥",
            "items": [
                {
                    "item": "Identify all potential witnesses immediately",
                    "required": True,
                    "visual_aid": None
                },
                {
                    "item": "Collect full names and contact information",
                    "required": True,
                    "visual_aid": None
                },
                {
                    "item": "Document what each witness observed",
                    "required": True,
                    "visual_aid": None
                },
                {
                    "item": "Get written statements as soon as possible",
                    "required": True,
                    "visual_aid": "document"
                },
                {
                    "item": "Note the witness's relationship to you (if any)",
                    "required": True,
                    "visual_aid": None
                },
                {
                    "item": "Record date, time, and location of their observation",
                    "required": True,
                    "visual_aid": None
                },
                {
                    "item": "Keep witness contact details confidential and secure",
                    "required": True,
                    "visual_aid": None
                }
            ]
        },
        "medical_evidence": {
            "title": "Medical Evidence Checklist",
            "icon": "🏥",
            "items": [
                {
                    "item": "Seek immediate medical attention after injury",
                    "required": True,
                    "visual_aid": None
                },
                {
                    "item": "Request detailed medical report from doctor",
                    "required": True,
                    "visual_aid": "document"
                },
                {
                    "item": "Photograph all visible injuries",
                    "required": True,
                    "visual_aid": "photo"
                },
                {
                    "item": "Keep all medical bills and prescriptions",
                    "required": True,
                    "visual_aid": "document"
                },
                {
                    "item": "Document treatment timeline and follow-ups",
                    "required": True,
                    "visual_aid": None
                },
                {
                    "item": "Get psychological evaluation if applicable",
                    "required": False,
                    "visual_aid": None
                },
                {
                    "item": "Preserve medical records in original form",
                    "required": True,
                    "visual_aid": "document"
                }
            ]
        },
        "financial_evidence": {
            "title": "Financial Evidence Checklist",
            "icon": "💰",
            "items": [
                {
                    "item": "Collect all bank statements showing transactions",
                    "required": True,
                    "visual_aid": "document"
                },
                {
                    "item": "Save payment receipts and invoices",
                    "required": True,
                    "visual_aid": "document"
                },
                {
                    "item": "Document transaction dates and amounts",
                    "required": True,
                    "visual_aid": None
                },
                {
                    "item": "Preserve digital payment confirmations (UPI, net banking)",
                    "required": True,
                    "visual_aid": "screenshot"
                },
                {
                    "item": "Calculate total financial loss with breakdown",
                    "required": True,
                    "visual_aid": None
                },
                {
                    "item": "Collect contracts or agreements related to payments",
                    "required": True,
                    "visual_aid": "document"
                },
                {
                    "item": "Note account numbers and transaction IDs",
                    "required": True,
                    "visual_aid": None
                }
            ]
        }
    }
    
    def __init__(self):
        """Initialize the evidence guide generator."""
        self.content = EvidenceGuideContent()
    
    def detect_case_type(self, case_description: Optional[str] = None, case_type_input: Optional[str] = None) -> CaseType:
        """
        Detect case type from description or use provided case type.
        
        Args:
            case_description: Optional description of the case
            case_type_input: Optional explicit case type
            
        Returns:
            Detected or specified CaseType
            
        Requirements: Case type detection for customized guides
        """
        # If explicit case type provided, use it
        if case_type_input:
            try:
                return CaseType(case_type_input.lower())
            except ValueError:
                pass
        
        # Simple keyword-based detection from description
        if case_description:
            description_lower = case_description.lower()
            
            if any(word in description_lower for word in ["defamation", "defame", "reputation", "slander", "libel"]):
                return CaseType.DEFAMATION
            elif any(word in description_lower for word in ["harassment", "harass", "stalk", "molest"]):
                return CaseType.HARASSMENT
            elif any(word in description_lower for word in ["extortion", "blackmail", "threat", "demand money"]):
                return CaseType.EXTORTION
            elif any(word in description_lower for word in ["assault", "attack", "beat", "hit", "violence"]):
                return CaseType.ASSAULT
            elif any(word in description_lower for word in ["fraud", "cheat", "scam", "deceive"]):
                return CaseType.FRAUD
            elif any(word in description_lower for word in ["cyber", "hacking", "phishing", "online fraud"]):
                return CaseType.CYBERCRIME
            elif any(word in description_lower for word in ["false accusation", "false charge", "wrongly accused"]):
                return CaseType.FALSE_ACCUSATION
        
        # Default to general
        return CaseType.GENERAL
    
    def generate_step_by_step_instructions(self, case_type: CaseType) -> List[Dict[str, Any]]:
        """
        Generate numbered step-by-step instructions for evidence collection.
        
        Args:
            case_type: Type of legal case
            
        Returns:
            List of numbered steps with visual aid references
            
        Requirements: 7.4 (Step-by-step format with visuals)
        """
        case_content = self.content.get_case_specific_content(case_type)
        steps = []
        
        # Step 1: Understand what evidence to collect
        steps.append({
            "step_number": 1,
            "title": "Identify Required Evidence",
            "instruction": f"For {case_content['title'].lower()}, focus on collecting: " + 
                          ", ".join(case_content['key_evidence_types'][:3]) + ", and more.",
            "visual_aid": self.VISUAL_AIDS["document"],
            "details": case_content['key_evidence_types']
        })
        
        # Step 2: Immediate actions
        steps.append({
            "step_number": 2,
            "title": "Take Immediate Action",
            "instruction": "Collect evidence as soon as possible. Evidence can be lost, deleted, or become unavailable over time.",
            "visual_aid": None,
            "details": [
                "Act quickly - evidence may disappear",
                "Prioritize time-sensitive evidence",
                "Document everything immediately"
            ]
        })
        
        # Step 3: Digital evidence preservation
        steps.append({
            "step_number": 3,
            "title": "Preserve Digital Evidence",
            "instruction": "Follow proper procedures for digital evidence to ensure admissibility in court.",
            "visual_aid": self.VISUAL_AIDS["digital"],
            "details": self.content.get_digital_preservation_instructions()['instructions'][:5]
        })
        
        # Step 4: Case-specific collection
        steps.append({
            "step_number": 4,
            "title": "Follow Case-Specific Guidelines",
            "instruction": f"Apply specific evidence collection methods for {case_type.value} cases.",
            "visual_aid": None,
            "details": case_content['specific_instructions'][:5]
        })
        
        # Step 5: Organize and backup
        steps.append({
            "step_number": 5,
            "title": "Organize and Create Backups",
            "instruction": "Systematically organize all evidence and create multiple backups.",
            "visual_aid": self.VISUAL_AIDS["digital"],
            "details": [
                "Create a master folder with subfolders by type and date",
                "Label each piece of evidence clearly",
                "Make at least 3 backups in different locations",
                "Keep a detailed inventory of all evidence",
                "Store originals securely"
            ]
        })
        
        # Step 6: Maintain chain of custody
        steps.append({
            "step_number": 6,
            "title": "Document Chain of Custody",
            "instruction": "Keep records of who handled the evidence and when.",
            "visual_aid": self.VISUAL_AIDS["document"],
            "details": [
                "Create a log of evidence handling",
                "Note date, time, and person for each transfer",
                "Limit the number of people who handle evidence",
                "Store evidence securely when not in use"
            ]
        })
        
        # Step 7: Consult legal professional
        steps.append({
            "step_number": 7,
            "title": "Consult a Legal Professional",
            "instruction": "Have a lawyer review your evidence before submission to ensure it meets legal requirements.",
            "visual_aid": None,
            "details": [
                "Seek legal advice on evidence admissibility",
                "Get guidance on what additional evidence may be needed",
                "Understand the legal process for evidence submission",
                "Prepare for potential challenges to your evidence"
            ]
        })
        
        return steps
    
    def get_evidence_checklists(self, case_type: CaseType) -> List[Dict[str, Any]]:
        """
        Get relevant evidence type checklists for the case type.
        
        Args:
            case_type: Type of legal case
            
        Returns:
            List of evidence checklists with at least 5 items each
            
        Requirements: 7.5 (Evidence type checklists with at least 5 items)
        """
        # Determine which checklists are most relevant for this case type
        relevant_checklists = []
        
        # All cases need digital communication checklist
        relevant_checklists.append(self.EVIDENCE_CHECKLISTS["digital_communication"])
        
        # Add case-specific checklists
        if case_type in [CaseType.ASSAULT, CaseType.HARASSMENT]:
            relevant_checklists.append(self.EVIDENCE_CHECKLISTS["medical_evidence"])
            relevant_checklists.append(self.EVIDENCE_CHECKLISTS["witness_evidence"])
        
        if case_type in [CaseType.FRAUD, CaseType.EXTORTION]:
            relevant_checklists.append(self.EVIDENCE_CHECKLISTS["financial_evidence"])
            relevant_checklists.append(self.EVIDENCE_CHECKLISTS["documentary_evidence"])
        
        if case_type == CaseType.CYBERCRIME:
            relevant_checklists.append(self.EVIDENCE_CHECKLISTS["documentary_evidence"])
        
        if case_type in [CaseType.DEFAMATION, CaseType.FALSE_ACCUSATION]:
            relevant_checklists.append(self.EVIDENCE_CHECKLISTS["witness_evidence"])
            relevant_checklists.append(self.EVIDENCE_CHECKLISTS["documentary_evidence"])
        
        # Always include physical and documentary evidence for general cases
        if case_type == CaseType.GENERAL:
            relevant_checklists.append(self.EVIDENCE_CHECKLISTS["physical_evidence"])
            relevant_checklists.append(self.EVIDENCE_CHECKLISTS["documentary_evidence"])
            relevant_checklists.append(self.EVIDENCE_CHECKLISTS["witness_evidence"])
        
        # Ensure we have at least 2 checklists
        if len(relevant_checklists) < 2:
            relevant_checklists.append(self.EVIDENCE_CHECKLISTS["documentary_evidence"])
        
        return relevant_checklists
    
    def generate_complete_guide(
        self,
        case_type: Optional[str] = None,
        case_description: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate a complete evidence guide with all sections.
        
        Args:
            case_type: Optional case type string
            case_description: Optional case description for detection
            language: Language code (default: "en")
            
        Returns:
            Complete evidence guide dictionary
            
        Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7
        """
        # Detect case type
        detected_case_type = self.detect_case_type(case_description, case_type)
        
        # Get all content sections
        case_specific = self.content.get_case_specific_content(detected_case_type)
        digital_preservation = self.content.get_digital_preservation_instructions()
        admissibility = self.content.get_admissibility_requirements()
        tampering_warning = self.content.get_tampering_warning()
        digital_communication = self.content.get_digital_communication_procedures()
        
        # Generate step-by-step instructions
        steps = self.generate_step_by_step_instructions(detected_case_type)
        
        # Get evidence checklists
        checklists = self.get_evidence_checklists(detected_case_type)
        
        # Compile complete guide
        guide = {
            "case_type": detected_case_type.value,
            "language": language,
            "title": case_specific["title"],
            "description": case_specific["description"],
            
            # Requirement 7.6: Tampering warnings
            "tampering_warning": tampering_warning,
            
            # Requirement 7.1: Case-specific guidance
            "case_specific_guidance": {
                "key_evidence_types": case_specific["key_evidence_types"],
                "specific_instructions": case_specific["specific_instructions"],
                "relevant_laws": case_specific["relevant_laws"]
            },
            
            # Requirement 7.4: Step-by-step format with visuals
            "step_by_step_instructions": steps,
            
            # Requirement 7.2: Digital preservation instructions
            "digital_preservation": digital_preservation,
            
            # Requirement 7.7: Digital communication procedures
            "digital_communication_procedures": digital_communication,
            
            # Requirement 7.3: Admissibility requirements
            "admissibility_requirements": admissibility,
            
            # Requirement 7.5: Evidence type checklists (at least 5 items each)
            "evidence_checklists": checklists,
            
            # Additional metadata
            "visual_aids_available": list(self.VISUAL_AIDS.keys()),
            "total_steps": len(steps),
            "total_checklists": len(checklists)
        }
        
        return guide


# Singleton instance
_generator_instance = None


def get_evidence_guide_generator() -> EvidenceGuideGenerator:
    """Get singleton instance of evidence guide generator."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = EvidenceGuideGenerator()
    return _generator_instance
