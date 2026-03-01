"""
Tests for Ollama client.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from ollama_client import OllamaClient, get_ollama_client


class TestOllamaClient:
    """Test suite for OllamaClient."""
    
    def test_initialization_default_values(self):
        """Test client initialization with default values."""
        client = OllamaClient()
        assert client.base_url == "http://localhost:11434"
        assert client.model == "mistral:7b"
        assert client.temperature == 0.3
        assert client.timeout == 30
    
    def test_initialization_custom_values(self):
        """Test client initialization with custom values."""
        client = OllamaClient(
            base_url="http://custom:8080",
            model="llama2:13b",
            temperature=0.7
        )
        assert client.base_url == "http://custom:8080"
        assert client.model == "llama2:13b"
        assert client.temperature == 0.7
    
    @patch.dict('os.environ', {'OLLAMA_BASE_URL': 'http://env:9090'})
    def test_initialization_from_env(self):
        """Test client initialization from environment variable."""
        client = OllamaClient()
        assert client.base_url == "http://env:9090"
    
    @patch('requests.get')
    def test_is_available_success(self, mock_get):
        """Test is_available returns True when service is running."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        client = OllamaClient()
        assert client.is_available() is True
        mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=5)
    
    @patch('requests.get')
    def test_is_available_failure(self, mock_get):
        """Test is_available returns False when service is not running."""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        client = OllamaClient()
        assert client.is_available() is False
    
    @patch('requests.get')
    def test_list_models_success(self, mock_get):
        """Test list_models returns model list."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "mistral:7b", "size": 4109865159},
                {"name": "llama2:13b", "size": 7365960935}
            ]
        }
        mock_get.return_value = mock_response
        
        client = OllamaClient()
        models = client.list_models()
        
        assert len(models) == 2
        assert models[0]["name"] == "mistral:7b"
        assert models[1]["name"] == "llama2:13b"
    
    @patch('requests.get')
    def test_list_models_failure(self, mock_get):
        """Test list_models raises error on failure."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        client = OllamaClient()
        with pytest.raises(RuntimeError, match="Failed to list models"):
            client.list_models()
    
    @patch('requests.get')
    def test_is_model_available_true(self, mock_get):
        """Test is_model_available returns True when model exists."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "mistral:7b", "size": 4109865159}
            ]
        }
        mock_get.return_value = mock_response
        
        client = OllamaClient()
        assert client.is_model_available("mistral:7b") is True
    
    @patch('requests.get')
    def test_is_model_available_false(self, mock_get):
        """Test is_model_available returns False when model doesn't exist."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": []}
        mock_get.return_value = mock_response
        
        client = OllamaClient()
        assert client.is_model_available("nonexistent:model") is False

    
    @patch('requests.get')
    @patch('requests.post')
    def test_generate_success(self, mock_post, mock_get):
        """Test generate returns response successfully."""
        # Mock is_available check
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response
        
        # Mock generate response
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "model": "mistral:7b",
            "created_at": "2024-01-01T00:00:00Z",
            "message": {
                "role": "assistant",
                "content": "This is a test response"
            },
            "done": True,
            "total_duration": 1000000000,
            "prompt_eval_count": 10,
            "eval_count": 20
        }
        mock_post.return_value = mock_post_response
        
        client = OllamaClient()
        result = client.generate("Test prompt")
        
        assert result["response"] == "This is a test response"
        assert result["model"] == "mistral:7b"
        assert result["done"] is True
        assert result["total_duration"] == 1000000000
        assert result["prompt_eval_count"] == 10
        assert result["eval_count"] == 20
    
    @patch('requests.get')
    @patch('requests.post')
    def test_generate_with_system_prompt(self, mock_post, mock_get):
        """Test generate with system prompt."""
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response
        
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "model": "mistral:7b",
            "message": {"role": "assistant", "content": "Response"},
            "done": True
        }
        mock_post.return_value = mock_post_response
        
        client = OllamaClient()
        client.generate("User prompt", system_prompt="You are a legal assistant")
        
        # Verify the request payload includes system message
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert len(payload["messages"]) == 2
        assert payload["messages"][0]["role"] == "system"
        assert payload["messages"][0]["content"] == "You are a legal assistant"
        assert payload["messages"][1]["role"] == "user"
        assert payload["messages"][1]["content"] == "User prompt"
    
    @patch('requests.get')
    @patch('requests.post')
    def test_generate_with_context(self, mock_post, mock_get):
        """Test generate with conversation context."""
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response
        
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "model": "mistral:7b",
            "message": {"role": "assistant", "content": "Response"},
            "done": True
        }
        mock_post.return_value = mock_post_response
        
        context = [
            {"role": "user", "content": "Previous question"},
            {"role": "assistant", "content": "Previous answer"}
        ]
        
        client = OllamaClient()
        client.generate("New question", context=context)
        
        # Verify the request payload includes context
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert len(payload["messages"]) == 3
        assert payload["messages"][0] == context[0]
        assert payload["messages"][1] == context[1]
        assert payload["messages"][2]["role"] == "user"
        assert payload["messages"][2]["content"] == "New question"
    
    @patch('requests.get')
    @patch('requests.post')
    def test_generate_with_custom_temperature(self, mock_post, mock_get):
        """Test generate with custom temperature."""
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response
        
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "model": "mistral:7b",
            "message": {"role": "assistant", "content": "Response"},
            "done": True
        }
        mock_post.return_value = mock_post_response
        
        client = OllamaClient()
        client.generate("Test", temperature=0.8)
        
        # Verify temperature in request
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert payload["options"]["temperature"] == 0.8
    
    @patch('requests.get')
    @patch('requests.post')
    def test_generate_with_max_tokens(self, mock_post, mock_get):
        """Test generate with max tokens limit."""
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response
        
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "model": "mistral:7b",
            "message": {"role": "assistant", "content": "Response"},
            "done": True
        }
        mock_post.return_value = mock_post_response
        
        client = OllamaClient()
        client.generate("Test", max_tokens=100)
        
        # Verify max tokens in request
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert payload["options"]["num_predict"] == 100
    
    @patch('requests.get')
    def test_generate_service_unavailable(self, mock_get):
        """Test generate raises error when service is unavailable."""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        client = OllamaClient()
        with pytest.raises(RuntimeError, match="Ollama service is not available"):
            client.generate("Test")
    
    @patch('requests.get')
    @patch('requests.post')
    def test_generate_timeout(self, mock_post, mock_get):
        """Test generate handles timeout."""
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response
        
        mock_post.side_effect = requests.exceptions.Timeout()
        
        client = OllamaClient()
        with pytest.raises(RuntimeError, match="Request to Ollama timed out"):
            client.generate("Test")
    
    @patch('requests.get')
    @patch('requests.post')
    def test_generate_request_error(self, mock_post, mock_get):
        """Test generate handles request errors."""
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response
        
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        
        client = OllamaClient()
        with pytest.raises(RuntimeError, match="Failed to generate response"):
            client.generate("Test")
    
    @patch('requests.get')
    @patch('requests.post')
    def test_generate_stream_success(self, mock_post, mock_get):
        """Test generate_stream yields response chunks."""
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get.return_value = mock_get_response
        
        # Mock streaming response
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.iter_lines.return_value = [
            b'{"message": {"content": "Hello"}, "done": false}',
            b'{"message": {"content": " world"}, "done": false}',
            b'{"message": {"content": "!"}, "done": true}'
        ]
        mock_post.return_value = mock_post_response
        
        client = OllamaClient()
        chunks = list(client.generate_stream("Test"))
        
        assert len(chunks) == 3
        assert chunks[0]["message"]["content"] == "Hello"
        assert chunks[1]["message"]["content"] == " world"
        assert chunks[2]["message"]["content"] == "!"
        assert chunks[2]["done"] is True
    
    @patch('requests.get')
    def test_generate_stream_service_unavailable(self, mock_get):
        """Test generate_stream raises error when service is unavailable."""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        client = OllamaClient()
        with pytest.raises(RuntimeError, match="Ollama service is not available"):
            list(client.generate_stream("Test"))
    
    @patch('requests.post')
    def test_pull_model_success(self, mock_post):
        """Test pull_model successfully downloads model."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        result = client.pull_model("mistral:7b")
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_pull_model_failure(self, mock_post):
        """Test pull_model handles errors."""
        mock_post.side_effect = requests.exceptions.RequestException("Download failed")
        
        client = OllamaClient()
        with pytest.raises(RuntimeError, match="Failed to pull model"):
            client.pull_model("mistral:7b")


def test_get_ollama_client_singleton():
    """Test get_ollama_client returns singleton instance."""
    client1 = get_ollama_client()
    client2 = get_ollama_client()
    
    assert client1 is client2


def test_get_ollama_client_creates_instance():
    """Test get_ollama_client creates OllamaClient instance."""
    # Reset singleton
    import ollama_client
    ollama_client._ollama_client = None
    
    client = get_ollama_client()
    assert isinstance(client, OllamaClient)
