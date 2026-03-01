"""
Test document templates and template configuration
"""

import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from templates.template_config import (
    DocumentType,
    FieldType,
    get_template_config,
    get_required_fields,
    get_optional_fields,
    get_all_fields,
    validate_template_inputs,
    TEMPLATE_REGISTRY
)


# Set up Jinja2 environment
TEMPLATE_DIR = Path(__file__).parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True
)


class TestTemplateConfiguration:
    """Test template configuration and field definitions"""
    
    def test_all_document_types_registered(self):
        """Verify all document types are registered in template registry"""
        assert DocumentType.LEGAL_LETTER in TEMPLATE_REGISTRY
        assert DocumentType.RTI_APPLICATION in TEMPLATE_REGISTRY
        assert DocumentType.COUNTER_PETITION in TEMPLATE_REGISTRY
    
    def test_template_config_structure(self):
        """Verify template config has required structure"""
        for doc_type in DocumentType:
            config = get_template_config(doc_type)
            assert config is not None
            assert "name" in config
            assert "description" in config
            assert "template_file" in config
            assert "fields" in config
            assert "category" in config
    
    def test_template_files_exist(self):
        """Verify all template files exist"""
        for doc_type in DocumentType:
            config = get_template_config(doc_type)
            template_file = TEMPLATE_DIR / config["template_file"]
            assert template_file.exists(), f"Template file {config['template_file']} not found"
    
    def test_legal_letter_has_required_fields(self):
        """Verify legal letter template has all required fields"""
        required_fields = get_required_fields(DocumentType.LEGAL_LETTER)
        required_field_names = [f.name for f in required_fields]
        
        # Check essential required fields
        assert "sender_name" in required_field_names
        assert "sender_address" in required_field_names
        assert "sender_phone" in required_field_names
        assert "sender_email" in required_field_names
        assert "recipient_name" in required_field_names
        assert "subject" in required_field_names
        assert "incident_description" in required_field_names
        assert "legal_grounds" in required_field_names
        assert "demands" in required_field_names
    
    def test_legal_letter_has_optional_fields(self):
        """Verify legal letter template has optional fields"""
        optional_fields = get_optional_fields(DocumentType.LEGAL_LETTER)
        optional_field_names = [f.name for f in optional_fields]
        
        # Check optional fields
        assert "date" in optional_field_names
        assert "reference_number" in optional_field_names
        assert "timeline" in optional_field_names
        assert "consequences" in optional_field_names
        assert "attachments" in optional_field_names
    
    def test_rti_application_has_required_fields(self):
        """Verify RTI application template has all required fields"""
        required_fields = get_required_fields(DocumentType.RTI_APPLICATION)
        required_field_names = [f.name for f in required_fields]
        
        # Check essential required fields
        assert "applicant_name" in required_field_names
        assert "applicant_address" in required_field_names
        assert "applicant_phone" in required_field_names
        assert "applicant_email" in required_field_names
        assert "department_name" in required_field_names
        assert "department_address" in required_field_names
        assert "information_sought" in required_field_names
        assert "period_of_information" in required_field_names
    
    def test_rti_application_has_optional_fields(self):
        """Verify RTI application template has optional fields"""
        optional_fields = get_optional_fields(DocumentType.RTI_APPLICATION)
        optional_field_names = [f.name for f in optional_fields]
        
        # Check optional fields
        assert "date" in optional_field_names
        assert "pio_name" in optional_field_names
        assert "purpose" in optional_field_names
        assert "preferred_format" in optional_field_names
        assert "bpl_status" in optional_field_names
        assert "application_fee" in optional_field_names
    
    def test_counter_petition_has_required_fields(self):
        """Verify counter-petition template has all required fields"""
        required_fields = get_required_fields(DocumentType.COUNTER_PETITION)
        required_field_names = [f.name for f in required_fields]
        
        # Check essential required fields
        assert "respondent_name" in required_field_names
        assert "respondent_address" in required_field_names
        assert "court_name" in required_field_names
        assert "case_number" in required_field_names
        assert "petitioner_name" in required_field_names
        assert "case_type" in required_field_names
        assert "facts_of_case" in required_field_names
        assert "counter_facts" in required_field_names
        assert "legal_objections" in required_field_names
        assert "evidence_list" in required_field_names
        assert "prayer_relief" in required_field_names
    
    def test_counter_petition_has_optional_fields(self):
        """Verify counter-petition template has optional fields"""
        optional_fields = get_optional_fields(DocumentType.COUNTER_PETITION)
        optional_field_names = [f.name for f in optional_fields]
        
        # Check optional fields
        assert "date" in optional_field_names
        assert "advocate_name" in optional_field_names
        assert "advocate_enrollment" in optional_field_names
        assert "attachments" in optional_field_names


