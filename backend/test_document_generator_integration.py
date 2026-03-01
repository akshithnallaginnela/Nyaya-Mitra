"""
Integration test for document generator service
Tests the complete workflow from input to PDF generation
"""

import pytest
from document_generator_service import get_document_generator_service
from templates.template_config import DocumentType
from pathlib import Path
import tempfile


class TestDocumentGeneratorIntegration:
    """Integration tests for complete document generation workflow"""
    
    @pytest.fixture
    def service(self):
        """Get document generator service"""
        return get_document_generator_service()
    
    def test_complete_legal_letter_workflow(self, service):
        """Test complete workflow: validate -> render -> generate PDF"""
        # Step 1: Prepare user inputs
        user_inputs = {
            "sender_name": "Rajesh Kumar Sharma",
            "sender_address": "123, MG Road, Bangalore, Karnataka - 560001",
            "sender_phone": "+91-9876543210",
            "sender_email": "rajesh.sharma@email.com",
            "recipient_name": "Dr. Priya Mehta",
            "recipient_designation": "Principal, ABC College",
            "recipient_address": "ABC College, College Road, Mumbai, Maharashtra - 400001",
            "subject": "Complaint regarding false allegations and harassment",
            "incident_date": "15th January 2024",
            "incident_description": "On 15th January 2024, I was falsely accused of misconduct by a fellow student without any evidence. This has caused severe mental distress and damage to my reputation.",
            "legal_grounds": "Section 499 IPC (Defamation), Article 21 of Constitution (Right to Life and Personal Liberty)",
            "demands": "1. Immediate withdrawal of false allegations\n2. Written apology\n3. Compensation for mental harassment and reputational damage",
            "date": "20th January 2024",
            "timeline": "7 days",
            "consequences": "file a defamation case and approach the police",
            "attachments": ["Copy of ID proof", "Screenshots of messages", "Witness statements"]
        }
        
        # Step 2: Validate inputs
        is_valid, errors = service.validate_inputs(DocumentType.LEGAL_LETTER, user_inputs)
        assert is_valid, f"Validation failed: {errors}"
        
        # Step 3: Generate document (both text and PDF)
        text_content, pdf_bytes = service.generate_document(DocumentType.LEGAL_LETTER, user_inputs)
        
        # Step 4: Verify text content
        assert text_content is not None
        assert len(text_content) > 0
        assert "Rajesh Kumar Sharma" in text_content
        assert "Dr. Priya Mehta" in text_content
        assert "false allegations" in text_content
        assert "Section 499 IPC" in text_content
        assert "7 days" in text_content
        assert "defamation case" in text_content
        assert "Copy of ID proof" in text_content
        
        # Step 5: Verify PDF generation
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b'%PDF'
        
        # Step 6: Verify PDF can be saved to file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as f:
            f.write(pdf_bytes)
            temp_path = Path(f.name)
        
        assert temp_path.exists()
        assert temp_path.stat().st_size > 0
        
        # Cleanup
        temp_path.unlink()
    
    def test_complete_rti_application_workflow(self, service):
        """Test complete RTI application generation workflow"""
        user_inputs = {
            "applicant_name": "Priya Sharma",
            "applicant_address": "456, Park Street, Kolkata, West Bengal - 700016",
            "applicant_phone": "+91-9876543210",
            "applicant_email": "priya.sharma@email.com",
            "department_name": "Delhi Police",
            "department_address": "Police Headquarters, ITO, New Delhi - 110002",
            "information_sought": "1. Copy of FIR No. 123/2024 registered at XYZ Police Station\n2. Current status of investigation in the said FIR\n3. Names and designations of investigating officers assigned to the case",
            "period_of_information": "January 2024 to March 2024",
            "date": "25th January 2024",
            "purpose": "To understand the status of my complaint and take appropriate legal action",
            "preferred_format": "Certified photocopies",
            "application_fee": "₹10"
        }
        
        # Validate and generate
        is_valid, errors = service.validate_inputs(DocumentType.RTI_APPLICATION, user_inputs)
        assert is_valid, f"Validation failed: {errors}"
        
        text_content, pdf_bytes = service.generate_document(DocumentType.RTI_APPLICATION, user_inputs)
        
        # Verify content
        assert "Priya Sharma" in text_content
        assert "Delhi Police" in text_content
        assert "FIR No. 123/2024" in text_content
        assert "Right to Information Act, 2005" in text_content
        assert "Section 6(1)" in text_content
        assert "Certified photocopies" in text_content
        
        # Verify PDF
        assert pdf_bytes[:4] == b'%PDF'
    
    def test_complete_counter_petition_workflow(self, service):
        """Test complete counter-petition generation workflow"""
        user_inputs = {
            "respondent_name": "Amit Kumar Singh",
            "respondent_address": "789, Civil Lines, Lucknow, Uttar Pradesh - 226001",
            "respondent_phone": "+91-9876543210",
            "respondent_email": "amit.singh@email.com",
            "court_name": "District Court, Lucknow",
            "case_number": "123",
            "case_year": "2024",
            "petitioner_name": "Smt. Neha Verma",
            "case_type": "Civil Suit",
            "original_petition_date": "10th January 2024",
            "facts_of_case": "The petitioner has alleged that the respondent breached a contract and caused financial loss of Rs. 5 lakhs.",
            "counter_facts": "The allegations made by the petitioner are completely false and fabricated. No such contract existed between the parties. The petitioner is attempting to extort money through false legal proceedings.",
            "legal_objections": "1. The petition is barred by limitation under Article 113 of the Limitation Act\n2. The court lacks territorial jurisdiction as the alleged cause of action did not arise within its jurisdiction\n3. No valid cause of action exists as no contract was ever executed",
            "evidence_list": "1. Email correspondence showing no contract discussions\n2. Witness statement of Mr. Ramesh Kumar\n3. Bank statements showing no financial transactions with petitioner",
            "prayer_relief": "1. Declare the allegations as false and malicious\n2. Dismiss the petition with exemplary costs\n3. Award compensation of Rs. 2 lakhs for harassment and legal expenses",
            "date": "30th January 2024",
            "advocate_name": "Adv. Ramesh Chandra",
            "advocate_enrollment": "UP/12345/2010",
            "attachments": ["Email correspondence", "Witness affidavits", "Bank statements"]
        }
        
        # Validate and generate
        is_valid, errors = service.validate_inputs(DocumentType.COUNTER_PETITION, user_inputs)
        assert is_valid, f"Validation failed: {errors}"
        
        text_content, pdf_bytes = service.generate_document(DocumentType.COUNTER_PETITION, user_inputs)
        
        # Verify content
        assert "Amit Kumar Singh" in text_content
        assert "District Court, Lucknow" in text_content
        assert "Smt. Neha Verma" in text_content
        assert "COUNTER-PETITION" in text_content
        assert "barred by limitation" in text_content
        assert "Adv. Ramesh Chandra" in text_content
        assert "UP/12345/2010" in text_content
        
        # Verify PDF
        assert pdf_bytes[:4] == b'%PDF'
    
    def test_workflow_with_minimal_inputs(self, service):
        """Test workflow with only required fields (no optional fields)"""
        user_inputs = {
            "sender_name": "Minimal User",
            "sender_address": "123 Street, City",
            "sender_phone": "+91-9876543210",
            "sender_email": "minimal@email.com",
            "recipient_name": "Recipient Name",
            "recipient_designation": "Designation",
            "recipient_address": "456 Avenue, City",
            "subject": "Test Subject",
            "incident_date": "15th January 2024",
            "incident_description": "Brief description of incident",
            "legal_grounds": "Applicable legal provisions",
            "demands": "Specific demands"
        }
        
        # Should work with only required fields
        is_valid, errors = service.validate_inputs(DocumentType.LEGAL_LETTER, user_inputs)
        assert is_valid
        
        text_content, pdf_bytes = service.generate_document(DocumentType.LEGAL_LETTER, user_inputs)
        
        # Should have placeholders for optional fields
        assert text_content is not None
        assert "Minimal User" in text_content
        assert "15 days" in text_content  # Default timeline
        assert "appropriate legal action" in text_content  # Default consequences
        
        # PDF should still be generated
        assert pdf_bytes[:4] == b'%PDF'
    
    def test_workflow_error_handling(self, service):
        """Test that workflow properly handles validation errors"""
        # Invalid inputs - missing required fields
        invalid_inputs = {
            "sender_name": "Test User",
            "sender_email": "invalid-email"  # Invalid email, missing other required fields
        }
        
        # Validation should fail
        is_valid, errors = service.validate_inputs(DocumentType.LEGAL_LETTER, invalid_inputs)
        assert not is_valid
        assert len(errors) > 0
        
        # Generate should raise error
        with pytest.raises(ValueError, match="Validation errors"):
            service.generate_document(DocumentType.LEGAL_LETTER, invalid_inputs)
    
    def test_all_document_types_workflow(self, service):
        """Test that all document types can be generated successfully"""
        # Legal Letter
        legal_letter_inputs = {
            "sender_name": "User 1",
            "sender_address": "Address 1",
            "sender_phone": "+91-1111111111",
            "sender_email": "user1@email.com",
            "recipient_name": "Recipient 1",
            "recipient_designation": "Designation 1",
            "recipient_address": "Address 2",
            "subject": "Subject 1",
            "incident_date": "Date 1",
            "incident_description": "Description 1",
            "legal_grounds": "Grounds 1",
            "demands": "Demands 1"
        }
        
        # RTI Application
        rti_inputs = {
            "applicant_name": "User 2",
            "applicant_address": "Address 2",
            "applicant_phone": "+91-2222222222",
            "applicant_email": "user2@email.com",
            "department_name": "Department 1",
            "department_address": "Address 3",
            "information_sought": "Information 1",
            "period_of_information": "Period 1"
        }
        
        # Counter-Petition
        counter_petition_inputs = {
            "respondent_name": "User 3",
            "respondent_address": "Address 3",
            "respondent_phone": "+91-3333333333",
            "respondent_email": "user3@email.com",
            "court_name": "Court 1",
            "case_number": "001",
            "case_year": "2024",
            "petitioner_name": "Petitioner 1",
            "case_type": "Type 1",
            "original_petition_date": "Date 1",
            "facts_of_case": "Facts 1",
            "counter_facts": "Counter Facts 1",
            "legal_objections": "Objections 1",
            "evidence_list": "Evidence 1",
            "prayer_relief": "Relief 1"
        }
        
        # Test all three document types
        for doc_type, inputs in [
            (DocumentType.LEGAL_LETTER, legal_letter_inputs),
            (DocumentType.RTI_APPLICATION, rti_inputs),
            (DocumentType.COUNTER_PETITION, counter_petition_inputs)
        ]:
            is_valid, errors = service.validate_inputs(doc_type, inputs)
            assert is_valid, f"Validation failed for {doc_type}: {errors}"
            
            text_content, pdf_bytes = service.generate_document(doc_type, inputs)
            assert text_content is not None
            assert len(text_content) > 0
            assert pdf_bytes[:4] == b'%PDF'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
