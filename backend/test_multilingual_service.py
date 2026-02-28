"""
Tests for multilingual service.
"""
import pytest
from multilingual_service import MultilingualService, get_multilingual_service


class TestMultilingualService:
    """Test suite for MultilingualService."""
    
    def test_initialization(self):
        """Test service initialization."""
        service = MultilingualService()
        assert service is not None
    
    def test_detect_language_english(self):
        """Test language detection for English."""
        service = MultilingualService()
        
        text = "What is defamation under Indian law?"
        language = service.detect_language(text)
        
        assert language == "en"
    
    def test_detect_language_hindi(self):
        """Test language detection for Hindi."""
        service = MultilingualService()
        
        text = "भारतीय कानून के तहत मानहानि क्या है?"
        language = service.detect_language(text)
        
        assert language == "hi"
    
    def test_detect_language_empty_text(self):
        """Test language detection with empty text defaults to English."""
        service = MultilingualService()
        
        assert service.detect_language("") == "en"
        assert service.detect_language("   ") == "en"
    
    def test_detect_language_unsupported_defaults_to_english(self):
        """Test unsupported language defaults to English."""
        service = MultilingualService()
        
        # French text (not in supported languages)
        text = "Qu'est-ce que la diffamation?"
        language = service.detect_language(text)
        
        # Should default to English for unsupported languages
        assert language == "en"
    
    def test_is_language_supported_true(self):
        """Test is_language_supported returns True for supported languages."""
        service = MultilingualService()
        
        assert service.is_language_supported("en") is True
        assert service.is_language_supported("hi") is True
        assert service.is_language_supported("ta") is True
        assert service.is_language_supported("te") is True
        assert service.is_language_supported("bn") is True
        assert service.is_language_supported("mr") is True
        assert service.is_language_supported("gu") is True
    
    def test_is_language_supported_false(self):
        """Test is_language_supported returns False for unsupported languages."""
        service = MultilingualService()
        
        assert service.is_language_supported("fr") is False
        assert service.is_language_supported("de") is False
        assert service.is_language_supported("es") is False
    
    def test_get_language_name(self):
        """Test getting language names."""
        service = MultilingualService()
        
        assert service.get_language_name("en") == "English"
        assert service.get_language_name("hi") == "Hindi"
        assert service.get_language_name("ta") == "Tamil"
        assert service.get_language_name("te") == "Telugu"
        assert service.get_language_name("bn") == "Bengali"
        assert service.get_language_name("mr") == "Marathi"
        assert service.get_language_name("gu") == "Gujarati"
    
    def test_get_language_name_unknown(self):
        """Test getting name for unknown language."""
        service = MultilingualService()
        
        assert service.get_language_name("xx") == "Unknown"
    
    def test_get_supported_languages(self):
        """Test getting all supported languages."""
        service = MultilingualService()
        
        languages = service.get_supported_languages()
        
        assert len(languages) == 7
        assert "en" in languages
        assert "hi" in languages
        assert languages["en"] == "English"
        assert languages["hi"] == "Hindi"
    
    def test_get_language_prompt_suffix_english(self):
        """Test getting prompt suffix for English."""
        service = MultilingualService()
        
        suffix = service.get_language_prompt_suffix("en")
        
        assert "English" in suffix
        assert "clear" in suffix.lower()
    
    def test_get_language_prompt_suffix_hindi(self):
        """Test getting prompt suffix for Hindi."""
        service = MultilingualService()
        
        suffix = service.get_language_prompt_suffix("hi")
        
        assert "हिंदी" in suffix
    
    def test_get_language_prompt_suffix_unsupported_defaults_to_english(self):
        """Test prompt suffix for unsupported language defaults to English."""
        service = MultilingualService()
        
        suffix = service.get_language_prompt_suffix("fr")
        
        assert "English" in suffix
    
    def test_get_language_disclaimer_english(self):
        """Test getting disclaimer for English."""
        service = MultilingualService()
        
        disclaimer = service.get_language_disclaimer("en")
        
        assert "⚠️" in disclaimer
        assert "legal professional" in disclaimer.lower()
    
    def test_get_language_disclaimer_hindi(self):
        """Test getting disclaimer for Hindi."""
        service = MultilingualService()
        
        disclaimer = service.get_language_disclaimer("hi")
        
        assert "⚠️" in disclaimer
        assert "कानूनी" in disclaimer or "पेशेवर" in disclaimer
    
    def test_get_language_disclaimer_tamil(self):
        """Test getting disclaimer for Tamil."""
        service = MultilingualService()
        
        disclaimer = service.get_language_disclaimer("ta")
        
        assert "⚠️" in disclaimer
        assert "சட்ட" in disclaimer
    
    def test_prepare_multilingual_prompt(self):
        """Test preparing multilingual prompt."""
        service = MultilingualService()
        
        base_prompt = "You are a legal assistant."
        enhanced_prompt = service.prepare_multilingual_prompt(base_prompt, "hi")
        
        assert base_prompt in enhanced_prompt
        assert "हिंदी" in enhanced_prompt
    
    def test_add_language_disclaimer_with_disclaimer(self):
        """Test adding disclaimer to response."""
        service = MultilingualService()
        
        response = "This is legal information."
        enhanced_response = service.add_language_disclaimer(response, "en", add_disclaimer=True)
        
        assert response in enhanced_response
        assert "⚠️" in enhanced_response
        assert len(enhanced_response) > len(response)
    
    def test_add_language_disclaimer_without_disclaimer(self):
        """Test not adding disclaimer when flag is False."""
        service = MultilingualService()
        
        response = "This is legal information."
        enhanced_response = service.add_language_disclaimer(response, "en", add_disclaimer=False)
        
        assert enhanced_response == response
    
    def test_process_query_language_auto_detect(self):
        """Test processing query language with auto-detection."""
        service = MultilingualService()
        
        query = "What is defamation?"
        result = service.process_query_language(query)
        
        assert result["detected_language"] == "en"
        assert result["response_language"] == "en"
        assert result["language_name"] == "English"
    
    def test_process_query_language_with_preferred(self):
        """Test processing query language with preferred language."""
        service = MultilingualService()
        
        query = "What is defamation?"
        result = service.process_query_language(query, preferred_language="hi")
        
        assert result["detected_language"] == "en"
        assert result["response_language"] == "hi"  # Uses preferred
        assert result["language_name"] == "Hindi"
    
    def test_process_query_language_preferred_unsupported(self):
        """Test processing with unsupported preferred language falls back to detected."""
        service = MultilingualService()
        
        query = "What is defamation?"
        result = service.process_query_language(query, preferred_language="fr")
        
        assert result["detected_language"] == "en"
        assert result["response_language"] == "en"  # Falls back to detected
    
    def test_process_query_language_hindi_query(self):
        """Test processing Hindi query."""
        service = MultilingualService()
        
        query = "मानहानि क्या है?"
        result = service.process_query_language(query)
        
        assert result["detected_language"] == "hi"
        assert result["response_language"] == "hi"
        assert result["language_name"] == "Hindi"


def test_get_multilingual_service_singleton():
    """Test get_multilingual_service returns singleton instance."""
    service1 = get_multilingual_service()
    service2 = get_multilingual_service()
    
    assert service1 is service2


def test_get_multilingual_service_creates_instance():
    """Test get_multilingual_service creates MultilingualService instance."""
    # Reset singleton
    import multilingual_service
    multilingual_service._multilingual_service = None
    
    service = get_multilingual_service()
    assert isinstance(service, MultilingualService)
