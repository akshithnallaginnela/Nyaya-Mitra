"""
Unit tests for document generation endpoints

Tests the document generation API endpoints including:
- GET /api/documents/templates - List available templates
- POST /api/documents/generate - Generate document from template
- GET /api/documents/{id} - Retrieve generated document
- GET /api/documents/ - List user's documents

Requirements: 4.1, 4.2
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import shutil
import json

from main import app
from database import Base, get_db, get_db_session
from models.user import User
from models.generated_document import GeneratedDocument
from utils.jwt import create_access_token
import bcrypt


# Test database setup - Use in-memory SQLite with TypeDecorator for UUID
from sqlalchemy import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid


class GUID(TypeDecorator):
    """Platform-independent GUID type. Uses PostgreSQL's UUID type, otherwise uses CHAR(36)."""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            else:
                return str(uuid.UUID(value))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if isinstance(value, uuid.UUID):
                return value
            else:
                return uuid.UUID(value)


TEST_DATABASE_URL = "sqlite:///./test_document_endpoints.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override both database dependencies
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_db_session] = override_get_db


@pytest.fixture(scope="function")
def test_db():
    """Create test database and tables using raw SQL to avoid UUID issues"""
    # Create tables with raw SQL
    with engine.connect() as conn:
        # Create users table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                college_name TEXT,
                preferred_language TEXT NOT NULL DEFAULT 'en',
                last_login TIMESTAMP,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            )
        """))
        
        # Create generated_documents table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS generated_documents (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                document_type TEXT NOT NULL,
                template_inputs TEXT NOT NULL,
                file_path TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        conn.commit()
    
    yield
    
    # Drop tables
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS generated_documents"))
        conn.execute(text("DROP TABLE IF EXISTS users"))
        conn.commit()
    
    # Clean up generated documents directory
    docs_dir = Path("generated_documents")
    if docs_dir.exists():
        shutil.rmtree(docs_dir)


@pytest.fixture
def test_user(test_db):
    """Create a test user"""
    db = TestingSessionLocal()
    
    password = "TestPassword123!"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user = User(
        email="test@example.com",
        password_hash=password_hash,
        full_name="Test User",
        preferred_language="en"
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    db.close()
    return user


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers with JWT token"""
    token = create_access_token(test_user.id, test_user.email)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestListTemplates:
    """Test GET /api/documents/templates endpoint"""
    
    def test_list_templates_success(self, client, auth_headers):
        """Test successful template listing"""
        response = client.get("/api/documents/templates", headers=auth_headers)
        
        assert response.status_code == 200
        templates = response.json()
        
        # Should return list of templates
        assert isinstance(templates, list)
        assert len(templates) > 0
        
        # Check template structure
        for template in templates:
            assert "document_type" in template
            assert "name" in template
            assert "description" in template
            assert "category" in template
            assert "fields" in template
            assert isinstance(template["fields"], list)
            
            # Check field structure
            for field in template["fields"]:
                assert "name" in field
                assert "label" in field
                assert "field_type" in field
                assert "required" in field
                assert "description" in field
                assert "placeholder" in field
    
    def test_list_templates_requires_auth(self, client):
        """Test that listing templates requires authentication"""
        response = client.get("/api/documents/templates")
        assert response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing auth
    
    def test_list_templates_contains_expected_types(self, client, auth_headers):
        """Test that all expected document types are present"""
        response = client.get("/api/documents/templates", headers=auth_headers)
        
        assert response.status_code == 200
        templates = response.json()
        
        doc_types = [t["document_type"] for t in templates]
        
        # Should include the three main document types
        assert "legal_letter" in doc_types
        assert "rti_application" in doc_types
        assert "counter_petition" in doc_types


