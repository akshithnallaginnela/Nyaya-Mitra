"""
Evidence Guide Content System
Provides case-type specific evidence guide templates with digital preservation,
admissibility requirements, tampering warnings, and digital communication procedures.

Requirements: 7.1, 7.2, 7.3, 7.6, 7.7
"""

from typing import Dict, List, Any
from enum import Enum


class CaseType(str, Enum):
    """Supported case types for evidence guides"""
    DEFAMATION = "defamation"
    HARASSMENT = "harassment"
    EXTORTION = "extortion"
    ASSAULT = "assault"
    FRAUD = "fraud"
    CYBERCRIME = "cybercrime"
    FALSE_ACCUSATION = "false_accusation"
    GENERAL = "general"


class EvidenceGuideContent:
    """
    Content system for evidence guides with case-type specific templates.
    
    Requirements:
    - 7.1: Case-specific guidance
    - 7.2: Digital preservation instructions
    - 7.3: Admissibility requirements
    - 7.6: Tampering warnings
    - 7.7: Digital communication procedures
    """
    
    # Common sections for all case types
    TAMPERING_WARNING = {
        "title": "⚠️ Evidence Tampering Warning",
        "content": [
            "Evidence tampering is a serious criminal offense under Section 204 of the Indian Penal Code.",
            "Tampering with evidence can result in imprisonment up to 7 years and/or fine.",
            "Never alter, destroy, or fabricate evidence. Present all evidence in its original form.",
            "If you discover evidence has been tampered with, report it immediately to authorities.",
            "Maintain chain of custody - document who handled the evidence and when."
        ],
        "legal_consequences": "Punishment for evidence tampering: Up to 7 years imprisonment under IPC Section 204"
    }
    
    ADMISSIBILITY_REQUIREMENTS = {
        "title": "Legal Admissibility Requirements",
        "content": [
            "Evidence must be relevant to the case and obtained legally.",
            "Digital evidence must be authenticated and its integrity verified.",
            "Hearsay evidence is generally not admissible unless it falls under exceptions.",
            "Evidence obtained through illegal means (e.g., illegal wiretapping) is inadmissible.",
            "Original documents are preferred; copies must be properly certified.",
            "Chain of custody must be maintained for physical evidence.",
            "Expert testimony may be required for technical or scientific evidence."
        ],
        "key_laws": [
            "Indian Evidence Act, 1872 - Sections 45-51 (Expert Opinion)",
            "Indian Evidence Act, 1872 - Section 65B (Electronic Evidence)",
            "Information Technology Act, 2000 - Section 65B (Digital Evidence)"
        ]
    }
    
    DIGITAL_PRESERVATION_INSTRUCTIONS = {
        "title": "Digital Evidence Preservation",
        "instructions": [
            "Take screenshots immediately - evidence can be deleted or modified",
            "Capture full screen including date, time, and URL/app name",
            "Save original files without editing or cropping",
            "Create multiple backups on different devices/cloud storage",
            "Document the date, time, and method of evidence collection",
            "Preserve metadata (EXIF data for photos, email headers, etc.)",
            "Do not forward or share evidence unnecessarily - maintain original copies"
        ],
        "best_practices": [
            "Use screen recording for video evidence or live interactions",
            "Save complete email threads with headers showing sender/receiver details",
            "For social media, capture profile information along with content",
            "Store evidence in read-only format when possible",
            "Create hash values (checksums) for digital files to prove integrity"
        ]
    }
    
    DIGITAL_COMMUNICATION_PROCEDURES = {
        "title": "Digital Communication Evidence Procedures",
        "screenshot_guidelines": [
            "Include the entire screen showing date, time, and platform",
            "Capture sender/receiver information clearly",
            "Show message timestamps and delivery status",
            "Include profile pictures and usernames",
            "Take multiple screenshots if conversation is long",
            "Do not crop or edit screenshots - keep them in original form"
        ],
        "backup_procedures": [
            "Export chat history from messaging apps (WhatsApp, Telegram, etc.)",
            "Save emails in .eml or .msg format to preserve headers",
            "Download social media posts and comments as HTML or PDF",
            "Record video calls if legally permissible (with consent)",
            "Store backups in multiple locations (local drive, cloud, external drive)",
            "Create a master folder with organized subfolders by date and type"
        ],
        "authentication_tips": [
            "Note the phone number or email address of the sender",
            "Document the platform used (WhatsApp, Email, SMS, etc.)",
            "Record the exact date and time of communication",
            "Preserve any delivery receipts or read receipts",
            "Keep the original device if possible for forensic verification"
        ]
    }
    
    # Case-type specific content
    CASE_SPECIFIC_GUIDES = {
        CaseType.DEFAMATION: {
            "title": "Evidence Guide for Defamation Cases",
            "description": "Collect evidence of false statements that harm your reputation",
            "key_evidence_types": [
                "Screenshots of defamatory posts/messages",
                "Published articles or social media posts",
                "Witness statements from people who saw the defamatory content",
                "Proof of your actual reputation (awards, certificates, testimonials)",
                "Evidence of damages (lost opportunities, mental distress)"
            ],
            "specific_instructions": [
                "Capture the defamatory statement in its original context",
                "Document the date and platform where it was published",
                "Identify the person who made the statement",
                "Show that the statement was communicated to third parties",
                "Collect evidence that the statement is false",
                "Document any harm caused to your reputation or livelihood"
            ],
            "relevant_laws": [
                "IPC Section 499 - Defamation",
                "IPC Section 500 - Punishment for Defamation"
            ]
        },
        
        CaseType.HARASSMENT: {
            "title": "Evidence Guide for Harassment Cases",
            "description": "Document patterns of unwanted behavior and communication",
            "key_evidence_types": [
                "Messages, emails, or calls showing harassment",
                "Screenshots of social media interactions",
                "Witness statements from people who observed the harassment",
                "Medical records if harassment caused physical/mental harm",
                "Police complaints or previous reports"
            ],
            "specific_instructions": [
                "Document every incident with date, time, and location",
                "Save all messages and communications from the harasser",
                "Record the frequency and pattern of harassment",
                "Note any threats or intimidating language",
                "Document your responses (or lack thereof) to show unwanted nature",
                "Collect evidence of any attempts to stop the harassment"
            ],
            "relevant_laws": [
                "IPC Section 354A - Sexual Harassment",
                "IPC Section 354D - Stalking",
                "IPC Section 509 - Word, gesture or act intended to insult the modesty of a woman"
            ]
        },
        
        CaseType.EXTORTION: {
            "title": "Evidence Guide for Extortion Cases",
            "description": "Preserve evidence of threats and demands for money or favors",
            "key_evidence_types": [
                "Messages or emails containing threats or demands",
                "Audio recordings of threatening calls (if legally recorded)",
                "Bank transaction records if money was paid",
                "Screenshots of demands on social media or messaging apps",
                "Witness statements from people aware of the extortion"
            ],
            "specific_instructions": [
                "Save all communication showing threats or demands",
                "Document what was demanded (money, favors, etc.)",
                "Record any deadlines or ultimatums given",
                "Preserve evidence of the threat (what harm was threatened)",
                "Keep records of any payments made under duress",
                "Do not delete threatening messages - they are crucial evidence"
            ],
            "relevant_laws": [
                "IPC Section 383 - Extortion",
                "IPC Section 384 - Punishment for Extortion",
                "IPC Section 385 - Putting person in fear of injury to commit extortion"
            ]
        },
        
        CaseType.ASSAULT: {
            "title": "Evidence Guide for Assault Cases",
            "description": "Document physical harm and the circumstances of the assault",
            "key_evidence_types": [
                "Medical reports and photographs of injuries",
                "Police FIR (First Information Report)",
                "Witness statements from people who saw the assault",
                "CCTV footage or video recordings",
                "Torn or damaged clothing",
                "Messages or threats before/after the assault"
            ],
            "specific_instructions": [
                "Seek immediate medical attention and get a medical report",
                "Photograph all injuries from multiple angles",
                "File a police complaint as soon as possible",
                "Identify and contact witnesses immediately",
                "Preserve any physical evidence (torn clothes, weapons, etc.)",
                "Document the exact location, date, and time of the assault",
                "Save any threatening messages before or after the incident"
            ],
            "relevant_laws": [
                "IPC Section 323 - Punishment for voluntarily causing hurt",
                "IPC Section 325 - Punishment for voluntarily causing grievous hurt",
                "IPC Section 351 - Assault"
            ]
        },
        
        CaseType.FRAUD: {
            "title": "Evidence Guide for Fraud Cases",
            "description": "Collect evidence of deception and financial loss",
            "key_evidence_types": [
                "Contracts, agreements, or written promises",
                "Bank statements and transaction records",
                "Emails or messages showing false representations",
                "Receipts, invoices, or payment proofs",
                "Witness statements from other victims or observers",
                "Company registration documents or business cards"
            ],
            "specific_instructions": [
                "Gather all documents related to the transaction",
                "Document the false promises or misrepresentations made",
                "Collect proof of payment (bank transfers, receipts, etc.)",
                "Show the actual facts that contradict the false claims",
                "Calculate and document your financial losses",
                "Identify the person or entity responsible for the fraud",
                "Check if others were also defrauded (pattern of fraud)"
            ],
            "relevant_laws": [
                "IPC Section 415 - Cheating",
                "IPC Section 420 - Cheating and dishonestly inducing delivery of property",
                "IPC Section 463 - Forgery"
            ]
        },
        
        CaseType.CYBERCRIME: {
            "title": "Evidence Guide for Cybercrime Cases",
            "description": "Preserve digital evidence of online criminal activity",
            "key_evidence_types": [
                "Screenshots of fraudulent websites or messages",
                "Email headers showing sender information",
                "IP addresses and server logs (if accessible)",
                "Transaction records for online fraud",
                "Malware or phishing email samples",
                "Social media profiles of perpetrators"
            ],
            "specific_instructions": [
                "Do not interact further with the cybercriminal",
                "Take screenshots of all relevant web pages and messages",
                "Save complete email headers (not just the message body)",
                "Document URLs, usernames, and account details",
                "Report to cybercrime.gov.in immediately",
                "Preserve your device for forensic analysis if needed",
                "Change passwords and secure your accounts",
                "Keep records of all financial transactions"
            ],
            "relevant_laws": [
                "IT Act Section 66 - Computer related offences",
                "IT Act Section 66C - Identity theft",
                "IT Act Section 66D - Cheating by personation using computer resource",
                "IT Act Section 67 - Publishing obscene material"
            ]
        },
        
        CaseType.FALSE_ACCUSATION: {
            "title": "Evidence Guide for False Accusation Cases",
            "description": "Gather evidence to prove your innocence and the falsity of accusations",
            "key_evidence_types": [
                "Alibi evidence (proof you were elsewhere)",
                "Witness statements supporting your version",
                "Digital evidence (GPS data, CCTV footage, etc.)",
                "Communication records showing the truth",
                "Evidence of motive for false accusation",
                "Inconsistencies in the accuser's statements"
            ],
            "specific_instructions": [
                "Document your whereabouts at the time of alleged incident",
                "Collect evidence proving the accusation is false",
                "Identify witnesses who can support your innocence",
                "Preserve digital footprints (location data, online activity)",
                "Document any motive the accuser might have",
                "Collect evidence of the accuser's credibility issues",
                "Save all communication with the accuser",
                "Gather character references and testimonials"
            ],
            "relevant_laws": [
                "IPC Section 211 - False charge of offence made with intent to injure",
                "IPC Section 182 - False information to public servant",
                "IPC Section 191 - Giving false evidence"
            ]
        },
        
        CaseType.GENERAL: {
            "title": "General Evidence Collection Guide",
            "description": "Basic evidence collection principles for any legal case",
            "key_evidence_types": [
                "Documentary evidence (contracts, letters, receipts)",
                "Digital evidence (emails, messages, social media)",
                "Physical evidence (objects, photographs)",
                "Testimonial evidence (witness statements)",
                "Expert evidence (professional opinions)"
            ],
            "specific_instructions": [
                "Collect evidence as soon as possible",
                "Preserve evidence in its original form",
                "Document the context of each piece of evidence",
                "Maintain a chronological record of events",
                "Identify and contact potential witnesses",
                "Keep multiple copies of all evidence",
                "Organize evidence systematically by type and date",
                "Consult a lawyer before submitting evidence"
            ],
            "relevant_laws": [
                "Indian Evidence Act, 1872",
                "Code of Criminal Procedure, 1973",
                "Information Technology Act, 2000"
            ]
        }
    }
    
    @classmethod
    def get_case_specific_content(cls, case_type: CaseType) -> Dict[str, Any]:
        """
        Get case-specific evidence guide content.
        
        Args:
            case_type: Type of legal case
            
        Returns:
            Dictionary containing case-specific guide content
            
        Requirements: 7.1 (Case-specific guidance)
        """
        return cls.CASE_SPECIFIC_GUIDES.get(case_type, cls.CASE_SPECIFIC_GUIDES[CaseType.GENERAL])
    
    @classmethod
    def get_digital_preservation_instructions(cls) -> Dict[str, Any]:
        """
        Get digital evidence preservation instructions.
        
        Returns:
            Dictionary containing digital preservation guidelines
            
        Requirements: 7.2 (Digital preservation instructions)
        """
        return cls.DIGITAL_PRESERVATION_INSTRUCTIONS
    
    @classmethod
    def get_admissibility_requirements(cls) -> Dict[str, Any]:
        """
        Get legal admissibility requirements for evidence.
        
        Returns:
            Dictionary containing admissibility requirements
            
        Requirements: 7.3 (Admissibility requirements)
        """
        return cls.ADMISSIBILITY_REQUIREMENTS
    
    @classmethod
    def get_tampering_warning(cls) -> Dict[str, Any]:
        """
        Get evidence tampering warning.
        
        Returns:
            Dictionary containing tampering warning
            
        Requirements: 7.6 (Tampering warnings)
        """
        return cls.TAMPERING_WARNING
    
    @classmethod
    def get_digital_communication_procedures(cls) -> Dict[str, Any]:
        """
        Get digital communication evidence procedures.
        
        Returns:
            Dictionary containing screenshot and backup procedures
            
        Requirements: 7.7 (Digital communication procedures)
        """
        return cls.DIGITAL_COMMUNICATION_PROCEDURES
    
    @classmethod
    def get_all_case_types(cls) -> List[str]:
        """Get list of all supported case types."""
        return [case_type.value for case_type in CaseType]
