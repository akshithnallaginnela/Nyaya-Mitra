"""
Integration tests for attachment checklist in document generation
Tests that checklist is properly included in generated documents
"""

import pytest
from document_generator_service import DocumentGeneratorService
from templates.template_config import DocumentType


class TestAttachmentChecklistIntegration:
    """Test attachment checklist integration with document generation"""
    
    @pytest.fixture
    def service(self):
        """Create document generator service instance"""
        return DocumentGeneratorService()
    
    def test_legal_letter_includes_checklist(self, service):
        """Test that legal letter includes attachment checklist"""
        inputs = {
            "sender_name": "Test User",
            "sender_address": "123 Test Street, Test City",
            "sender_phone": "+91-9876543210",
            "sender_email": "test@example.com",
            "recipient_name": "Recipient Name",
            "recipient_designation": "Principal",
            "recipient_address": "456 College Road",
            "subject": "Test Subject",
            "incident_date": "15th January 2024",
            "incident_description": "Test incident description",
            "legal_grounds": "Test legal grounds",
            "demands": "Test demands"
        }
        
        text_content, pdf_bytes = service.generate_document(DocumentType.LEGAL_LETTER, inputs)
        
        # Check that checklist is included
        assert "ATTACHMENT CHECKLIST" in text_content
        assert "REQUIRED ATTACHMENTS:" in text_content
        assert "Copy of Identity Proof" in text_content
        assert "Address Proof" in text_content
        assert "Evidence of Incident" in text_content
        assert "[ ] Attached" in text_content
    
    def test_rti_application_includes_checklist(self, service):
        """Test that RTI application includes attachment checklist"""
        inputs = {
            "applicant_name": "Test Applicant",
            "applicant_address": "123 Test Street",
            "applicant_phone": "+91-9876543210",
            "applicant_email": "test@example.com",
            "department_name": "Test Department",
            "department_address": "456 Dept Street",
            "information_sought": "Test information",
            "period_of_information": "January 2024"
        }
        
        text_content, pdf_bytes = service.generate_document(DocumentType.RTI_APPLICATION, inputs)
        
        # Check that checklist is included
        assert "ATTACHMENT CHECKLIST" in text_content
        assert "REQUIRED ATTACHMENTS:" in text_content
        assert "Application Fee Payment Receipt" in text_content
        assert "Copy of Identity Proof" in text_content
    
    def test_counter_petition_includes_checklist(self, service):
        """Test that counter-petition includes attachment checklist"""
        inputs = {
            "respondent_name": "Test Respondent",
            "respondent_address": "123 Test Street",
            "respondent_phone": "+91-9876543210",
            "respondent_email": "test@example.com",
            "court_name": "Test Court",
            "case_number": "123",
            "case_year": "2024",
            "petitioner_name": "Test Petitioner",
            "case_type": "Civil Suit",
            "original_petition_date": "10th January 2024",
            "facts_of_case": "Test facts",
            "counter_facts": "Test counter facts",
            "legal_objections": "Test objections",
            "evidence_list": "Test evidence",
            "prayer_relief": "Test relief"
        }
        
        text_content, pdf_bytes = service.generate_document(DocumentType.COUNTER_PETITION, inputs)
        
        # Check that checklist is included
        assert "ATTACHMENT CHECKLIST" in text_content
        assert "REQUIRED ATTACHMENTS:" in text_content
        assert "Copy of Original Petition" in text_content
        assert "Court Notice/Summons" in text_content
    
    def test_checklist_conditional_items_with_reference(self, service):
        """Test that conditional items appear when conditions are met"""
        inputs = {
            "sender_name": "Test User",
            "sender_address": "123 Test Street",
            "sender_phone": "+91-9876543210",
            "sender_email": "test@example.com",
            "recipient_name": "Recipient Name",
            "recipient_designation": "Principal",
            "recipient_address": "456 College Road",
            "subject": "Test Subject",
            "incident_date": "15th January 2024",
            "incident_description": "Test incident",
            "legal_grounds": "Test grounds",
            "demands": "Test demands",
            "reference_number": "REF/2024/123"  # This should trigger conditional attachment
        }
        
        text_content, pdf_bytes = service.generate_document(DocumentType.LEGAL_LETTER, inputs)
        
        # Check that conditional item is included
        assert "Previous Correspondence" in text_content
    
    def test_checklist_conditional_items_without_reference(self, service):
        """Test that conditional items don't appear when conditions are not met"""
        inputs = {
            "sender_name": "Test User",
            "sender_address": "123 Test Street",
            "sender_phone": "+91-9876543210",
            "sender_email": "test@example.com",
            "recipient_name": "Recipient Name",
            "recipient_designation": "Principal",
            "recipient_address": "456 College Road",
            "subject": "Test Subject",
            "incident_date": "15th January 2024",
            "incident_description": "Test incident",
            "legal_grounds": "Test grounds",
            "demands": "Test demands"
            # No reference_number
        }
        
        text_content, pdf_bytes = service.generate_document(DocumentType.LEGAL_LETTER, inputs)
        
        # Check that conditional item is NOT included
        assert "Previous Correspondence" not in text_content
    
    def test_rti_checklist_with_bpl_status(self, service):
        """Test RTI checklist changes based on BPL status"""
        inputs_bpl = {
            "applicant_name": "Test Applicant",
            "applicant_address": "123 Test Street",
            "applicant_phone": "+91-9876543210",
            "applicant_email": "test@example.com",
            "department_name": "Test Department",
            "department_address": "456 Dept Street",
            "information_sought": "Test information",
            "period_of_information": "January 2024",
            "bpl_status": True
        }
        
        text_content_bpl, _ = service.generate_document(DocumentType.RTI_APPLICATION, inputs_bpl)
        
        # With BPL status, should include BPL certificate
        assert "BPL Certificate" in text_content_bpl
        # Should NOT include fee payment
        assert "Application Fee Payment Receipt" not in text_content_bpl
        
        # Test without BPL status
        inputs_no_bpl = inputs_bpl.copy()
        inputs_no_bpl["bpl_status"] = False
        
        text_content_no_bpl, _ = service.generate_document(DocumentType.RTI_APPLICATION, inputs_no_bpl)
        
        # Without BPL status, should include fee payment
        assert "Application Fee Payment Receipt" in text_content_no_bpl
        # Should NOT include BPL certificate
        assert "BPL Certificate" not in text_content_no_bpl
    
    def test_counter_petition_checklist_with_advocate(self, service):
        """Test counter-petition checklist includes Vakalatnama when advocate is present"""
        inputs = {
            "respondent_name": "Test Respondent",
            "respondent_address": "123 Test Street",
            "respondent_phone": "+91-9876543210",
            "respondent_email": "test@example.com",
            "court_name": "Test Court",
            "case_number": "123",
            "case_year": "2024",
            "petitioner_name": "Test Petitioner",
            "case_type": "Civil Suit",
            "original_petition_date": "10th January 2024",
            "facts_of_case": "Test facts",
            "counter_facts": "Test counter facts",
            "legal_objections": "Test objections",
            "evidence_list": "Test evidence",
            "prayer_relief": "Test relief",
            "advocate_name": "Adv. Ramesh Kumar"
        }
        
        text_content, _ = service.generate_document(DocumentType.COUNTER_PETITION, inputs)
        
        # Should include Vakalatnama
        assert "Vakalatnama" in text_content
    
    def test_checklist_has_checkboxes(self, service):
        """Test that checklist includes checkboxes for user to mark"""
        inputs = {
            "sender_name": "Test User",
            "sender_address": "123 Test Street",
            "sender_phone": "+91-9876543210",
            "sender_email": "test@example.com",
            "recipient_name": "Recipient Name",
            "recipient_designation": "Principal",
            "recipient_address": "456 College Road",
            "subject": "Test Subject",
            "incident_date": "15th January 2024",
            "incident_description": "Test incident",
            "legal_grounds": "Test grounds",
            "demands": "Test demands"
        }
        
        text_content, _ = service.generate_document(DocumentType.LEGAL_LETTER, inputs)
        
        # Check for checkboxes
        assert "[ ] Attached" in text_content
        assert "[ ] Not Applicable" in text_content
    
    def test_checklist_has_instructions(self, service):
        """Test that checklist includes user instructions"""
        inputs = {
            "sender_name": "Test User",
            "sender_address": "123 Test Street",
            "sender_phone": "+91-9876543210",
            "sender_email": "test@example.com",
            "recipient_name": "Recipient Name",
            "recipient_designation": "Principal",
            "recipient_address": "456 College Road",
            "subject": "Test Subject",
            "incident_date": "15th January 2024",
            "incident_description": "Test incident",
            "legal_grounds": "Test grounds",
            "demands": "Test demands"
        }
        
        text_content, _ = service.generate_document(DocumentType.LEGAL_LETTER, inputs)
        
        # Check for instructions
        assert "Please ensure the following documents are attached" in text_content
        assert "Keep copies of all attachments for your records" in text_content
    
    def test_checklist_separates_required_and_optional(self, service):
        """Test that checklist clearly separates required and optional attachments"""
        inputs = {
            "sender_name": "Test User",
            "sender_address": "123 Test Street",
            "sender_phone": "+91-9876543210",
            "sender_email": "test@example.com",
            "recipient_name": "Recipient Name",
            "recipient_designation": "Principal",
            "recipient_address": "456 College Road",
            "subject": "Test Subject",
            "incident_date": "15th January 2024",
            "incident_description": "Test incident",
            "legal_grounds": "Test grounds",
            "demands": "Test demands"
        }
        
        text_content, _ = service.generate_document(DocumentType.LEGAL_LETTER, inputs)
        
        # Check for section headers
        assert "REQUIRED ATTACHMENTS:" in text_content
        assert "OPTIONAL ATTACHMENTS" in text_content
        
        # Check that required section comes before optional
        required_pos = text_content.index("REQUIRED ATTACHMENTS:")
        optional_pos = text_content.index("OPTIONAL ATTACHMENTS")
        assert required_pos < optional_pos