class TestGenerateDocument:
    """Test POST /api/documents/generate endpoint"""
    
    def test_generate_legal_letter_success(self, client, auth_headers, test_user):
        """Test successful legal letter generation"""
        request_data = {
            "document_type": "legal_letter",
            "inputs": {
                "sender_name": "John Doe",
                "sender_address": "123 Main St, Mumbai, Maharashtra - 400001",
                "sender_phone": "+91-9876543210",
                "sender_email": "john@example.com",
                "recipient_name": "Jane Smith",
                "recipient_designation": "Principal",
                "recipient_address": "ABC College, Mumbai, Maharashtra - 400002",
                "subject": "Complaint regarding false allegations",
                "incident_date": "15th January 2024",
                "incident_description": "I was falsely accused of misconduct on 15th January 2024.",
                "legal_grounds": "Section 499 IPC (Defamation)",
                "demands": "1. Immediate withdrawal of allegations\n2. Written apology"
            }
        }
        
        response = client.post("/api/documents/generate", headers=auth_headers, json=request_data)
        
        assert response.status_code == 201
        result = response.json()
        
        # Check response structure
        assert "id" in result
        assert "document_type" in result
        assert result["document_type"] == "legal_letter"
        assert "created_at" in result
        assert "file_path" in result
        assert "text_content" in result
        assert "pdf_available" in result
        assert result["pdf_available"] is True
        
        # Check that text content contains key information
        text = result["text_content"]
        assert "John Doe" in text
        assert "Jane Smith" in text
        assert "false allegations" in text
        
        # Verify document was saved to database
        db = TestingSessionLocal()
        doc = db.query(GeneratedDocument).filter(
            GeneratedDocument.user_id == test_user.id
        ).first()
        assert doc is not None
        assert doc.document_type == "legal_letter"
        db.close()
        
        # Verify files were created
        pdf_path = Path(result["file_path"])
        assert pdf_path.exists()
        
        text_path = pdf_path.with_suffix('.txt')
        assert text_path.exists()
    
    def test_generate_rti_application_success(self, client, auth_headers):
        """Test successful RTI application generation"""
        request_data = {
            "document_type": "rti_application",
            "inputs": {
                "applicant_name": "Priya Sharma",
                "applicant_address": "456 Park St, Kolkata, West Bengal - 700016",
                "applicant_phone": "+91-9876543210",
                "applicant_email": "priya@example.com",
                "department_name": "Delhi Police",
                "department_address": "Police HQ, ITO, New Delhi - 110002",
                "information_sought": "Copy of FIR No. 123/2024",
                "period_of_information": "January 2024"
            }
        }
        
        response = client.post("/api/documents/generate", headers=auth_headers, json=request_data)
        
        assert response.status_code == 201
        result = response.json()
        assert result["document_type"] == "rti_application"
        assert "Priya Sharma" in result["text_content"]
    
    def test_generate_counter_petition_success(self, client, auth_headers):
        """Test successful counter-petition generation"""
        request_data = {
            "document_type": "counter_petition",
            "inputs": {
                "respondent_name": "Amit Kumar Singh",
                "respondent_address": "789 Civil Lines, Lucknow, UP - 226001",
                "respondent_phone": "+91-9876543210",
                "respondent_email": "amit@example.com",
                "court_name": "District Court, Lucknow",
                "case_number": "123",
                "case_year": "2024",
                "petitioner_name": "Neha Verma",
                "case_type": "Civil Suit",
                "original_petition_date": "10th January 2024",
                "facts_of_case": "The petitioner alleged misconduct",
                "counter_facts": "The allegations are false",
                "legal_objections": "The petition is barred by limitation",
                "evidence_list": "Email correspondence",
                "prayer_relief": "Dismiss the petition"
            }
        }
        
        response = client.post("/api/documents/generate", headers=auth_headers, json=request_data)
        
        assert response.status_code == 201
        result = response.json()
        assert result["document_type"] == "counter_petition"
        assert "Amit Kumar Singh" in result["text_content"]
    
    def test_generate_document_missing_required_field(self, client, auth_headers):
        """Test document generation with missing required field"""
        request_data = {
            "document_type": "legal_letter",
            "inputs": {
                "sender_name": "John Doe",
                # Missing other required fields
            }
        }
        
        response = client.post("/api/documents/generate", headers=auth_headers, json=request_data)
        
        assert response.status_code == 400
        assert "Validation errors" in response.json()["detail"]
    
    def test_generate_document_invalid_type(self, client, auth_headers):
        """Test document generation with invalid document type"""
        request_data = {
            "document_type": "invalid_type",
            "inputs": {}
        }
        
        response = client.post("/api/documents/generate", headers=auth_headers, json=request_data)
        
        assert response.status_code == 400
        assert "Invalid document type" in response.json()["detail"]
    
    def test_generate_document_requires_auth(self, client):
        """Test that document generation requires authentication"""
        request_data = {
            "document_type": "legal_letter",
            "inputs": {}
        }
        
        response = client.post("/api/documents/generate", json=request_data)
        assert response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing auth
    
    def test_generate_document_with_optional_fields(self, client, auth_headers):
        """Test document generation with optional fields"""
        request_data = {
            "document_type": "legal_letter",
            "inputs": {
                "sender_name": "John Doe",
                "sender_address": "123 Main St, Mumbai, Maharashtra - 400001",
                "sender_phone": "+91-9876543210",
                "sender_email": "john@example.com",
                "recipient_name": "Jane Smith",
                "recipient_designation": "Principal",
                "recipient_address": "ABC College, Mumbai, Maharashtra - 400002",
                "subject": "Complaint",
                "incident_date": "15th January 2024",
                "incident_description": "Incident description",
                "legal_grounds": "Legal grounds",
                "demands": "Demands",
                # Optional fields
                "reference_number": "REF/2024/001",
                "timeline": "15 days",
                "consequences": "Legal action will be taken"
            }
        }
        
        response = client.post("/api/documents/generate", headers=auth_headers, json=request_data)
        
        assert response.status_code == 201
        result = response.json()
        
        # Check that optional fields are included
        text = result["text_content"]
        assert "REF/2024/001" in text
        assert "15 days" in text


