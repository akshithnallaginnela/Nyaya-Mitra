"""
Translation service for UI elements and text processing.
Integrates spaCy for English and IndicNLP for Hindi and regional languages.
"""
from typing import Dict, Optional, List, Any
import spacy
from spacy.language import Language
import logging
import json
from pathlib import Path

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
        """Load UI element translations from JSON files for all supported languages."""
        translations_dir = Path(__file__).parent / "translations"
        
        # Supported languages
        supported_languages = ["en", "hi", "ta", "te", "bn", "mr", "gu"]
        
        for lang in supported_languages:
            translation_file = translations_dir / f"{lang}.json"
            
            if translation_file.exists():
                try:
                    with open(translation_file, "r", encoding="utf-8") as f:
                        self._ui_translations[lang] = json.load(f)
                    logger.info(f"Loaded {lang} translations from {translation_file}")
                except Exception as e:
                    logger.error(f"Failed to load {lang} translations: {e}")
                    # Fallback to empty dict
                    self._ui_translations[lang] = {}
            else:
                logger.warning(f"Translation file not found: {translation_file}")
                # Fallback to empty dict
                self._ui_translations[lang] = {}
    
    def get_translation(self, key: str, language: str = "en") -> str:
        """
        Get translation for a UI element key.
        
        Args:
            key: Translation key
            language: Target language code
            
        Returns:
            Translated string or key if not found
        """
        if language not in self._ui_translations:
            language = "en"
        
        return self._ui_translations[language].get(key, key)
    
    def get_all_translations(self, language: str = "en") -> Dict[str, str]:
        """
        Get all translations for a language.
        
        Args:
            language: Target language code
            
        Returns:
            Dictionary of all translations
        """
        if language not in self._ui_translations:
            language = "en"
        
        return self._ui_translations[language].copy()
    
    def process_text(self, text: str, language: str = "en") -> Optional[Any]:
        """
        Process text using appropriate NLP model.
        
        Args:
            text: Input text
            language: Language code
            
        Returns:
            Processed spaCy Doc object or None if model not available
        """
        if language not in self._nlp_models or self._nlp_models[language] is None:
            logger.warning(f"NLP model for {language} not available")
            return None
        
        return self._nlp_models[language](text)
    
    def extract_entities(self, text: str, language: str = "en") -> List[Dict[str, str]]:
        """
        Extract named entities from text.
        
        Args:
            text: Input text
            language: Language code
            
        Returns:
            List of entities with text, label, and position
        """
        doc = self.process_text(text, language)
        if doc is None:
            return []
        
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        return entities
    
    def tokenize(self, text: str, language: str = "en") -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            language: Language code
            
        Returns:
            List of tokens
        """
        doc = self.process_text(text, language)
        if doc is None:
            # Fallback to simple whitespace tokenization
            return text.split()
        
        return [token.text for token in doc]
    
    def add_translation(self, key: str, translations: Dict[str, str]):
        """
        Add or update a translation key for multiple languages.
        
        Args:
            key: Translation key
            translations: Dictionary mapping language codes to translations
        """
        for lang, translation in translations.items():
            if lang in self._ui_translations:
                self._ui_translations[lang][key] = translation


# Singleton instance
_translation_service: Optional[TranslationService] = None


def get_translation_service() -> TranslationService:
    """
    Get or create singleton translation service instance.
    
    Returns:
        TranslationService instance
    """
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service
