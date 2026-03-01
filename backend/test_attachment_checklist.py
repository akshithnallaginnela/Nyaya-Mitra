"""
Tests for Attachment Checklist Generator
"""

import pytest
from attachment_checklist import (
    get_attachment_checklist,
    format_checklist_for_document,
    get_attachment_summary,
    ATTACHMENT_REGISTRY
)
from templates.template_config import DocumentType


class TestAttachmentChecklist:
    """Test attachment checklist generation"""
    
    def test_legal_letter_checklist_basic(self):
        """Test basic checklist generation for legal letter"""
        checklist = get_attachment_checklist(DocumentType.LEGAL_LETTER)
        
        assert len(checklist) > 0
        assert any(item["name"] == "Copy of Identity Proof" for item in checklist)
        assert any(item["name"] == "Address Proof" for item in checklist)
        assert any(item["name"] == "Evidence of Incident" for item in checklist)
    
    def test_legal_letter_checklist_with_reference(self):
        """Test checklist includes previous correspondence when reference number provided"""
        user_inputs = {
            "reference_number": "REF/2024/123"
        }
        
        checklist = get_attachment_checklist(DocumentType.LEGAL_LETTER, user_inputs)
        
        # Should include previous correspondence
        assert any(item["name"] == "Previous Correspondence" for item in checklist)
    
    def test_legal_letter_checklist_without_reference(self):
        """Test checklist excludes previous correspondence when no reference number"""
        user_inputs = {}
        
        checklist = get_attachment_checklist(DocumentType.LEGAL_LETTER, user_inputs)
        
        # Should not include previous correspondence
        assert not any(item["name"] == "Previous Correspondence" for item in checklist)
    
    def test_rti_application_checklist_with_bpl(self):
        """Test RTI checklist with BPL status"""
        user_inputs = {
            "bpl_status": True
        }
        
        checklist = get_attachment_checklist(DocumentType.RTI_APPLICATION, user_inputs)
        
        # Should include BPL certificate
        assert any(item["name"] == "BPL Certificate" for item in checklist)
        # Should NOT include fee payment receipt
        assert not any(item["name"] == "Application Fee Payment Receipt" for item in checklist)
    
    def test_rti_application_checklist_without_bpl(self):
        """Test RTI checklist without BPL status"""
        user_inputs = {
            "bpl_status": False
        }
        
        checklist = get_attachment_checklist(DocumentType.RTI_APPLICATION, user_inputs)
        
        # Should include fee payment receipt
        assert any(item["name"] == "Application Fee Payment Receipt" for item in checklist)
        # Should NOT include BPL certificate
        assert not any(item["name"] == "BPL Certificate" for item in checklist)
    
    def test_counter_petition_checklist_with_advocate(self):
        """Test counter-petition checklist with advocate"""
        user_inputs = {
            "advocate_name": "Adv. Ramesh Kumar"
        }
        
        checklist = get_attachment_checklist(DocumentType.COUNTER_PETITION, user_inputs)
        
        # Should include Vakalatnama
        assert any(item["name"] == "Vakalatnama" for item in checklist)
    
    def test_counter_petition_checklist_without_advocate(self):
        """Test counter-petition checklist without advocate"""
        user_inputs = {}
        
        checklist = get_attachment_checklist(DocumentType.COUNTER_PETITION, user_inputs)
        
        # Should NOT include Vakalatnama
        assert not any(item["name"] == "Vakalatnama" for item in checklist)
    
    def test_checklist_has_required_and_optional(self):
        """Test checklist contains both required and optional items"""
        checklist = get_attachment_checklist(DocumentType.LEGAL_LETTER)
        
        required_items = [item for item in checklist if item["required"]]
        optional_items = [item for item in checklist if not item["required"]]
        
        assert len(required_items) > 0
        assert len(optional_items) > 0
    
    def test_checklist_item_structure(self):
        """Test each checklist item has correct structure"""
        checklist = get_attachment_checklist(DocumentType.LEGAL_LETTER)
        
        for item in checklist:
            assert "name" in item
            assert "description" in item
            assert "required" in item
            assert "status" in item
            assert isinstance(item["name"], str)
            assert isinstance(item["description"], str)
            assert isinstance(item["required"], bool)
            assert item["status"] == "pending"


class TestChecklistFormatting:
    """Test checklist formatting for document inclusion"""
    
    def test_format_checklist_basic(self):
        """Test basic checklist formatting"""
        checklist = get_attachment_checklist(DocumentType.LEGAL_LETTER)
        formatted = format_checklist_for_document(checklist)
        
        assert "ATTACHMENT CHECKLIST" in formatted
        assert "REQUIRED ATTACHMENTS:" in formatted
        assert "OPTIONAL ATTACHMENTS" in formatted
        assert "[ ] Attached" in formatted
    
    def test_format_empty_checklist(self):
        """Test formatting empty checklist"""
        formatted = format_checklist_for_document([])
        
        assert "[NO ATTACHMENTS REQUIRED]" in formatted
    
    def test_format_checklist_has_all_items(self):
        """Test formatted checklist includes all items"""
        checklist = get_attachment_checklist(DocumentType.LEGAL_LETTER)
        formatted = format_checklist_for_document(checklist)
        
        for item in checklist:
            assert item["name"] in formatted
            assert item["description"] in formatted
    
    def test_format_checklist_separates_required_optional(self):
        """Test formatted checklist separates required and optional items"""
        checklist = get_attachment_checklist(DocumentType.LEGAL_LETTER)
        formatted = format_checklist_for_document(checklist)
        
        # Check structure
        assert formatted.index("REQUIRED ATTACHMENTS:") < formatted.index("OPTIONAL ATTACHMENTS")
    
    def test_format_checklist_includes_instructions(self):
        """Test formatted checklist includes user instructions"""
        checklist = get_attachment_checklist(DocumentType.LEGAL_LETTER)
        formatted = format_checklist_for_document(checklist)
        
        assert "Please ensure the following documents are attached" in formatted
        assert "Keep copies of all attachments for your records" in formatted