class TestGetDocument:
    """Test GET /api/documents/{id} endpoint"""
    
    def test_get_document_success(self, client, auth_headers, test_user):
        """Test successful document retrieval"""
        # First generate a document
        request_data = {
            "document_type": "legal_letter",
            "inputs": {
                "sender_name": "John Doe",
                "sender_address": "123 Main St, Mumbai, Maharashtra - 400001",
                "sender_phone": "+91-9876543210",
                "sender_email": "john@example.com",
                "recipient_name": "Jane Smith",
                "recipient_designation": "Principal",
                "recipient_address": "ABC College, Mumbai, Maharashtra - 400002",
                "subject": "Complaint",
                "incident_date": "15th January 2024",
                "incident_description": "Incident description",
                "legal_grounds": "Legal grounds",
                "demands": "Demands"
            }
        }
        
        gen_response = client.post("/api/documents/generate", headers=auth_headers, json=request_data)
        assert gen_response.status_code == 201
        doc_id = gen_response.json()["id"]
        
        # Now retrieve the document
        response = client.get(f"/api/documents/{doc_id}", headers=auth_headers)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["id"] == doc_id
        assert result["document_type"] == "legal_letter"
        assert "text_content" in result
        assert "John Doe" in result["text_content"]
    
    def test_get_document_not_found(self, client, auth_headers):
        """Test retrieving non-existent document"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/documents/{fake_id}", headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_document_requires_auth(self, client):
        """Test that document retrieval requires authentication"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/documents/{fake_id}")
        
        assert response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing auth
    
    def test_get_document_different_user(self, client, test_user):
        """Test that users can only access their own documents"""
        # Create first user's document
        token1 = create_access_token(test_user.id, test_user.email)
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        request_data = {
            "document_type": "legal_letter",
            "inputs": {
                "sender_name": "John Doe",
                "sender_address": "123 Main St, Mumbai, Maharashtra - 400001",
                "sender_phone": "+91-9876543210",
                "sender_email": "john@example.com",
                "recipient_name": "Jane Smith",
                "recipient_designation": "Principal",
                "recipient_address": "ABC College, Mumbai, Maharashtra - 400002",
                "subject": "Complaint",
                "incident_date": "15th January 2024",
                "incident_description": "Incident description",
                "legal_grounds": "Legal grounds",
                "demands": "Demands"
            }
        }
        
        gen_response = client.post("/api/documents/generate", headers=headers1, json=request_data)
        doc_id = gen_response.json()["id"]
        
        # Create second user
        db = TestingSessionLocal()
        password_hash = bcrypt.hashpw("password".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user2 = User(
            email="user2@example.com",
            password_hash=password_hash,
            full_name="User Two",
            preferred_language="en"
        )
        db.add(user2)
        db.commit()
        db.close()
        
        # Try to access first user's document as second user
        token2 = create_access_token(user2.id, user2.email)
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        response = client.get(f"/api/documents/{doc_id}", headers=headers2)
        
        assert response.status_code == 404  # Should not find document


class TestListUserDocuments:
    """Test GET /api/documents/ endpoint"""
    
    def test_list_user_documents_empty(self, client, auth_headers):
        """Test listing documents when user has none"""
        response = client.get("/api/documents/", headers=auth_headers)
        
        assert response.status_code == 200
        documents = response.json()
        assert isinstance(documents, list)
        assert len(documents) == 0
    
    def test_list_user_documents_with_documents(self, client, auth_headers):
        """Test listing documents when user has generated some"""
        # Generate two documents
        request_data1 = {
            "document_type": "legal_letter",
            "inputs": {
                "sender_name": "John Doe",
                "sender_address": "123 Main St, Mumbai, Maharashtra - 400001",
                "sender_phone": "+91-9876543210",
                "sender_email": "john@example.com",
                "recipient_name": "Jane Smith",
                "recipient_designation": "Principal",
                "recipient_address": "ABC College, Mumbai, Maharashtra - 400002",
                "subject": "Complaint",
                "incident_date": "15th January 2024",
                "incident_description": "Incident description",
                "legal_grounds": "Legal grounds",
                "demands": "Demands"
            }
        }
        
        request_data2 = {
            "document_type": "rti_application",
            "inputs": {
                "applicant_name": "Priya Sharma",
                "applicant_address": "456 Park St, Kolkata, West Bengal - 700016",
                "applicant_phone": "+91-9876543210",
                "applicant_email": "priya@example.com",
                "department_name": "Delhi Police",
                "department_address": "Police HQ, ITO, New Delhi - 110002",
                "information_sought": "Copy of FIR",
                "period_of_information": "January 2024"
            }
        }
        
        client.post("/api/documents/generate", headers=auth_headers, json=request_data1)
        client.post("/api/documents/generate", headers=auth_headers, json=request_data2)
        
        # List documents
        response = client.get("/api/documents/", headers=auth_headers)
        
        assert response.status_code == 200
        documents = response.json()
        assert len(documents) == 2
        
        # Check document structure (should not include full content)
        for doc in documents:
            assert "id" in doc
            assert "document_type" in doc
            assert "created_at" in doc
            assert "file_path" in doc
            assert "text_content" not in doc  # Should not include full content in list
    
    def test_list_user_documents_requires_auth(self, client):
        """Test that listing documents requires authentication"""
        response = client.get("/api/documents/")
        assert response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing auth


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