class TestTemplateValidation:
    """Test template input validation"""
    
    def test_validate_missing_required_fields(self):
        """Test validation fails when required fields are missing"""
        inputs = {
            "sender_name": "John Doe"
            # Missing other required fields
        }
        is_valid, errors = validate_template_inputs(DocumentType.LEGAL_LETTER, inputs)
        assert not is_valid
        assert len(errors) > 0
    
    def test_validate_invalid_email(self):
        """Test validation fails for invalid email"""
        inputs = {
            "sender_name": "John Doe",
            "sender_address": "123 Street",
            "sender_phone": "+91-9876543210",
            "sender_email": "invalid-email",  # Invalid email
            "recipient_name": "Jane Doe",
            "recipient_designation": "Principal",
            "recipient_address": "456 Avenue",
            "subject": "Test Subject",
            "incident_date": "2024-01-15",
            "incident_description": "Test incident",
            "legal_grounds": "Test grounds",
            "demands": "Test demands"
        }
        is_valid, errors = validate_template_inputs(DocumentType.LEGAL_LETTER, inputs)
        assert not is_valid
        assert any("email" in error.lower() for error in errors)
    
    def test_validate_valid_inputs(self):
        """Test validation passes with all required fields"""
        inputs = {
            "sender_name": "John Doe",
            "sender_address": "123 Street, City, State - 123456",
            "sender_phone": "+91-9876543210",
            "sender_email": "john.doe@email.com",
            "recipient_name": "Jane Doe",
            "recipient_designation": "Principal",
            "recipient_address": "456 Avenue, City, State - 654321",
            "subject": "Complaint regarding false allegations",
            "incident_date": "15th January 2024",
            "incident_description": "On 15th January 2024, I was falsely accused...",
            "legal_grounds": "Section 499 IPC (Defamation)",
            "demands": "1. Immediate withdrawal of allegations\n2. Written apology"
        }
        is_valid, errors = validate_template_inputs(DocumentType.LEGAL_LETTER, inputs)
        assert is_valid
        assert len(errors) == 0


class TestTemplateRendering:
    """Test template rendering with Jinja2"""
    
    def test_render_legal_letter_with_required_fields(self):
        """Test rendering legal letter with only required fields"""
        template = jinja_env.get_template("legal_letter.j2")
        
        inputs = {
            "sender_name": "Rajesh Kumar",
            "sender_address": "123, MG Road, Bangalore, Karnataka - 560001",
            "sender_phone": "+91-9876543210",
            "sender_email": "rajesh.kumar@email.com",
            "recipient_name": "Dr. Priya Mehta",
            "recipient_designation": "Principal",
            "recipient_address": "ABC College, College Road, Mumbai, Maharashtra - 400001",
            "subject": "Complaint regarding false allegations",
            "incident_date": "15th January 2024",
            "incident_description": "On 15th January 2024, I was falsely accused of misconduct by a fellow student.",
            "legal_grounds": "Section 499 IPC (Defamation), Article 21 of Constitution (Right to Life and Personal Liberty)",
            "demands": "1. Immediate withdrawal of false allegations\n2. Written apology\n3. Compensation for mental harassment"
        }
        
        rendered = template.render(**inputs)
        
        # Verify key content is present
        assert "Rajesh Kumar" in rendered
        assert "Dr. Priya Mehta" in rendered
        assert "false allegations" in rendered
        assert "Section 499 IPC" in rendered
        assert "Immediate withdrawal" in rendered
    
    def test_render_legal_letter_with_placeholders(self):
        """Test rendering legal letter with missing optional fields shows placeholders"""
        template = jinja_env.get_template("legal_letter.j2")
        
        inputs = {
            "sender_name": "Rajesh Kumar",
            "sender_address": "123, MG Road, Bangalore",
            "sender_phone": "+91-9876543210",
            "sender_email": "rajesh.kumar@email.com",
            "recipient_name": "Dr. Priya Mehta",
            "recipient_designation": "Principal",
            "recipient_address": "ABC College, Mumbai",
            "subject": "Test Subject",
            "incident_date": "15th January 2024",
            "incident_description": "Test description",
            "legal_grounds": "Test grounds",
            "demands": "Test demands"
            # date not provided - should use placeholder
        }
        
        rendered = template.render(**inputs)
        
        # Verify placeholder is present for missing date
        assert "[DATE]" in rendered or "15 days" in rendered  # Default timeline
    
    def test_render_rti_application(self):
        """Test rendering RTI application"""
        template = jinja_env.get_template("rti_application.j2")
        
        inputs = {
            "applicant_name": "Priya Sharma",
            "applicant_address": "456, Park Street, Kolkata, West Bengal - 700016",
            "applicant_phone": "+91-9876543210",
            "applicant_email": "priya.sharma@email.com",
            "department_name": "Delhi Police",
            "department_address": "Police Headquarters, ITO, New Delhi - 110002",
            "information_sought": "1. Copy of FIR No. 123/2024\n2. Status of investigation",
            "period_of_information": "January 2024 to March 2024"
        }
        
        rendered = template.render(**inputs)
        
        # Verify key content is present
        assert "Priya Sharma" in rendered
        assert "Delhi Police" in rendered
        assert "Right to Information Act, 2005" in rendered
        assert "FIR No. 123/2024" in rendered
    
    def test_render_counter_petition(self):
        """Test rendering counter-petition"""
        template = jinja_env.get_template("counter_petition.j2")
        
        inputs = {
            "respondent_name": "Amit Kumar Singh",
            "respondent_address": "789, Civil Lines, Lucknow, UP - 226001",
            "respondent_phone": "+91-9876543210",
            "respondent_email": "amit.singh@email.com",
            "court_name": "District Court, Lucknow",
            "case_number": "123",
            "case_year": "2024",
            "petitioner_name": "Smt. Neha Verma",
            "case_type": "Civil Suit",
            "original_petition_date": "10th January 2024",
            "facts_of_case": "The petitioner has alleged that...",
            "counter_facts": "The allegations are completely false...",
            "legal_objections": "1. The petition is barred by limitation\n2. No cause of action exists",
            "evidence_list": "1. Email correspondence\n2. Witness statements",
            "prayer_relief": "Dismiss the petition with costs"
        }
        
        rendered = template.render(**inputs)
        
        # Verify key content is present
        assert "Amit Kumar Singh" in rendered
        assert "District Court, Lucknow" in rendered
        assert "COUNTER-PETITION" in rendered
        assert "Smt. Neha Verma" in rendered
        assert "barred by limitation" in rendered


