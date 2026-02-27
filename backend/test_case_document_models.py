"""
Test suite for CaseAnalysis and GeneratedDocument models.

This test file verifies that the CaseAnalysis and GeneratedDocument models
are correctly implemented with proper validation, relationships, and constraints.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from database import Base, engine, get_db
from models import CaseAnalysis, GeneratedDocument, User


# Setup and teardown
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """Create a test user for relationship testing."""
    with get_db() as db:
        user = User(
            email="test@example.com",
            full_name="Test User",
            preferred_language="en"
        )
        user.set_password("TestPass123!")
        db.add(user)
        db.commit()
        db.refresh(user)
        return user.id


# CaseAnalysis Model Tests
class TestCaseAnalysisModel:
    """Test cases for CaseAnalysis model."""
    
    def test_create_case_analysis_success(self, test_user):
        """Test creating a valid case analysis."""
        with get_db() as db:
            case_analysis = CaseAnalysis(
                user_id=test_user,
                complaint_details={
                    "evidence": ["Document 1", "Witness testimony"],
                    "allegations": "False accusation of theft",
                    "procedures": "Police complaint filed",
                    "timeline": "Incident on 2024-01-15"
                },
                validity_score=65,
                score_breakdown={
                    "evidence": 25,
                    "legal_basis": 20,
                    "procedural": 15,
                    "timeline": 5
                },
                weaknesses=["Lack of direct evidence", "No witness corroboration"],
                recommendations=["Gather more evidence", "Consult legal expert"]
            )
            db.add(case_analysis)
            db.commit()
            db.refresh(case_analysis)
            
            assert case_analysis.id is not None
            assert case_analysis.user_id == test_user
            assert case_analysis.validity_score == 65
            assert case_analysis.score_breakdown["evidence"] == 25
            assert len(case_analysis.weaknesses) == 2
            assert len(case_analysis.recommendations) == 2
    
    def test_validity_score_bounds(self, test_user):
        """Test that validity score must be between 0 and 100."""
        with get_db() as db:
            # Test score = 0 (valid)
            case_analysis = CaseAnalysis(
                user_id=test_user,
                complaint_details={"test": "data"},
                validity_score=0,
                score_breakdown={
                    "evidence": 0,
                    "legal_basis": 0,
                    "procedural": 0,
                    "timeline": 0
                }
            )
            db.add(case_analysis)
            db.commit()
            assert case_analysis.validity_score == 0
            
            # Test score = 100 (valid)
            case_analysis2 = CaseAnalysis(
                user_id=test_user,
                complaint_details={"test": "data"},
                validity_score=100,
                score_breakdown={
                    "evidence": 40,
                    "legal_basis": 30,
                    "procedural": 20,
                    "timeline": 10
                }
            )
            db.add(case_analysis2)
            db.commit()
            assert case_analysis2.validity_score == 100
    
    def test_validity_score_out_of_range(self, test_user):
        """Test that validity score outside 0-100 raises error."""
        with get_db() as db:
            # Test score < 0
            with pytest.raises(ValueError, match="must be between 0 and 100"):
                case_analysis = CaseAnalysis(
                    user_id=test_user,
                    complaint_details={"test": "data"},
                    validity_score=-1,
                    score_breakdown={
                        "evidence": 0,
                        "legal_basis": 0,
                        "procedural": 0,
                        "timeline": 0
                    }
                )
                db.add(case_analysis)
                db.flush()
            
            # Test score > 100
            with pytest.raises(ValueError, match="must be between 0 and 100"):
                case_analysis = CaseAnalysis(
                    user_id=test_user,
                    complaint_details={"test": "data"},
                    validity_score=101,
                    score_breakdown={
                        "evidence": 40,
                        "legal_basis": 30,
                        "procedural": 20,
                        "timeline": 11
                    }
                )
                db.add(case_analysis)
                db.flush()
    
    def test_score_breakdown_validation(self, test_user):
        """Test that score breakdown must have all required components."""
        with get_db() as db:
            # Missing component
            with pytest.raises(ValueError, match="missing required components"):
                case_analysis = CaseAnalysis(
                    user_id=test_user,
                    complaint_details={"test": "data"},
                    validity_score=50,
                    score_breakdown={
                        "evidence": 20,
                        "legal_basis": 15
                        # Missing procedural and timeline
                    }
                )
                db.add(case_analysis)
                db.flush()
    
    def test_score_breakdown_component_ranges(self, test_user):
        """Test that score breakdown components have correct ranges."""
        with get_db() as db:
            # Evidence score out of range (max 40)
            with pytest.raises(ValueError, match="evidence score must be between"):
                case_analysis = CaseAnalysis(
                    user_id=test_user,
                    complaint_details={"test": "data"},
                    validity_score=50,
                    score_breakdown={
                        "evidence": 45,  # Max is 40
                        "legal_basis": 20,
                        "procedural": 15,
                        "timeline": 5
                    }
                )
                db.add(case_analysis)
                db.flush()
    
    def test_empty_complaint_details(self, test_user):
        """Test that complaint details cannot be empty."""
        with get_db() as db:
            with pytest.raises(ValueError, match="Complaint details cannot be empty"):
                case_analysis = CaseAnalysis(
                    user_id=test_user,
                    complaint_details={},
                    validity_score=50,
                    score_breakdown={
                        "evidence": 20,
                        "legal_basis": 15,
                        "procedural": 10,
                        "timeline": 5
                    }
                )
                db.add(case_analysis)
                db.flush()
    
    def test_user_relationship(self, test_user):
        """Test that case analysis is linked to user correctly."""
        with get_db() as db:
            case_analysis = CaseAnalysis(
                user_id=test_user,
                complaint_details={"test": "data"},
                validity_score=50,
                score_breakdown={
                    "evidence": 20,
                    "legal_basis": 15,
                    "procedural": 10,
                    "timeline": 5
                }
            )
            db.add(case_analysis)
            db.commit()
            
            # Fetch user and check relationship
            user = db.query(User).filter(User.id == test_user).first()
            assert len(user.case_analyses) == 1
            assert user.case_analyses[0].validity_score == 50
    
    def test_cascade_delete(self, test_user):
        """Test that deleting user cascades to case analyses."""
        with get_db() as db:
            # Create case analysis
            case_analysis = CaseAnalysis(
                user_id=test_user,
                complaint_details={"test": "data"},
                validity_score=50,
                score_breakdown={
                    "evidence": 20,
                    "legal_basis": 15,
                    "procedural": 10,
                    "timeline": 5
                }
            )
            db.add(case_analysis)
            db.commit()
            case_id = case_analysis.id
            
            # Delete user
            user = db.query(User).filter(User.id == test_user).first()
            db.delete(user)
            db.commit()
            
            # Verify case analysis is also deleted
            deleted_case = db.query(CaseAnalysis).filter(CaseAnalysis.id == case_id).first()
            assert deleted_case is None


# GeneratedDocument Model Tests
class TestGeneratedDocumentModel:
    """Test cases for GeneratedDocument model."""
    
    def test_create_generated_document_success(self, test_user):
        """Test creating a valid generated document."""
        with get_db() as db:
            document = GeneratedDocument(
                user_id=test_user,
                document_type="legal_letter",
                template_inputs={
                    "recipient_name": "John Doe",
                    "recipient_address": "123 Main St",
                    "subject": "Legal Notice",
                    "body": "This is a legal notice..."
                },
                file_path="/documents/legal_letter_123.pdf"
            )
            db.add(document)
            db.commit()
            db.refresh(document)
            
            assert document.id is not None
            assert document.user_id == test_user
            assert document.document_type == "legal_letter"
            assert document.template_inputs["recipient_name"] == "John Doe"
            assert document.file_path == "/documents/legal_letter_123.pdf"
    
    def test_valid_document_types(self, test_user):
        """Test all valid document types."""
        valid_types = [
            "legal_letter",
            "rti_application",
            "counter_petition",
            "complaint_letter",
            "notice_reply",
            "affidavit",
            "application"
        ]
        
        with get_db() as db:
            for doc_type in valid_types:
                document = GeneratedDocument(
                    user_id=test_user,
                    document_type=doc_type,
                    template_inputs={"test": "data"},
                    file_path=f"/documents/{doc_type}.pdf"
                )
                db.add(document)
                db.commit()
                assert document.document_type == doc_type
    
    def test_invalid_document_type(self, test_user):
        """Test that invalid document type raises error."""
        with get_db() as db:
            with pytest.raises(ValueError, match="Invalid document type"):
                document = GeneratedDocument(
                    user_id=test_user,
                    document_type="invalid_type",
                    template_inputs={"test": "data"},
                    file_path="/documents/test.pdf"
                )
                db.add(document)
                db.flush()
    
    def test_empty_template_inputs(self, test_user):
        """Test that template inputs cannot be empty."""
        with get_db() as db:
            with pytest.raises(ValueError, match="Template inputs cannot be empty"):
                document = GeneratedDocument(
                    user_id=test_user,
                    document_type="legal_letter",
                    template_inputs={},
                    file_path="/documents/test.pdf"
                )
                db.add(document)
                db.flush()
    
    def test_empty_file_path(self, test_user):
        """Test that file path cannot be empty."""
        with get_db() as db:
            with pytest.raises(ValueError, match="File path is required"):
                document = GeneratedDocument(
                    user_id=test_user,
                    document_type="legal_letter",
                    template_inputs={"test": "data"},
                    file_path=""
                )
                db.add(document)
                db.flush()
    
    def test_file_path_max_length(self, test_user):
        """Test that file path has maximum length constraint."""
        with get_db() as db:
            # Valid path (500 characters)
            valid_path = "/documents/" + "a" * 489 + ".pdf"
            document = GeneratedDocument(
                user_id=test_user,
                document_type="legal_letter",
                template_inputs={"test": "data"},
                file_path=valid_path
            )
            db.add(document)
            db.commit()
            assert len(document.file_path) == 500
            
            # Invalid path (>500 characters)
            with pytest.raises(ValueError, match="exceeds maximum length"):
                invalid_path = "/documents/" + "a" * 490 + ".pdf"
                document2 = GeneratedDocument(
                    user_id=test_user,
                    document_type="legal_letter",
                    template_inputs={"test": "data"},
                    file_path=invalid_path
                )
                db.add(document2)
                db.flush()
    
    def test_user_relationship(self, test_user):
        """Test that generated document is linked to user correctly."""
        with get_db() as db:
            document = GeneratedDocument(
                user_id=test_user,
                document_type="rti_application",
                template_inputs={"test": "data"},
                file_path="/documents/rti.pdf"
            )
            db.add(document)
            db.commit()
            
            # Fetch user and check relationship
            user = db.query(User).filter(User.id == test_user).first()
            assert len(user.generated_documents) == 1
            assert user.generated_documents[0].document_type == "rti_application"
    
    def test_cascade_delete(self, test_user):
        """Test that deleting user cascades to generated documents."""
        with get_db() as db:
            # Create document
            document = GeneratedDocument(
                user_id=test_user,
                document_type="legal_letter",
                template_inputs={"test": "data"},
                file_path="/documents/test.pdf"
            )
            db.add(document)
            db.commit()
            doc_id = document.id
            
            # Delete user
            user = db.query(User).filter(User.id == test_user).first()
            db.delete(user)
            db.commit()
            
            # Verify document is also deleted
            deleted_doc = db.query(GeneratedDocument).filter(GeneratedDocument.id == doc_id).first()
            assert deleted_doc is None
    
    def test_multiple_documents_per_user(self, test_user):
        """Test that a user can have multiple generated documents."""
        with get_db() as db:
            # Create multiple documents
            doc1 = GeneratedDocument(
                user_id=test_user,
                document_type="legal_letter",
                template_inputs={"test": "data1"},
                file_path="/documents/letter.pdf"
            )
            doc2 = GeneratedDocument(
                user_id=test_user,
                document_type="rti_application",
                template_inputs={"test": "data2"},
                file_path="/documents/rti.pdf"
            )
            doc3 = GeneratedDocument(
                user_id=test_user,
                document_type="counter_petition",
                template_inputs={"test": "data3"},
                file_path="/documents/petition.pdf"
            )
            db.add_all([doc1, doc2, doc3])
            db.commit()
            
            # Verify user has all documents
            user = db.query(User).filter(User.id == test_user).first()
            assert len(user.generated_documents) == 3
            doc_types = {doc.document_type for doc in user.generated_documents}
            assert doc_types == {"legal_letter", "rti_application", "counter_petition"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
