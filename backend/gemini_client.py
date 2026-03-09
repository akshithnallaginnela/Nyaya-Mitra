"""
Google Gemini API client for AI inference.
"""
import os
import requests
from typing import Dict, Optional

class GeminiClient:
    """Client for interacting with Google Gemini API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = "gemini-1.5-flash"
        self.base_url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent"
        
    def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Generate a complete response from Gemini."""
        
        # Combine system prompt and user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        url = f"{self.base_url}?key={self.api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": full_prompt
                }]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract text from Gemini response
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]
            
            return "I apologize, but I couldn't generate a response. Please try again."
            
        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_detail = e.response.json()
            except:
                error_detail = e.response.text
            return f"Error calling Gemini API: {e}. Details: {error_detail}"
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[list] = None,
        temperature: float = 0.7
    ) -> Dict:
        """Generate response with context (compatible with existing code)."""
        
        response_text = self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )
        
        return {
            "response": response_text,
            "model": self.model
        }


def get_gemini_client() -> GeminiClient:
    """Get Gemini client instance."""
    return GeminiClient()
