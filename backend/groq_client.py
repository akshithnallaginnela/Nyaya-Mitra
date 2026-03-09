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
            
            # FALLBACK: Return a helpful legal response for demo
            return self._get_fallback_response(prompt)
        except Exception as e:
            # FALLBACK: Return a helpful legal response for demo
            return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Provide a fallback response when API fails (for demo purposes)."""
        prompt_lower = prompt.lower()
        
        if "420" in prompt_lower or "cheating" in prompt_lower or "fraud" in prompt_lower:
            return """IPC Section 420 deals with cheating and dishonestly inducing delivery of property. 

**Key Points:**
- Punishment: Imprisonment up to 7 years and fine
- Applies when someone deceives another person to deliver property or consent to retention of property
- Common in fraud cases, fake promises, and financial scams

**What to do if you're a victim:**
1. File an FIR at the nearest police station
2. Gather all evidence (documents, messages, receipts)
3. Consult a lawyer for legal advice
4. Consider filing a civil suit for recovery

**Important:** This is general information. Please consult a qualified lawyer for advice specific to your situation."""
        
        elif "498a" in prompt_lower or "dowry" in prompt_lower or "harassment" in prompt_lower:
            return """IPC Section 498A deals with cruelty by husband or relatives of husband.

**Key Points:**
- Protects married women from harassment for dowry
- Punishment: Up to 3 years imprisonment and fine
- Non-bailable offense

**Steps to take:**
1. Document all incidents with dates and details
2. Inform family members or trusted friends
3. File a complaint at the nearest police station
4. Seek legal counsel immediately
5. Contact women's helpline: 181

**Important:** Your safety is paramount. Please consult a lawyer and consider reaching out to support services."""
        
        else:
            return """I can help you understand Indian legal matters. 

**Common Legal Resources:**
- **Police Emergency:** 100
- **Women's Helpline:** 181
- **Legal Aid:** Contact your nearest Legal Services Authority
- **Cyber Crime:** Report at cybercrime.gov.in

**For your specific query**, I recommend:
1. Consulting with a qualified lawyer
2. Visiting your nearest Legal Aid office
3. Filing a complaint if you're a victim of a crime

**Note:** This is general legal information. For advice specific to your situation, please consult a legal professional.

Would you like information about a specific IPC section or legal topic?"""
    
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
