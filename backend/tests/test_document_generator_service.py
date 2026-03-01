"""
Test document generator service
"""

import pytest
from pathlib import Path
from document_generator_service import DocumentGeneratorService, get_document_generator_service
from templates.template_config import DocumentType
from io import BytesIO
from reportlab.pdfgen import canvas
import re


class TestDocumentGeneratorService:
    """Test document generator service functionality"""
    
    @pytest.fixture
    def service(self):
        """Create document generator service instance"""
        return DocumentGeneratorService()
    
    def test_singleton_instance(self):
        """Test that get_document_generator_service returns singleton"""
        service1 = get_document_generator_service()
        service2 = get_document_generator_service()
        assert service1 is service2
    
    def test_load_template_legal_letter(self, service):
        """Test loading legal letter template"""
        template = service.load_template(DocumentType.LEGAL_LETTER)
        assert template is not None
        assert template.name == "legal_letter.j2"
    
    def test_load_template_rti_application(self, service):
        """Test loading RTI application template"""
        template = service.load_template(DocumentType.RTI_APPLICATION)
        assert template is not None
        assert template.name == "rti_application.j2"
    
    def test_load_template_counter_petition(self, service):
        """Test loading counter-petition template"""
        template = service.load_template(DocumentType.COUNTER_PETITION)
        assert template is not None
        assert template.name == "counter_petition.j2"
    
    def test_load_template_invalid_type(self, service):
        """Test loading template with invalid type raises error"""
        with pytest.raises(ValueError, match="Invalid document type"):
            service.load_template("invalid_type")
    
    def test_validate_inputs_missing_required_fields(self, service):
        """Test validation fails when required fields are missing"""
        inputs = {
            "sender_name": "John Doe"
            # Missing other required fields
        }
        is_valid, errors = service.validate_inputs(DocumentType.LEGAL_LETTER, inputs)
        assert not is_valid
        assert len(errors) > 0
        assert any("Required field" in error for error in errors)
    
    def test_validate_inputs_invalid_email(self, service):
        """Test validation fails for invalid email"""
        inputs = {
            "sender_name": "John Doe",
            "sender_address": "123 Street",
            "sender_phone": "+91-9876543210",
            "sender_email": "invalid-email",  # Invalid
            "recipient_name": "Jane Doe",
            "recipient_designation": "Principal",
            "recipient_address": "456 Avenue",
            "subject": "Test",
            "incident_date": "2024-01-15",
            "incident_description": "Test",
            "legal_grounds": "Test",
            "demands": "Test"
        }
        is_valid, errors = service.validate_inputs(DocumentType.LEGAL_LETTER, inputs)
        assert not is_valid
        assert any("email" in error.lower() for error in errors)
    
    def test_validate_inputs_valid(self, service):
        """Test validation passes with valid inputs"""
        inputs = {
            "sender_name": "John Doe",
            "sender_address": "123 Street, City",
            "sender_phone": "+91-9876543210",
            "sender_email": "john@email.com",
            "recipient_name": "Jane Doe",
            "recipient_designation": "Principal",
            "recipient_address": "456 Avenue",
            "subject": "Test Subject",
            "incident_date": "15th January 2024",
            "incident_description": "Test description",
            "legal_grounds": "Test grounds",
            "demands": "Test demands"
        }
        is_valid, errors = service.validate_inputs(DocumentType.LEGAL_LETTER, inputs)
        assert is_valid
        assert len(errors) == 0
    
    def test_add_placeholders_for_optional_fields(self, service):
        """Test that placeholders are added for missing optional fields"""
        inputs = {
            "sender_name": "John Doe",
            "sender_address": "123 Street",
            "sender_phone": "+91-9876543210",
            "sender_email": "john@email.com",
            "recipient_name": "Jane Doe",
            "recipient_designation": "Principal",
            "recipient_address": "456 Avenue",
            "subject": "Test",
            "incident_date": "15th January 2024",
            "incident_description": "Test",
            "legal_grounds": "Test",
            "demands": "Test"
            # Missing optional fields: date, reference_number, timeline, consequences, attachments
        }
        
        result = service.add_placeholders(inputs, DocumentType.LEGAL_LETTER)
        
        # Check that optional fields have placeholders
        assert "reference_number" in result
        assert "timeline" in result
        assert "consequences" in result
        assert "attachments" in result
        
        # Check that date is added if missing
        assert "date" in result
        assert result["date"] != ""
    
    def test_add_placeholders_preserves_provided_values(self, service):
        """Test that provided values are not overwritten by placeholders"""
        inputs = {
            "sender_name": "John Doe",
            "sender_address": "123 Street",
            "sender_phone": "+91-9876543210",
            "sender_email": "john@email.com",
            "recipient_name": "Jane Doe",
            "recipient_designation": "Principal",
            "recipient_address": "456 Avenue",
            "subject": "Test",
            "incident_date": "15th January 2024",
            "incident_description": "Test",
            "legal_grounds": "Test",
            "demands": "Test",
            "date": "20th January 2024",  # Provided
            "timeline": "7 days"  # Provided
        }
        
        result = service.add_placeholders(inputs, DocumentType.LEGAL_LETTER)
        
        # Check that provided values are preserved
        assert result["date"] == "20th January 2024"
        assert result["timeline"] == "7 days"
    
    def test_render_template_legal_letter(self, service):
        """Test rendering legal letter template"""
        inputs = {
            "sender_name": "Rajesh Kumar",
            "sender_address": "123, MG Road, Bangalore, Karnataka - 560001",
            "sender_phone": "+91-9876543210",
            "sender_email": "rajesh@email.com",
            "recipient_name": "Dr. Priya Mehta",
            "recipient_designation": "Principal",
            "recipient_address": "ABC College, Mumbai",
            "subject": "Complaint regarding false allegations",
            "incident_date": "15th January 2024",
            "incident_description": "I was falsely accused of misconduct.",
            "legal_grounds": "Section 499 IPC (Defamation)",
            "demands": "1. Withdrawal of allegations\n2. Written apology"
        }
        
        rendered = service.render_template(DocumentType.LEGAL_LETTER, inputs)
        
        # Verify key content is present
        assert "Rajesh Kumar" in rendered
        assert "Dr. Priya Mehta" in rendered
        assert "false allegations" in rendered
        assert "Section 499 IPC" in rendered
        assert "Withdrawal of allegations" in rendered
        assert "From:" in rendered
        assert "To:" in rendered
        assert "Subject:" in rendered
    
    def test_render_template_with_placeholders(self, service):
        """Test that missing optional fields show placeholders in rendered output"""
        inputs = {
            "sender_name": "John Doe",
            "sender_address": "123 Street",
            "sender_phone": "+91-9876543210",
            "sender_email": "john@email.com",
            "recipient_name": "Jane Doe",
            "recipient_designation": "Principal",
            "recipient_address": "456 Avenue",
            "subject": "Test",
            "incident_date": "15th January 2024",
            "incident_description": "Test",
            "legal_grounds": "Test",
            "demands": "Test"
            # No optional fields provided
        }
        
        rendered = service.render_template(DocumentType.LEGAL_LETTER, inputs)
        
        # Check that placeholders or defaults are present
        assert "15 days" in rendered or "[TIMELINE" in rendered  # Default timeline
        assert "appropriate legal action" in rendered or "[CONSEQUENCES" in rendered
    
    def test_render_template_validation_error(self, service):
        """Test that render_template raises error for invalid inputs"""
        inputs = {
            "sender_name": "John Doe"
            # Missing required fields
        }
        
        with pytest.raises(ValueError, match="Validation errors"):
            service.render_template(DocumentType.LEGAL_LETTER, inputs)
    
    def test_generate_pdf_creates_valid_pdf(self, service):
        """Test that generate_pdf creates valid PDF bytes"""
        text_content = """
        Test Document
        
        This is a test document with multiple lines.
        It should be converted to PDF format.
        
        HEADING IN CAPS
        
        More content here.
        """
        
        pdf_bytes = service.generate_pdf(text_content)
        
        # Check that PDF bytes are generated
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        
        # Check PDF header (PDF files start with %PDF)
        assert pdf_bytes[:4] == b'%PDF'
    
    def test_generate_pdf_handles_special_characters(self, service):
        """Test that generate_pdf handles special characters correctly"""
        text_content = """
        Test with special characters: & < >
        Email: test@email.com
        Phone: +91-9876543210
        """
        
        pdf_bytes = service.generate_pdf(text_content)
        
        # Should not raise error and should generate valid PDF
        assert pdf_bytes is not None
        assert pdf_bytes[:4] == b'%PDF'
    
    def test_generate_pdf_handles_long_content(self, service):
        """Test that generate_pdf handles long content with multiple pages"""
        # Create long content
        text_content = "\n".join([f"Line {i}: This is a test line with some content." for i in range(100)])
        
        pdf_bytes = service.generate_pdf(text_content)
        
        # Should generate valid PDF
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b'%PDF'
    
    def test_generate_document_returns_both_formats(self, service):
        """Test that generate_document returns both text and PDF"""
        inputs = {
            "sender_name": "Test User",
            "sender_address": "123 Street",
            "sender_phone": "+91-9876543210",
            "sender_email": "test@email.com",
            "recipient_name": "Recipient",
            "recipient_designation": "Principal",
            "recipient_address": "456 Avenue",
            "subject": "Test Subject",
            "incident_date": "15th January 2024",
            "incident_description": "Test description",
            "legal_grounds": "Test grounds",
            "demands": "Test demands"
        }
        
        text_content, pdf_bytes = service.generate_document(DocumentType.LEGAL_LETTER, inputs)
        
        # Check text content
        assert text_content is not None
        assert len(text_content) > 0
        assert "Test User" in text_content
        
        # Check PDF bytes
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b'%PDF'
    
    def test_generate_document_rti_application(self, service):
        """Test generating RTI application document"""
        inputs = {
            "applicant_name": "Priya Sharma",
            "applicant_address": "456, Park Street, Kolkata",
            "applicant_phone": "+91-9876543210",
            "applicant_email": "priya@email.com",
            "department_name": "Delhi Police",
            "department_address": "Police HQ, New Delhi",
            "information_sought": "Copy of FIR No. 123/2024",
            "period_of_information": "January 2024"
        }
        
        text_content, pdf_bytes = service.generate_document(DocumentType.RTI_APPLICATION, inputs)
        
        # Check text content
        assert "Priya Sharma" in text_content
        assert "Delhi Police" in text_content
        assert "Right to Information" in text_content
        assert "FIR No. 123/2024" in text_content
        
        # Check PDF
        assert pdf_bytes[:4] == b'%PDF'
    
    def test_generate_document_counter_petition(self, service):
        """Test generating counter-petition document"""
        inputs = {
            "respondent_name": "Amit Singh",
            "respondent_address": "789, Civil Lines, Lucknow",
            "respondent_phone": "+91-9876543210",
            "respondent_email": "amit@email.com",
            "court_name": "District Court, Lucknow",
            "case_number": "123",
            "case_year": "2024",
            "petitioner_name": "Neha Verma",
            "case_type": "Civil Suit",
            "original_petition_date": "10th January 2024",
            "facts_of_case": "Petitioner alleged...",
            "counter_facts": "Allegations are false...",
            "legal_objections": "Petition is barred by limitation",
            "evidence_list": "Email correspondence",
            "prayer_relief": "Dismiss the petition"
        }
        
        text_content, pdf_bytes = service.generate_document(DocumentType.COUNTER_PETITION, inputs)
        
        # Check text content
        assert "Amit Singh" in text_content
        assert "District Court, Lucknow" in text_content
        assert "Neha Verma" in text_content
        assert "COUNTER-PETITION" in text_content
        
        # Check PDF
        assert pdf_bytes[:4] == b'%PDF'
    
    def test_generate_document_with_all_optional_fields(self, service):
        """Test generating document with all optional fields provided"""
        inputs = {
            "sender_name": "Complete User",
            "sender_address": "123 Street",
            "sender_phone": "+91-9876543210",
            "sender_email": "complete@email.com",
            "recipient_name": "Recipient",
            "recipient_designation": "Principal",
            "recipient_address": "456 Avenue",
            "subject": "Complete Test",
            "incident_date": "15th January 2024",
            "incident_description": "Test",
            "legal_grounds": "Test",
            "demands": "Test",
            "date": "20th January 2024",
            "reference_number": "REF/2024/001",
            "timeline": "7 days",
            "consequences": "file a police complaint",
            "attachments": ["Document 1", "Document 2"]
        }
        
        text_content, pdf_bytes = service.generate_document(DocumentType.LEGAL_LETTER, inputs)
        
        # Check that all provided fields are in output
        assert "20th January 2024" in text_content
        assert "REF/2024/001" in text_content
        assert "7 days" in text_content
        assert "file a police complaint" in text_content
        assert "Document 1" in text_content
        assert "Document 2" in text_content


class TestDocumentGeneratorEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def service(self):
        """Create document generator service instance"""
        return DocumentGeneratorService()
    
    def test_empty_string_in_required_field(self, service):
        """Test that empty strings in required fields are caught"""
        inputs = {
            "sender_name": "",  # Empty string
            "sender_address": "123 Street",
            "sender_phone": "+91-9876543210",
            "sender_email": "test@email.com",
            "recipient_name": "Jane Doe",
            "recipient_designation": "Principal",
            "recipient_address": "456 Avenue",
            "subject": "Test",
            "incident_date": "15th January 2024",
            "incident_description": "Test",
            "legal_grounds": "Test",
            "demands": "Test"
        }
        
        is_valid, errors = service.validate_inputs(DocumentType.LEGAL_LETTER, inputs)
        assert not is_valid
    
    def test_very_long_text_content(self, service):
        """Test handling of very long text content"""
        long_text = "A" * 10000  # 10,000 characters
        
        inputs = {
            "sender_name": "Test User",
            "sender_address": "123 Street",
            "sender_phone": "+91-9876543210",
            "sender_email": "test@email.com",
            "recipient_name": "Recipient",
            "recipient_designation": "Principal",
            "recipient_address": "456 Avenue",
            "subject": "Test",
            "incident_date": "15th January 2024",
            "incident_description": long_text,  # Very long
            "legal_grounds": "Test",
            "demands": "Test"
        }
        
        # Should not raise error
        text_content, pdf_bytes = service.generate_document(DocumentType.LEGAL_LETTER, inputs)
        assert long_text in text_content
        assert pdf_bytes[:4] == b'%PDF'
    
    def test_unicode_characters_in_content(self, service):
        """Test handling of Unicode characters"""
        inputs = {
            "sender_name": "राजेश कुमार",  # Hindi name
            "sender_address": "123 Street",
            "sender_phone": "+91-9876543210",
            "sender_email": "test@email.com",
            "recipient_name": "Recipient",
            "recipient_designation": "Principal",
            "recipient_address": "456 Avenue",
            "subject": "Test",
            "incident_date": "15th January 2024",
            "incident_description": "Test with émojis 😀",
            "legal_grounds": "Test",
            "demands": "Test"
        }
        
        # Should handle Unicode without error
        text_content, pdf_bytes = service.generate_document(DocumentType.LEGAL_LETTER, inputs)
        assert "राजेश कुमार" in text_content
        assert pdf_bytes[:4] == b'%PDF'
    
    def test_list_field_with_empty_list(self, service):
        """Test handling of list fields with empty lists"""
        inputs = {
            "sender_name": "Test User",
            "sender_address": "123 Street",
            "sender_phone": "+91-9876543210",
            "sender_email": "test@email.com",
            "recipient_name": "Recipient",
            "recipient_designation": "Principal",
            "recipient_address": "456 Avenue",
            "subject": "Test",
            "incident_date": "15th January 2024",
            "incident_description": "Test",
            "legal_grounds": "Test",
            "demands": "Test",
            "attachments": []  # Empty list
        }
        
        # Should handle empty list without error
        text_content, pdf_bytes = service.generate_document(DocumentType.LEGAL_LETTER, inputs)
        assert text_content is not None
        assert pdf_bytes[:4] == b'%PDF'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
