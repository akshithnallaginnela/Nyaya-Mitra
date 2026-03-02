"""
Ollama client for AI response generation using Mistral 7B model.
"""
import os
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class OllamaClient:
    """Client for interacting with Ollama API for AI response generation."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3
    ):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Base URL for Ollama API (default: http://localhost:11434)
            model: Model name to use (reads OLLAMA_MODEL env var, fallback: mistral:7b)
            temperature: Temperature for response generation (default: 0.3 for consistency)
        """
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "mistral:7b")
        self.temperature = temperature
        self.timeout = 300  # 5 minute timeout - local LLM can be slow on CPU
        
    def is_available(self) -> bool:
        """
        Check if Ollama service is available.
        
        Returns:
            True if Ollama is running and accessible, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models in Ollama.
        
        Returns:
            List of model information dictionaries
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            return response.json().get("models", [])
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to list models: {str(e)}")
    
    def is_model_available(self, model_name: Optional[str] = None) -> bool:
        """
        Check if a specific model is available.
        
        Args:
            model_name: Model name to check (default: self.model)
            
        Returns:
            True if model is available, False otherwise
        """
        model_name = model_name or self.model
        try:
            models = self.list_models()
            return any(model.get("name") == model_name for model in models)
        except RuntimeError:
            return False

    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from the model.
        
        Args:
            prompt: User prompt/query
            system_prompt: System prompt to guide model behavior
            context: Previous conversation context as list of {"role": "user/assistant", "content": "..."}
            temperature: Override default temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dictionary with response and metadata:
            {
                "response": str,
                "model": str,
                "created_at": str,
                "done": bool,
                "total_duration": int (nanoseconds),
                "prompt_eval_count": int,
                "eval_count": int
            }
        """
        if not self.is_available():
            raise RuntimeError("Ollama service is not available")
        
        # Build messages for chat format
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if context:
            messages.extend(context)
        
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request payload
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature if temperature is not None else self.temperature
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract response text from message
            response_text = result.get("message", {}).get("content", "")
            
            return {
                "response": response_text,
                "model": result.get("model", self.model),
                "created_at": result.get("created_at", datetime.utcnow().isoformat()),
                "done": result.get("done", True),
                "total_duration": result.get("total_duration", 0),
                "prompt_eval_count": result.get("prompt_eval_count", 0),
                "eval_count": result.get("eval_count", 0)
            }
        except requests.exceptions.Timeout:
            raise RuntimeError("Request to Ollama timed out")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to generate response: {str(e)}")
    
    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
        temperature: Optional[float] = None
    ):
        """
        Generate a streaming response from the model.
        
        Args:
            prompt: User prompt/query
            system_prompt: System prompt to guide model behavior
            context: Previous conversation context
            temperature: Override default temperature
            
        Yields:
            Dictionary chunks with partial responses
        """
        if not self.is_available():
            raise RuntimeError("Ollama service is not available")
        
        # Build messages
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if context:
            messages.extend(context)
        
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request payload
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature if temperature is not None else self.temperature
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=True,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    import json
                    chunk = json.loads(line)
                    yield chunk
                    
        except requests.exceptions.Timeout:
            raise RuntimeError("Request to Ollama timed out")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to generate streaming response: {str(e)}")
    
    def pull_model(self, model_name: Optional[str] = None) -> bool:
        """
        Pull/download a model from Ollama library.
        
        Args:
            model_name: Model name to pull (default: self.model)
            
        Returns:
            True if successful, False otherwise
        """
        model_name = model_name or self.model
        
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=300  # 5 minute timeout for model download
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to pull model: {str(e)}")


# Singleton instance
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """
    Get or create singleton Ollama client instance.
    
    Returns:
        OllamaClient instance
    """
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client
