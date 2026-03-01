"""
Integration tests for translation infrastructure.
Tests the interaction between multilingual_service and translation_service.
"""
import pytest
from multilingual_service import get_multilingual_service
from translation_service import get_translation_service


class TestTranslationIntegration:
    """Integration tests for translation infrastructure."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.ml_service = get_multilingual_service()
        self.trans_service = get_translation_service()
    
    def test_detect_language_and_get_translation(self):
        """Test detecting language and getting appropriate translation."""
        # English query
        en_query = "I need legal help"
        en_lang = self.ml_service.detect_language(en_query)
        en_welcome = self.trans_service.get_translation("welcome", en_lang)
        
        assert en_lang == "en"
        assert en_welcome == "Welcome to Nyaya Mitra"
        
        # Hindi/Indic query (langdetect may detect as hi, mr, or other Indic language)
        hi_query = "मुझे कानूनी सहायता चाहिए"
        hi_lang = self.ml_service.detect_language(hi_query)
        hi_welcome = self.trans_service.get_translation("welcome", hi_lang)
        
        # Should detect as one of the supported Indic languages
        assert hi_lang in ["hi", "mr", "gu", "bn"]
        # Should have a valid translation
        assert hi_welcome
        assert isinstance(hi_welcome, str)
    
    def test_process_query_with_ui_translations(self):
        """Test processing query and getting UI translations."""
        query = "मुझे कानूनी सहायता चाहिए"
        
        # Process query language
        lang_info = self.ml_service.process_query_language(query)
        detected_lang = lang_info["response_language"]
        
        # Get UI translations for detected language
        translations = self.trans_service.get_all_translations(detected_lang)
        
        # Should detect as one of the supported Indic languages
        assert detected_lang in ["hi", "mr", "gu", "bn"]
        # Should have valid translations
        assert "chat_title" in translations
        assert "submit" in translations
        assert isinstance(translations["chat_title"], str)
    
    def test_multilingual_prompt_with_translations(self):
        """Test creating multilingual prompt with UI translations."""
        query = "I need help with a legal case"
        
        # Detect language
        lang_info = self.ml_service.process_query_language(query)
        lang = lang_info["response_language"]
        
        # Prepare prompt
        base_prompt = "You are a legal assistant."
        enhanced_prompt = self.ml_service.prepare_multilingual_prompt(
            base_prompt,
            lang
        )
        
        # Get UI translation for chat title
        chat_title = self.trans_service.get_translation("chat_title", lang)
        
        assert lang == "en"
        assert "English" in enhanced_prompt
        assert chat_title == "Legal Chat Assistant"
    
    def test_language_consistency_across_services(self):
        """Test that both services support the same languages."""
        ml_languages = self.ml_service.get_supported_languages()
        
        # Check that translation service has translations for all supported languages
        for lang_code in ml_languages.keys():
            translations = self.trans_service.get_all_translations(lang_code)
            assert isinstance(translations, dict)
            assert len(translations) > 0
    
    def test_disclaimer_with_translations(self):
        """Test adding disclaimer with UI translations."""
        response = "This is legal advice."
        lang = "hi"
        
        # Add disclaimer
        response_with_disclaimer = self.ml_service.add_language_disclaimer(
            response,
            lang,
            add_disclaimer=True
        )
        
        # Get error translation
        error_text = self.trans_service.get_translation("error", lang)
        
        assert "⚠️" in response_with_disclaimer
        assert error_text == "त्रुटि"
    
    def test_preferred_language_with_translations(self):
        """Test using preferred language with translations."""
        # User prefers Hindi but queries in English
        query = "I need legal help"
        preferred_lang = "hi"
        
        # Process with preferred language
        lang_info = self.ml_service.process_query_language(
            query,
            preferred_language=preferred_lang
        )
        
        # Get translations in preferred language
        translations = self.trans_service.get_all_translations(
            lang_info["response_language"]
        )
        
        assert lang_info["response_language"] == "hi"
        assert translations["legal_aid"] == "कानूनी सहायता"
    
    def test_unsupported_language_fallback(self):
        """Test that unsupported languages fall back to English."""
        # French query (unsupported)
        query = "J'ai besoin d'aide juridique"
        
        # Detect language (should default to English)
        lang_info = self.ml_service.process_query_language(query)
        detected_lang = lang_info["response_language"]
        
        # Get translations (should be English)
        translations = self.trans_service.get_all_translations(detected_lang)
        
        assert detected_lang == "en"
        assert translations["welcome"] == "Welcome to Nyaya Mitra"
    
    def test_all_supported_languages_have_complete_translations(self):
        """Test that all supported languages have complete UI translations."""
        ml_languages = self.ml_service.get_supported_languages()
        
        # Get English translations as reference
        en_translations = self.trans_service.get_all_translations("en")
        en_keys = set(en_translations.keys())
        
        # Check each supported language
        for lang_code in ml_languages.keys():
            translations = self.trans_service.get_all_translations(lang_code)
            lang_keys = set(translations.keys())
            
            # All languages should have the same keys as English
            assert lang_keys == en_keys, f"Language {lang_code} missing keys: {en_keys - lang_keys}"
    
    def test_legal_terms_consistency(self):
        """Test that legal terms are consistently translated."""
        legal_terms = ["case_analysis", "evidence_guide", "legal_aid", "emergency"]
        
        for lang in ["en", "hi", "ta"]:
            translations = self.trans_service.get_all_translations(lang)
            
            for term in legal_terms:
                # Each term should have a non-empty translation
                assert term in translations
                assert translations[term]
                assert isinstance(translations[term], str)


class TestTranslationWorkflow:
    """Test complete translation workflow scenarios."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.ml_service = get_multilingual_service()
        self.trans_service = get_translation_service()
    
    def test_complete_chat_workflow(self):
        """Test complete chat workflow with translations."""
        # User submits query in Hindi
        user_query = "मुझे कानूनी सहायता चाहिए"
        
        # Step 1: Detect language
        lang_info = self.ml_service.process_query_language(user_query)
        lang = lang_info["response_language"]
        
        # Step 2: Get UI translations
        ui_translations = self.trans_service.get_all_translations(lang)
        
        # Step 3: Prepare prompt
        base_prompt = "You are a legal assistant."
        enhanced_prompt = self.ml_service.prepare_multilingual_prompt(
            base_prompt,
            lang
        )
        
        # Step 4: Simulate AI response
        ai_response = "यह कानूनी सलाह है।"
        
        # Step 5: Add disclaimer
        final_response = self.ml_service.add_language_disclaimer(
            ai_response,
            lang,
            add_disclaimer=True
        )
        
        # Verify workflow
        assert lang in ["hi", "mr", "gu", "bn"]  # Indic language detected
        assert "chat_title" in ui_translations
        assert enhanced_prompt  # Prompt should be enhanced
        assert "⚠️" in final_response  # Disclaimer added
    
    def test_complete_document_generation_workflow(self):
        """Test complete document generation workflow with translations."""
        # User wants to generate document in Tamil
        preferred_lang = "ta"
        
        # Get UI translations
        ui_translations = self.trans_service.get_all_translations(preferred_lang)
        
        # Verify document-related translations
        assert ui_translations["document_generator"] == "ஆவண உருவாக்கி"
        assert ui_translations["legal_letter"] == "சட்ட கடிதம்"
        assert ui_translations["generate_document"] == "ஆவணத்தை உருவாக்கு"
        assert ui_translations["download_pdf"] == "PDF பதிவிறக்கம்"
    
    def test_complete_legal_aid_search_workflow(self):
        """Test complete legal aid search workflow with translations."""
        # User searches for legal aid in Hindi
        query = "मुझे वकील चाहिए"
        
        # Detect language
        lang_info = self.ml_service.process_query_language(query)
        lang = lang_info["response_language"]
        
        # Get UI translations
        ui_translations = self.trans_service.get_all_translations(lang)
        
        # Verify legal aid translations exist
        assert lang in ["hi", "mr", "gu", "bn"]  # Indic language detected
        assert "legal_aid" in ui_translations
        assert "find_legal_aid" in ui_translations
        assert "location" in ui_translations
        assert "contact_info" in ui_translations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
