# Nyaya Mitra Backend Tests

This directory contains all test files for the Nyaya Mitra backend.

## Test Organization

### Unit Tests
Tests for individual components and services:
- `test_user_model.py` - User model and authentication
- `test_conversation_models.py` - Conversation and message models
- `test_case_document_models.py` - Case analysis and document models
- `test_legal_aid_provider_model.py` - Legal aid provider model
- `test_database.py` - Database connection and session management
- `test_jwt_utils.py` - JWT token generation and validation
- `test_ollama_client.py` - Ollama API client
- `test_vector_db.py` - Vector database operations
- `test_rag_system.py` - RAG retrieval system
- `test_langchain_service.py` - LangChain orchestration
- `test_multilingual_service.py` - Language detection and processing
- `test_translation_service.py` - UI translation service
- `test_case_analysis_service.py` - Case validity scoring
- `test_action_plan_service.py` - Action plan generation
- `test_document_generator_service.py` - Document generation
- `test_attachment_checklist.py` - Attachment checklist generation
- `test_legal_aid_search_service.py` - Legal aid search logic
- `test_seed_legal_aid_providers.py` - Legal aid provider seeding

### Integration Tests
Tests for API endpoints and service integration:
- `test_auth_endpoints.py` - Authentication API endpoints
- `test_chat_endpoints.py` - Chat API endpoints
- `test_websocket_stream.py` - WebSocket streaming
- `test_case_endpoints.py` - Case analysis endpoints (if exists)
- `test_document_endpoints.py` - Document generation endpoints
- `test_attachment_api.py` - Attachment checklist API
- `test_legal_aid_endpoints.py` - Legal aid search endpoints
- `test_action_plan_integration.py` - Action plan integration with chat
- `test_document_generator_integration.py` - Document generation integration
- `test_attachment_checklist_integration.py` - Attachment checklist integration
- `test_translation_integration.py` - Translation service integration
- `test_document_ingestion.py` - Document ingestion pipeline
- `test_document_templates.py` - Jinja2 template rendering

### Manual Tests
Scripts for manual testing:
- `test_websocket_manual.py` - Manual WebSocket testing
- `test_legal_aid_api_manual.py` - Manual legal aid API testing

### Verification Scripts
Scripts to verify implementation:
- `verify_user_model.py` - Verify user model implementation
- `verify_conversation_models.py` - Verify conversation models
- `verify_case_document_models.py` - Verify case and document models
- `verify_implementation.py` - Overall implementation verification

## Running Tests

### Run All Tests
```bash
cd backend
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_user_model.py -v
```

### Run Tests by Category
```bash
# Unit tests only
pytest tests/test_*_model.py tests/test_*_service.py -v

# Integration tests only
pytest tests/test_*_endpoints.py tests/test_*_integration.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

### Run Specific Test Class or Function
```bash
pytest tests/test_user_model.py::TestUserModelCreation -v
pytest tests/test_auth_endpoints.py::test_register_success -v
```

## Test Database Files

Test database files (`.db` files) are created during test execution and stored in this directory. They are automatically cleaned up after tests complete.

## Requirements

All test dependencies are listed in `requirements.txt`:
- pytest
- pytest-asyncio
- pytest-cov
- httpx (for FastAPI testing)
- sqlalchemy
- And all other backend dependencies

## Writing New Tests

When adding new tests:
1. Create test file with `test_` prefix
2. Use pytest fixtures for setup/teardown
3. Follow existing test patterns
4. Add docstrings to test functions
5. Group related tests in classes
6. Use descriptive test names

Example:
```python
import pytest

class TestMyFeature:
    """Test suite for my feature."""
    
    def test_basic_functionality(self):
        """Test basic functionality works correctly."""
        # Arrange
        # Act
        # Assert
        pass
```

## CI/CD Integration

These tests are run automatically in the CI/CD pipeline on every commit. All tests must pass before code can be merged.
