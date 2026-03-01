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
