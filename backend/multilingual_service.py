"""
Multilingual query processing service for language detection and translation.
"""
from typing import Dict, Optional, List
from langdetect import detect, LangDetectException
from langdetect import DetectorFactory

# Set seed for consistent language detection
DetectorFactory.seed = 0


class MultilingualService:
    """Service for handling multilingual queries and responses."""
    
    # Supported languages mapping
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "Hindi",
        "ta": "Tamil",
        "te": "Telugu",
        "bn": "Bengali",
        "mr": "Marathi",
        "gu": "Gujarati"
    }
    
    # Language-specific legal prompt templates
    LANGUAGE_PROMPTS = {
        "en": {
            "system_suffix": "\n\nRespond in English with clear, simple language.",
            "disclaimer": "\n\n⚠️ Please note: I have limited information on this topic. I strongly recommend consulting with a qualified legal professional for accurate advice specific to your situation."
        },
        "hi": {
            "system_suffix": "\n\nहिंदी में स्पष्ट और सरल भाषा में जवाब दें।",
            "disclaimer": "\n\n⚠️ कृपया ध्यान दें: मेरे पास इस विषय पर सीमित जानकारी है। मैं दृढ़ता से अनुशंसा करता हूं कि आप अपनी स्थिति के लिए सटीक सलाह के लिए एक योग्य कानूनी पेशेवर से परामर्श करें।"
        },
        "ta": {
            "system_suffix": "\n\nதெளிவான மற்றும் எளிய மொழியில் தமிழில் பதிலளிக்கவும்.",
            "disclaimer": "\n\n⚠️ தயவுசெய்து கவனிக்கவும்: இந்த தலைப்பில் எனக்கு வரையறுக்கப்பட்ட தகவல் உள்ளது. உங்கள் சூழ்நிலைக்கு குறிப்பிட்ட துல்லியமான ஆலோசனைக்கு தகுதியான சட்ட நிபுணரை அணுகுமாறு நான் கடுமையாக பரிந்துரைக்கிறேன்."
        },
        "te": {
            "system_suffix": "\n\nస్పష్టమైన మరియు సరళమైన భాషలో తెలుగులో స్పందించండి.",
            "disclaimer": "\n\n⚠️ దయచేసి గమనించండి: ఈ అంశంపై నాకు పరిమిత సమాచారం ఉంది. మీ పరిస్థితికి నిర్దిష్టమైన ఖచ్చితమైన సలహా కోసం అర్హత కలిగిన న్యాయ నిపుణుడిని సంప్రదించమని నేను గట్టిగా సిఫార్సు చేస్తున్నాను."
        },
        "bn": {
            "system_suffix": "\n\nস্পষ্ট এবং সহজ ভাষায় বাংলায় উত্তর দিন।",
            "disclaimer": "\n\n⚠️ অনুগ্রহ করে মনে রাখবেন: এই বিষয়ে আমার সীমিত তথ্য আছে। আমি দৃঢ়ভাবে সুপারিশ করছি যে আপনার পরিস্থিতির জন্য সঠিক পরামর্শের জন্য একজন যোগ্য আইনি পেশাদারের সাথে পরামর্শ করুন।"
        },
        "mr": {
            "system_suffix": "\n\nस्पष्ट आणि सोप्या भाषेत मराठीत उत्तर द्या.",
            "disclaimer": "\n\n⚠️ कृपया लक्षात घ्या: या विषयावर माझ्याकडे मर्यादित माहिती आहे. मी जोरदार शिफारस करतो की तुम्ही तुमच्या परिस्थितीसाठी अचूक सल्ल्यासाठी पात्र कायदेशीर व्यावसायिकाचा सल्ला घ्या."
        },
        "gu": {
            "system_suffix": "\n\nસ્પષ્ટ અને સરળ ભાષામાં ગુજરાતીમાં જવાબ આપો.",
            "disclaimer": "\n\n⚠️ કૃપા કરીને નોંધ લો: આ વિષય પર મારી પાસે મર્યાદિત માહિતી છે. હું ભારપૂર્વક ભલામણ કરું છું કે તમે તમારી પરિસ્થિતિ માટે ચોક્કસ સલાહ માટે લાયક કાનૂની વ્યાવસાયિકની સલાહ લો."
        }
    }
    
    def __init__(self):
        """Initialize multilingual service."""
        pass
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of input text.
        
        Args:
            text: Input text to detect language
            
        Returns:
            ISO 639-1 language code (e.g., 'en', 'hi', 'ta')
            Returns 'en' as default if detection fails
        """
        if not text or not text.strip():
            return "en"
        
        try:
            detected_lang = detect(text)
            
            # Map to supported languages
            if detected_lang in self.SUPPORTED_LANGUAGES:
                return detected_lang
            
            # Default to English for unsupported languages
            return "en"
            
        except LangDetectException:
            # Default to English if detection fails
            return "en"
    
    def is_language_supported(self, language_code: str) -> bool:
        """
        Check if a language is supported.
        
        Args:
            language_code: ISO 639-1 language code
            
        Returns:
            True if language is supported, False otherwise
        """
        return language_code in self.SUPPORTED_LANGUAGES
    
    def get_language_name(self, language_code: str) -> str:
        """
        Get the full name of a language from its code.
        
        Args:
            language_code: ISO 639-1 language code
            
        Returns:
            Full language name or "Unknown" if not supported
        """
        return self.SUPPORTED_LANGUAGES.get(language_code, "Unknown")
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get all supported languages.
        
        Returns:
            Dictionary mapping language codes to names
        """
        return self.SUPPORTED_LANGUAGES.copy()
    
    def get_language_prompt_suffix(self, language_code: str) -> str:
        """
        Get language-specific prompt suffix for system prompt.
        
        Args:
            language_code: ISO 639-1 language code
            
        Returns:
            Language-specific prompt suffix
        """
        if language_code not in self.LANGUAGE_PROMPTS:
            language_code = "en"
        
        return self.LANGUAGE_PROMPTS[language_code]["system_suffix"]
    
    def get_language_disclaimer(self, language_code: str) -> str:
        """
        Get language-specific disclaimer text.
        
        Args:
            language_code: ISO 639-1 language code
            
        Returns:
            Language-specific disclaimer text
        """
        if language_code not in self.LANGUAGE_PROMPTS:
            language_code = "en"
        
        return self.LANGUAGE_PROMPTS[language_code]["disclaimer"]
    
    def prepare_multilingual_prompt(
        self,
        base_prompt: str,
        language_code: str
    ) -> str:
        """
        Prepare a prompt with language-specific instructions.
        
        Args:
            base_prompt: Base system prompt
            language_code: Target language code
            
        Returns:
            Enhanced prompt with language instructions
        """
        suffix = self.get_language_prompt_suffix(language_code)
        return base_prompt + suffix
    
    def add_language_disclaimer(
        self,
        response: str,
        language_code: str,
        add_disclaimer: bool = True
    ) -> str:
        """
        Add language-specific disclaimer to response if needed.
        
        Args:
            response: Original response text
            language_code: Language code
            add_disclaimer: Whether to add disclaimer
            
        Returns:
            Response with disclaimer if applicable
        """
        if not add_disclaimer:
            return response
        
        disclaimer = self.get_language_disclaimer(language_code)
        return response + disclaimer
    
    def process_query_language(
        self,
        query: str,
        preferred_language: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Process query to determine language and prepare for processing.
        
        Args:
            query: User query text
            preferred_language: User's preferred language (optional)
            
        Returns:
            Dictionary with detected_language and response_language
        """
        # Detect language from query
        detected_language = self.detect_language(query)
        
        # Use preferred language if provided and supported
        if preferred_language and self.is_language_supported(preferred_language):
            response_language = preferred_language
        else:
            response_language = detected_language
        
        return {
            "detected_language": detected_language,
            "response_language": response_language,
            "language_name": self.get_language_name(response_language)
        }


# Singleton instance
_multilingual_service: Optional[MultilingualService] = None


def get_multilingual_service() -> MultilingualService:
    """
    Get or create singleton multilingual service instance.
    
    Returns:
        MultilingualService instance
    """
    global _multilingual_service
    if _multilingual_service is None:
        _multilingual_service = MultilingualService()
    return _multilingual_service
