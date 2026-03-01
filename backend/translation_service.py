"""
Translation service for UI elements and text processing.
Integrates spaCy for English and IndicNLP for Hindi and regional languages.
"""
from typing import Dict, Optional, List, Any
import spacy
from spacy.language import Language
import logging

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for handling translations and NLP processing."""
    
    def __init__(self):
        """Initialize translation service with NLP models."""
        self._nlp_models: Dict[str, Language] = {}
        self._ui_translations: Dict[str, Dict[str, str]] = {}
        self._load_nlp_models()
        self._load_ui_translations()
    
    def _load_nlp_models(self):
        """Load spaCy models for supported languages."""
        try:
            # Load English model
            self._nlp_models["en"] = spacy.load("en_core_web_sm")
            logger.info("Loaded English spaCy model")
        except OSError:
            logger.warning("English spaCy model not found. Run: python -m spacy download en_core_web_sm")
            self._nlp_models["en"] = None
        
        # Note: IndicNLP models would be loaded here when available
        # For now, we'll use basic text processing for Indic languages
        for lang in ["hi", "ta", "te", "bn", "mr", "gu"]:
            self._nlp_models[lang] = None
    
    def _load_ui_translations(self):
        """Load UI element translations for all supported languages."""
        # English translations (base)
        self._ui_translations["en"] = {
            # Common UI elements
            "app_name": "Nyaya Mitra",
            "welcome": "Welcome to Nyaya Mitra",
            "login": "Login",
            "register": "Register",
            "logout": "Logout",
            "email": "Email",
            "password": "Password",
            "full_name": "Full Name",
            "college_name": "College Name",
            "submit": "Submit",
            "cancel": "Cancel",
            "save": "Save",
            "delete": "Delete",
            "edit": "Edit",
            "back": "Back",
            "next": "Next",
            "previous": "Previous",
            "search": "Search",
            "filter": "Filter",
            "clear": "Clear",
            "loading": "Loading...",
            "error": "Error",
            "success": "Success",
            
            # Chat interface
            "chat_title": "Legal Chat Assistant",
            "chat_placeholder": "Ask your legal question...",
            "send_message": "Send",
            "new_conversation": "New Conversation",
            "conversation_history": "Conversation History",
            
            # Case analysis
            "case_analysis": "Case Analysis",
            "validity_score": "Validity Score",
            "evidence_strength": "Evidence Strength",
            "legal_basis": "Legal Basis",
            "procedural_compliance": "Procedural Compliance",
            "timeline_analysis": "Timeline Analysis",
            "weaknesses": "Weaknesses",
            "recommendations": "Recommendations",
            
            # Document generation
            "document_generator": "Document Generator",
            "select_template": "Select Template",
            "legal_letter": "Legal Letter",
            "rti_application": "RTI Application",
            "counter_petition": "Counter Petition",
            "generate_document": "Generate Document",
            "download_pdf": "Download PDF",
            "download_text": "Download Text",
            
            # Legal aid
            "legal_aid": "Legal Aid",
            "find_legal_aid": "Find Legal Aid",
            "location": "Location",
            "specialization": "Specialization",
            "contact_info": "Contact Information",
            "phone": "Phone",
            "address": "Address",
            
            # Emergency
            "emergency": "Emergency",
            "emergency_contacts": "Emergency Contacts",
            "police": "Police",
            "legal_helpline": "Legal Helpline",
            "mental_health": "Mental Health Support",
            "student_services": "Student Services",
            
            # Evidence guide
            "evidence_guide": "Evidence Guide",
            "collect_evidence": "Collect Evidence",
            "digital_evidence": "Digital Evidence",
            "physical_evidence": "Physical Evidence",
            
            # Settings
            "settings": "Settings",
            "language": "Language",
            "change_language": "Change Language",
            "profile": "Profile",
            "account": "Account",
        }
        
        # Hindi translations
        self._ui_translations["hi"] = {
            "app_name": "न्याय मित्र",
            "welcome": "न्याय मित्र में आपका स्वागत है",
            "login": "लॉगिन",
            "register": "पंजीकरण करें",
            "logout": "लॉगआउट",
            "email": "ईमेल",
            "password": "पासवर्ड",
            "full_name": "पूरा नाम",
            "college_name": "कॉलेज का नाम",
            "submit": "जमा करें",
            "cancel": "रद्द करें",
            "save": "सहेजें",
            "delete": "हटाएं",
            "edit": "संपादित करें",
            "back": "वापस",
            "next": "अगला",
            "previous": "पिछला",
            "search": "खोजें",
            "filter": "फ़िल्टर",
            "clear": "साफ़ करें",
            "loading": "लोड हो रहा है...",
            "error": "त्रुटि",
            "success": "सफलता",
            
            "chat_title": "कानूनी चैट सहायक",
            "chat_placeholder": "अपना कानूनी सवाल पूछें...",
            "send_message": "भेजें",
            "new_conversation": "नई बातचीत",
            "conversation_history": "बातचीत का इतिहास",
            
            "case_analysis": "मामले का विश्लेषण",
            "validity_score": "वैधता स्कोर",
            "evidence_strength": "साक्ष्य की मजबूती",
            "legal_basis": "कानूनी आधार",
            "procedural_compliance": "प्रक्रियात्मक अनुपालन",
            "timeline_analysis": "समयरेखा विश्लेषण",
            "weaknesses": "कमजोरियां",
            "recommendations": "सिफारिशें",
            
            "document_generator": "दस्तावेज़ जनरेटर",
            "select_template": "टेम्पलेट चुनें",
            "legal_letter": "कानूनी पत्र",
            "rti_application": "आरटीआई आवेदन",
            "counter_petition": "प्रति याचिका",
            "generate_document": "दस्तावेज़ बनाएं",
            "download_pdf": "पीडीएफ डाउनलोड करें",
            "download_text": "टेक्स्ट डाउनलोड करें",
            
            "legal_aid": "कानूनी सहायता",
            "find_legal_aid": "कानूनी सहायता खोजें",
            "location": "स्थान",
            "specialization": "विशेषज्ञता",
            "contact_info": "संपर्क जानकारी",
            "phone": "फोन",
            "address": "पता",
            
            "emergency": "आपातकाल",
            "emergency_contacts": "आपातकालीन संपर्क",
            "police": "पुलिस",
            "legal_helpline": "कानूनी हेल्पलाइन",
            "mental_health": "मानसिक स्वास्थ्य सहायता",
            "student_services": "छात्र सेवाएं",
            
            "evidence_guide": "साक्ष्य मार्गदर्शिका",
            "collect_evidence": "साक्ष्य एकत्र करें",
            "digital_evidence": "डिजिटल साक्ष्य",
            "physical_evidence": "भौतिक साक्ष्य",
            
            "settings": "सेटिंग्स",
            "language": "भाषा",
            "change_language": "भाषा बदलें",
            "profile": "प्रोफ़ाइल",
            "account": "खाता",
        }
