import boto3
import json
import os
from typing import Dict, List, Optional, Any, Generator

class BedrockClient:
    """
    Client for interacting with Amazon Bedrock models.
    Supports Claude 3 (Haiku/Sonnet) and Llama 3 models.
    """
    def __init__(self, region: str = "us-east-1", model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"):
        self.region = region
        self.model_id = model_id
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region
        )

    def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Generate a complete response from the Bedrock model.
        """
        # Format for Claude 3
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        if system_prompt:
            body["system"] = system_prompt

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response.get("body").read())
            return response_body.get("content", [{}])[0].get("text", "")
            
        except Exception as e:
            return f"Error calling Amazon Bedrock: {str(e)}"

    def stream_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Stream response from Bedrock (Claude 3 format).
        """
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system_prompt:
            body["system"] = system_prompt

        try:
            response = self.client.invoke_model_with_response_stream(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            for event in response.get("body"):
                chunk = json.loads(event.get("chunk").get("bytes").decode())
                if chunk.get("type") == "content_block_delta":
                    yield chunk.get("delta", {}).get("text", "")
                    
        except Exception as e:
            yield f"Error streaming from Bedrock: {str(e)}"
