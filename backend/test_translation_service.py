"""
Unit tests for translation service.
"""
import pytest
from translation_service import TranslationService, get_translation_service


class TestTranslationService:
    """Test suite for TranslationService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = TranslationService()
    
    def test_get_translation_english(self):
        """Test getting English translation."""
        result = self.service.get_translation("welcome", "en")
        assert result == "Welcome to Nyaya Mitra"
    
    def test_get_translation_hindi(self):
        """Test getting Hindi translation."""
        result = self.service.get_translation("welcome", "hi")
        assert result == "न्याय मित्र में आपका स्वागत है"
    
    def test_get_translation_tamil(self):
        """Test getting Tamil translation."""
        result = self.service.get_translation("welcome", "ta")
        assert result == "நியாய மித்ராவிற்கு வரவேற்கிறோம்"
    
    def test_get_translation_missing_key(self):
        """Test getting translation for missing key returns key."""
        result = self.service.get_translation("nonexistent_key", "en")
        assert result == "nonexistent_key"
    
    def test_get_translation_unsupported_language(self):
        """Test getting translation for unsupported language defaults to English."""
        result = self.service.get_translation("welcome", "fr")
        assert result == "Welcome to Nyaya Mitra"
    
    def test_get_all_translations_english(self):
        """Test getting all English translations."""
        translations = self.service.get_all_translations("en")
        assert isinstance(translations, dict)
        assert "welcome" in translations
        assert "login" in translations
        assert translations["app_name"] == "Nyaya Mitra"
    
    def test_get_all_translations_hindi(self):
        """Test getting all Hindi translations."""
        translations = self.service.get_all_translations("hi")
        assert isinstance(translations, dict)
        assert translations["app_name"] == "न्याय मित्र"
        assert translations["login"] == "लॉगिन"
    
    def test_translation_consistency_across_languages(self):
        """Test that all languages have the same keys."""
        en_translations = self.service.get_all_translations("en")
        hi_translations = self.service.get_all_translations("hi")
        ta_translations = self.service.get_all_translations("ta")
        
        # All should have the same keys
        assert set(en_translations.keys()) == set(hi_translations.keys())
        assert set(en_translations.keys()) == set(ta_translations.keys())
    
    def test_add_translation(self):
        """Test adding a new translation."""
        self.service.add_translation("test_key", {
            "en": "Test English",
            "hi": "परीक्षण हिंदी"
        })
        
        assert self.service.get_translation("test_key", "en") == "Test English"
        assert self.service.get_translation("test_key", "hi") == "परीक्षण हिंदी"
    
    def test_tokenize_english(self):
        """Test tokenizing English text."""
        text = "I need legal help"
        tokens = self.service.tokenize(text, "en")
        
        # Should return list of tokens
        assert isinstance(tokens, list)
        assert len(tokens) > 0
    
    def test_tokenize_unsupported_language_fallback(self):
        """Test tokenization falls back to simple split for unsupported languages."""
        text = "मुझे कानूनी सहायता चाहिए"
        tokens = self.service.tokenize(text, "hi")
        
        # Should fall back to whitespace tokenization
        assert isinstance(tokens, list)
        assert len(tokens) > 0
    
    def test_extract_entities_english(self):
        """Test entity extraction from English text."""
        text = "I filed a complaint at Delhi Police Station"
        entities = self.service.extract_entities(text, "en")
        
        # Should return list of entities
        assert isinstance(entities, list)
    
    def test_extract_entities_unsupported_language(self):
        """Test entity extraction returns empty list for unsupported languages."""
        text = "मुझे कानूनी सहायता चाहिए"
        entities = self.service.extract_entities(text, "hi")
        
        # Should return empty list when model not available
        assert isinstance(entities, list)
        assert len(entities) == 0
    
    def test_process_text_english(self):
        """Test processing English text with spaCy."""
        text = "I need legal help"
        doc = self.service.process_text(text, "en")
        
        # May be None if spaCy model not installed, or a Doc object
        if doc is not None:
            assert hasattr(doc, 'ents')
    
    def test_process_text_unsupported_language(self):
        """Test processing unsupported language returns None."""
        text = "मुझे कानूनी सहायता चाहिए"
        doc = self.service.process_text(text, "hi")
        
        # Should return None for unsupported language
        assert doc is None


class TestTranslationServiceSingleton:
    """Test singleton pattern for translation service."""
    
    def test_get_translation_service_singleton(self):
        """Test that get_translation_service returns same instance."""
        service1 = get_translation_service()
        service2 = get_translation_service()
        
        assert service1 is service2
    
    def test_singleton_maintains_state(self):
        """Test that singleton maintains state across calls."""
        service1 = get_translation_service()
        service1.add_translation("singleton_test", {
            "en": "Singleton Test"
        })
        
        service2 = get_translation_service()
        result = service2.get_translation("singleton_test", "en")
        
        assert result == "Singleton Test"


class TestTranslationKeys:
    """Test that all required translation keys exist."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = TranslationService()
        self.required_keys = [
            "app_name", "welcome", "login", "register", "logout",
            "email", "password", "submit", "cancel",
            "chat_title", "case_analysis", "document_generator",
            "legal_aid", "emergency", "evidence_guide"
        ]
    
    def test_required_keys_exist_in_english(self):
        """Test that all required keys exist in English."""
        translations = self.service.get_all_translations("en")
        
        for key in self.required_keys:
            assert key in translations, f"Missing key: {key}"
    
    def test_required_keys_exist_in_hindi(self):
        """Test that all required keys exist in Hindi."""
        translations = self.service.get_all_translations("hi")
        
        for key in self.required_keys:
            assert key in translations, f"Missing key: {key}"
    
    def test_required_keys_exist_in_tamil(self):
        """Test that all required keys exist in Tamil."""
        translations = self.service.get_all_translations("ta")
        
        for key in self.required_keys:
            assert key in translations, f"Missing key: {key}"
    
    def test_no_empty_translations(self):
        """Test that no translations are empty strings."""
        for lang in ["en", "hi", "ta"]:
            translations = self.service.get_all_translations(lang)
            
            for key, value in translations.items():
                assert value, f"Empty translation for {key} in {lang}"
                assert isinstance(value, str), f"Non-string translation for {key} in {lang}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