class TestLegalFormatting:
    """Test proper legal formatting and language in templates"""
    
    def test_legal_letter_has_proper_structure(self):
        """Verify legal letter has proper formal structure"""
        template = jinja_env.get_template("legal_letter.j2")
        
        # Render with minimal inputs
        inputs = {
            "sender_name": "Test Sender",
            "sender_address": "Test Address",
            "sender_phone": "+91-1234567890",
            "sender_email": "test@email.com",
            "recipient_name": "Test Recipient",
            "recipient_designation": "Test Designation",
            "recipient_address": "Test Address",
            "subject": "Test Subject",
            "incident_date": "Test Date",
            "incident_description": "Test Description",
            "legal_grounds": "Test Grounds",
            "demands": "Test Demands"
        }
        
        rendered = template.render(**inputs)
        
        # Check for proper formal structure
        assert "From:" in rendered
        assert "To:" in rendered
        assert "Subject:" in rendered
        assert "Respected Sir/Madam" in rendered
        assert "Yours faithfully" in rendered
        assert "DECLARATION:" in rendered
        assert "Signature:" in rendered
    
    def test_rti_application_has_legal_provisions(self):
        """Verify RTI application includes legal provisions"""
        template = jinja_env.get_template("rti_application.j2")
        
        inputs = {
            "applicant_name": "Test",
            "applicant_address": "Test",
            "applicant_phone": "+91-1234567890",
            "applicant_email": "test@email.com",
            "department_name": "Test Dept",
            "department_address": "Test Address",
            "information_sought": "Test Info",
            "period_of_information": "Test Period"
        }
        
        rendered = template.render(**inputs)
        
        # Check for legal provisions
        assert "Right to Information Act, 2005" in rendered
        assert "Section 6(1)" in rendered
        assert "Section 7(1)" in rendered
        assert "30 days" in rendered
        assert "48 hours" in rendered
    
    def test_counter_petition_has_court_format(self):
        """Verify counter-petition follows court format"""
        template = jinja_env.get_template("counter_petition.j2")
        
        inputs = {
            "respondent_name": "Test",
            "respondent_address": "Test",
            "respondent_phone": "+91-1234567890",
            "respondent_email": "test@email.com",
            "court_name": "Test Court",
            "case_number": "123",
            "case_year": "2024",
            "petitioner_name": "Test Petitioner",
            "case_type": "Test Case",
            "original_petition_date": "Test Date",
            "facts_of_case": "Test Facts",
            "counter_facts": "Test Counter",
            "legal_objections": "Test Objections",
            "evidence_list": "Test Evidence",
            "prayer_relief": "Test Relief"
        }
        
        rendered = template.render(**inputs)
        
        # Check for court format
        assert "IN THE" in rendered
        assert "... Petitioner" in rendered
        assert "... Respondent" in rendered
        assert "VERSUS" in rendered
        assert "COUNTER-PETITION" in rendered
        assert "VERIFICATION" in rendered
        assert "PRAYER" in rendered
        assert "ANNEXURES:" in rendered


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
