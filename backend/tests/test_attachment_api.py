"""
Unit tests for attachment checklist API functionality
Tests the attachment checklist functions used by the API
"""

import pytest
from attachment_checklist import get_attachment_checklist, get_attachment_summary
from templates.template_config import DocumentType


class TestAttachmentAPI:
    """Test attachment checklist API functions"""
    
    def test_get_attachment_summary_for_api(self):
        """Test getting attachment summary for API response"""
        summary = get_attachment_summary(DocumentType.LEGAL_LETTER)
        
        # Verify structure matches API response model
        assert "total_attachments" in summary
        assert "required_count" in summary
        assert "optional_count" in summary
        assert "attachments" in summary
        
        # Verify data types
        assert isinstance(summary["total_attachments"], int)
        assert isinstance(summary["required_count"], int)
        assert isinstance(summary["optional_count"], int)
        assert isinstance(summary["attachments"], list)
        
        # Verify attachment items have correct structure
        for attachment in summary["attachments"]:
            assert "name" in attachment
            assert "description" in attachment
            assert "required" in attachment
            assert isinstance(attachment["name"], str)
            assert isinstance(attachment["description"], str)
            assert isinstance(attachment["required"], bool)
    
    def test_get_checklist_for_api(self):
        """Test getting checklist for API response"""
        user_inputs = {
            "sender_name": "Test User",
            "reference_number": "REF/123"
        }
        
        checklist = get_attachment_checklist(DocumentType.LEGAL_LETTER, user_inputs)
        
        # Verify structure matches API response
        assert isinstance(checklist, list)
        assert len(checklist) > 0
        
        for item in checklist:
            assert "name" in item
            assert "description" in item
            assert "required" in item
            assert "status" in item
            assert isinstance(item["name"], str)
            assert isinstance(item["description"], str)
            assert isinstance(item["required"], bool)
            assert isinstance(item["status"], str)
    
    def test_all_document_types_have_summaries(self):
        """Test that all document types return valid summaries"""
        for doc_type in DocumentType:
            summary = get_attachment_summary(doc_type)
            
            assert summary is not None
            assert summary["total_attachments"] >= 0
            assert summary["required_count"] >= 0
            assert summary["optional_count"] >= 0
            assert isinstance(summary["attachments"], list)
    
    def test_checklist_response_structure(self):
        """Test checklist response has correct structure for API"""
        # Simulate API request data
        request_data = {
            "document_type": "legal_letter",
            "inputs": {
                "sender_name": "Test User",
                "sender_email": "test@example.com"
            }
        }
        
        doc_type = DocumentType(request_data["document_type"])
        checklist = get_attachment_checklist(doc_type, request_data["inputs"])
        summary = get_attachment_summary(doc_type)
        
        # Simulate API response
        response = {
            "document_type": request_data["document_type"],
            "checklist": checklist,
            "total_attachments": summary["total_attachments"],
            "required_count": summary["required_count"],
            "optional_count": summary["optional_count"]
        }
        
        # Verify response structure
        assert "document_type" in response
        assert "checklist" in response
        assert "total_attachments" in response
        assert "required_count" in response
        assert "optional_count" in response
        
        assert isinstance(response["checklist"], list)
        assert isinstance(response["total_attachments"], int)
        assert isinstance(response["required_count"], int)
        assert isinstance(response["optional_count"], int)
    
    def test_template_response_includes_attachment_summary(self):
        """Test that template response includes attachment summary"""
        # Simulate template listing response
        from templates.template_config import TEMPLATE_REGISTRY
        
        templates = []
        for doc_type, config in TEMPLATE_REGISTRY.items():
            attachment_summary = get_attachment_summary(doc_type)
            
            template_response = {
                "document_type": doc_type.value,
                "name": config["name"],
                "description": config["description"],
                "category": config["category"],
                "attachment_summary": attachment_summary
            }
            
            templates.append(template_response)
        
        # Verify all templates have attachment summaries
        assert len(templates) == len(DocumentType)
        
        for template in templates:
            assert "attachment_summary" in template
            assert "total_attachments" in template["attachment_summary"]
            assert "required_count" in template["attachment_summary"]
            assert "optional_count" in template["attachment_summary"]
            assert "attachments" in template["attachment_summary"]
    
    def test_conditional_checklist_for_different_inputs(self):
        """Test that checklist changes based on user inputs"""
        # Test with reference number
        inputs_with_ref = {"reference_number": "REF/123"}
        checklist_with_ref = get_attachment_checklist(DocumentType.LEGAL_LETTER, inputs_with_ref)
        
        # Test without reference number
        inputs_without_ref = {}
        checklist_without_ref = get_attachment_checklist(DocumentType.LEGAL_LETTER, inputs_without_ref)
        
        # Checklists should be different
        assert len(checklist_with_ref) != len(checklist_without_ref)
        
        # With reference should have more items
        assert len(checklist_with_ref) > len(checklist_without_ref)
    
    def test_bpl_status_affects_rti_checklist(self):
        """Test that BPL status affects RTI application checklist"""
        # Test with BPL status
        inputs_bpl = {"bpl_status": True}
        checklist_bpl = get_attachment_checklist(DocumentType.RTI_APPLICATION, inputs_bpl)
        
        # Test without BPL status
        inputs_no_bpl = {"bpl_status": False}
        checklist_no_bpl = get_attachment_checklist(DocumentType.RTI_APPLICATION, inputs_no_bpl)
        
        # Check that BPL certificate is in BPL checklist
        bpl_cert_in_bpl = any(item["name"] == "BPL Certificate" for item in checklist_bpl)
        assert bpl_cert_in_bpl
        
        # Check that fee payment is in non-BPL checklist
        fee_in_no_bpl = any(item["name"] == "Application Fee Payment Receipt" for item in checklist_no_bpl)
        assert fee_in_no_bpl
        
        # Check that fee payment is NOT in BPL checklist
        fee_in_bpl = any(item["name"] == "Application Fee Payment Receipt" for item in checklist_bpl)
        assert not fee_in_bpl
        
        # Check that BPL certificate is NOT in non-BPL checklist
        bpl_cert_in_no_bpl = any(item["name"] == "BPL Certificate" for item in checklist_no_bpl)
        assert not bpl_cert_in_no_bpl
