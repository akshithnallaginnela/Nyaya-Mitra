"""
Groq API client for fast LLM inference.
"""
import os
import requests
from typing import Dict, Optional

class GroqClient:
    """Client for interacting with Groq API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama3-8b-8192"  # Current Groq model
        
    def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Generate a complete response from Groq."""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_detail = e.response.json()
            except:
                error_detail = e.response.text
            return f"Error calling Groq API: {e}. Details: {error_detail}"
        except Exception as e:
            return f"Error calling Groq API: {str(e)}"
    
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


def get_groq_client() -> GroqClient:
    """Get Groq client instance."""
    return GroqClient()
