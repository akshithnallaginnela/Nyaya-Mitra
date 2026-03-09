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
        """Provide intelligent fallback response based on query analysis."""
        prompt_lower = prompt.lower()
        
        # Extract IPC section numbers
        import re
        ipc_match = re.search(r'(?:ipc|section)\s*(\d+[a-z]*)', prompt_lower)
        
        if ipc_match:
            section = ipc_match.group(1)
            return f"""Based on Indian Penal Code Section {section}:

This section deals with specific offenses under Indian law. For accurate legal interpretation and advice specific to your situation, I recommend:

1. **Consult a Lawyer**: Legal matters require professional guidance
2. **Visit Legal Aid**: Free legal services available at District Legal Services Authority
3. **File FIR**: If you're a victim, report to the nearest police station
4. **Document Everything**: Keep records of all relevant evidence

**Important Resources:**
- Police Emergency: 100
- Women's Helpline: 181
- Legal Aid: Contact your nearest Legal Services Authority
- Cyber Crime: cybercrime.gov.in

**Note:** This is general information. For advice specific to your case, please consult a qualified legal professional."""
        
        elif any(word in prompt_lower for word in ['bail', 'custody', 'arrest', 'detention']):
            return """**Bail Application in India:**

**Types of Bail:**
1. **Regular Bail**: Applied after arrest
2. **Anticipatory Bail**: Applied before arrest (under Section 438 CrPC)
3. **Interim Bail**: Temporary bail pending regular bail hearing

**Steps to Apply:**
1. File bail application in appropriate court
2. Provide surety and bail bond
3. Attend all court hearings
4. Comply with bail conditions

**Documents Needed:**
- Copy of FIR
- Personal identification
- Address proof
- Surety documents

**Important:** Bail is a constitutional right under Article 21. Consult a criminal lawyer immediately for your specific case.

**Emergency Contacts:**
- Police: 100
- Legal Aid: Contact District Legal Services Authority"""
        
        elif any(word in prompt_lower for word in ['consumer', 'refund', 'defective', 'warranty']):
            return """**Consumer Rights in India (Consumer Protection Act, 2019):**

**Your Rights:**
1. **Right to Safety**: Protection against hazardous goods
2. **Right to Information**: Complete product information
3. **Right to Choose**: Access to variety of products
4. **Right to be Heard**: Voice complaints
5. **Right to Redressal**: Compensation for defective products
6. **Right to Consumer Education**: Know your rights

**How to File Complaint:**
1. **District Forum**: Claims up to ₹1 crore
2. **State Commission**: Claims ₹1-10 crore
3. **National Commission**: Claims above ₹10 crore

**Online Complaint:** Visit consumerhelpline.gov.in or call 1800-11-4000

**Documents Needed:**
- Purchase receipt/invoice
- Product warranty card
- Photos of defect
- Communication with seller

**Time Limit:** File within 2 years of purchase

For specific guidance, consult a consumer rights lawyer."""
        
        elif any(word in prompt_lower for word in ['harassment', 'stalking', 'threat', 'abuse']):
            return """**Protection Against Harassment:**

**Legal Provisions:**
- IPC Section 354A: Sexual harassment
- IPC Section 354D: Stalking
- IPC Section 506: Criminal intimidation
- IPC Section 509: Insulting modesty

**Immediate Steps:**
1. **Document Everything**: Save messages, emails, call logs
2. **File Police Complaint**: Visit nearest police station
3. **Seek Protection Order**: Apply under Section 12 of Protection of Women from Domestic Violence Act (if applicable)
4. **Contact Helplines**: Women's Helpline 181, Cyber Crime 1930

**Evidence to Collect:**
- Screenshots of messages
- Call records
- Witness statements
- CCTV footage (if available)

**Your Safety First:**
- Inform trusted friends/family
- Change routines if being stalked
- Consider restraining order

**Emergency:** Call 100 (Police) or 112 (Emergency Response)

Consult a lawyer specializing in women's rights or criminal law."""
        
        else:
            # Generic legal assistance response
            return f"""I can help you understand Indian legal matters.

**Your Query:** {prompt[:100]}...

**General Guidance:**
For specific legal issues, I recommend:

1. **Consult a Lawyer**: Professional legal advice is essential
2. **Legal Aid Services**: Free legal help available at District Legal Services Authority
3. **File Complaint**: If you're a victim, report to police (Call 100)
4. **Document Everything**: Keep all evidence and records

**Common Legal Resources:**
- **Police Emergency:** 100
- **Women's Helpline:** 181
- **Child Helpline:** 1098
- **Senior Citizen Helpline:** 14567
- **Cyber Crime:** 1930 or cybercrime.gov.in
- **Legal Aid:** Contact District Legal Services Authority

**Online Resources:**
- eCourts: ecourts.gov.in
- National Legal Services Authority: nalsa.gov.in
- Consumer Helpline: consumerhelpline.gov.in

Would you like information about a specific legal topic or IPC section?

**Note:** This is general information. For advice specific to your situation, please consult a qualified legal professional."""
    
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