class TestAttachmentSummary:
    """Test attachment summary generation"""
    
    def test_summary_structure(self):
        """Test summary has correct structure"""
        summary = get_attachment_summary(DocumentType.LEGAL_LETTER)
        
        assert "total_attachments" in summary
        assert "required_count" in summary
        assert "optional_count" in summary
        assert "attachments" in summary
    
    def test_summary_counts(self):
        """Test summary counts are correct"""
        summary = get_attachment_summary(DocumentType.LEGAL_LETTER)
        
        assert summary["total_attachments"] == summary["required_count"] + summary["optional_count"]
        assert summary["required_count"] > 0
        assert summary["total_attachments"] > 0
    
    def test_summary_attachments_list(self):
        """Test summary attachments list structure"""
        summary = get_attachment_summary(DocumentType.LEGAL_LETTER)
        
        for attachment in summary["attachments"]:
            assert "name" in attachment
            assert "description" in attachment
            assert "required" in attachment
    
    def test_summary_for_all_document_types(self):
        """Test summary generation for all document types"""
        for doc_type in DocumentType:
            summary = get_attachment_summary(doc_type)
            
            assert summary["total_attachments"] >= 0
            assert summary["required_count"] >= 0
            assert summary["optional_count"] >= 0
            assert isinstance(summary["attachments"], list)


class TestAttachmentRegistry:
    """Test attachment registry configuration"""
    
    def test_registry_has_all_document_types(self):
        """Test registry includes all document types"""
        for doc_type in DocumentType:
            assert doc_type in ATTACHMENT_REGISTRY
    
    def test_registry_items_are_valid(self):
        """Test all registry items have valid structure"""
        for doc_type, attachments in ATTACHMENT_REGISTRY.items():
            assert isinstance(attachments, list)
            assert len(attachments) > 0
            
            for attachment in attachments:
                assert hasattr(attachment, "name")
                assert hasattr(attachment, "description")
                assert hasattr(attachment, "required")
                assert isinstance(attachment.name, str)
                assert isinstance(attachment.description, str)
                assert isinstance(attachment.required, bool)


class TestConditionalAttachments:
    """Test conditional attachment logic"""
    
    def test_conditional_attachment_included_when_condition_met(self):
        """Test conditional attachment is included when condition is met"""
        user_inputs = {
            "reference_number": "REF/123"
        }
        
        checklist = get_attachment_checklist(DocumentType.LEGAL_LETTER, user_inputs)
        
        # Previous Correspondence has condition "reference_number"
        assert any(item["name"] == "Previous Correspondence" for item in checklist)
    
    def test_conditional_attachment_excluded_when_condition_not_met(self):
        """Test conditional attachment is excluded when condition is not met"""
        user_inputs = {}
        
        checklist = get_attachment_checklist(DocumentType.LEGAL_LETTER, user_inputs)
        
        # Previous Correspondence should not be included
        assert not any(item["name"] == "Previous Correspondence" for item in checklist)
    
    def test_bpl_status_true_condition(self):
        """Test BPL status true condition"""
        user_inputs = {"bpl_status": True}
        
        checklist = get_attachment_checklist(DocumentType.RTI_APPLICATION, user_inputs)
        
        # BPL certificate should be included
        assert any(item["name"] == "BPL Certificate" for item in checklist)
    
    def test_bpl_status_false_condition(self):
        """Test BPL status false condition"""
        user_inputs = {"bpl_status": False}
        
        checklist = get_attachment_checklist(DocumentType.RTI_APPLICATION, user_inputs)
        
        # Fee payment should be included
        assert any(item["name"] == "Application Fee Payment Receipt" for item in checklist)
    
    def test_not_bpl_condition(self):
        """Test not_bpl condition logic"""
        # When BPL is True, not_bpl items should be excluded
        user_inputs_bpl = {"bpl_status": True}
        checklist_bpl = get_attachment_checklist(DocumentType.RTI_APPLICATION, user_inputs_bpl)
        assert not any(item["name"] == "Application Fee Payment Receipt" for item in checklist_bpl)
        
        # When BPL is False, not_bpl items should be included
        user_inputs_not_bpl = {"bpl_status": False}
        checklist_not_bpl = get_attachment_checklist(DocumentType.RTI_APPLICATION, user_inputs_not_bpl)
        assert any(item["name"] == "Application Fee Payment Receipt" for item in checklist_not_bpl)


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_invalid_document_type(self):
        """Test handling of invalid document type"""
        # Should return empty list for invalid type
        checklist = get_attachment_checklist("invalid_type")
        assert checklist == []
    
    def test_none_user_inputs(self):
        """Test handling of None user inputs"""
        checklist = get_attachment_checklist(DocumentType.LEGAL_LETTER, None)
        
        # Should still return valid checklist
        assert len(checklist) > 0
    
    def test_empty_user_inputs(self):
        """Test handling of empty user inputs"""
        checklist = get_attachment_checklist(DocumentType.LEGAL_LETTER, {})
        
        # Should return valid checklist
        assert len(checklist) > 0
    
    def test_extra_user_inputs(self):
        """Test handling of extra user inputs not related to conditions"""
        user_inputs = {
            "sender_name": "Test User",
            "extra_field": "Extra Value",
            "another_field": 123
        }
        
        checklist = get_attachment_checklist(DocumentType.LEGAL_LETTER, user_inputs)
        
        # Should not cause errors
        assert len(checklist) > 0
