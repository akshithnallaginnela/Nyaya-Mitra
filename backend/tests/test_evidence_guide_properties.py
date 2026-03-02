"""
Property-Based Tests for Evidence Guide System

This file documents the property tests that should be implemented for Task 15.4.
These tests validate the requirements 7.1-7.7 using property-based testing.

Requirements validated:
- Property 31: Case-specific guidance (Requirement 7.1)
- Property 32: Digital preservation instructions (Requirement 7.2)
- Property 33: Admissibility requirements (Requirement 7.3)
- Property 34: Step-by-step format with visuals (Requirement 7.4)
- Property 35: Evidence type checklists (Requirement 7.5)
- Property 36: Tampering warnings (Requirement 7.6)
- Property 37: Digital communication procedures (Requirement 7.7)
"""

import pytest
from fastapi.testclient import TestClient
from main import app
from evidence_guide_content import CaseType
from evidence_guide_generator import get_evidence_guide_generator

client = TestClient(app)


# Property 31: Case-specific guidance
# For any evidence guidance request with a specified case type,
# the returned Evidence_Guide should contain instructions specific to that case type.
def test_property_31_case_specific_guidance():
    """
    Property 31: Case-specific guidance
    Validates: Requirement 7.1
    
    For any case type, the guide should contain case-specific content.
    """
    # Test all case types
    for case_type in CaseType:
        response = client.get(f"/api/evidence/guide?case_type={case_type.value}")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify case type matches
        assert data['case_type'] == case_type.value
        
        # Verify case-specific guidance exists
        assert 'case_specific_guidance' in data
        guidance = data['case_specific_guidance']
        
        # Verify case-specific content is present
        assert len(guidance['key_evidence_types']) > 0
        assert len(guidance['specific_instructions']) > 0
        assert len(guidance['relevant_laws']) > 0
        
        # Verify title and description are case-specific
        assert case_type.value in data['title'].lower() or 'general' in data['title'].lower()
        assert len(data['description']) > 0


# Property 32: Digital preservation instructions
# For any Evidence_Guide generated, the guide should include a section on
# digital evidence preservation with at least 3 specific instructions.
def test_property_32_digital_preservation_instructions():
    """
    Property 32: Digital preservation instructions
    Validates: Requirement 7.2
    
    Every guide must have at least 3 digital preservation instructions.
    """
    # Test with different case types
    case_types = ['harassment', 'fraud', 'general']
    
    for case_type in case_types:
        response = client.get(f"/api/evidence/guide?case_type={case_type}")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify digital preservation section exists
        assert 'digital_preservation' in data
        preservation = data['digital_preservation']
        
        # Verify at least 3 instructions
        assert 'instructions' in preservation
        assert len(preservation['instructions']) >= 3, \
            f"Expected at least 3 instructions, got {len(preservation['instructions'])}"
        
        # Verify instructions are non-empty strings
        for instruction in preservation['instructions']:
            assert isinstance(instruction, str)
            assert len(instruction) > 0


# Property 33: Admissibility requirements
# For any Evidence_Guide generated, the guide should include an explanation
# of legal requirements for evidence admissibility.
def test_property_33_admissibility_requirements():
    """
    Property 33: Admissibility requirements
    Validates: Requirement 7.3
    
    Every guide must include admissibility requirements section.
    """
    response = client.get("/api/evidence/guide?case_type=defamation")
    assert response.status_code == 200
    
    data = response.json()
    
    # Verify admissibility requirements section exists
    assert 'admissibility_requirements' in data
    requirements = data['admissibility_requirements']
    
    # Verify required fields
    assert 'title' in requirements
    assert 'content' in requirements
    assert 'key_laws' in requirements
    
    # Verify content is substantial
    assert len(requirements['content']) > 0
    assert len(requirements['key_laws']) > 0
    
    # Verify content items are non-empty
    for item in requirements['content']:
        assert isinstance(item, str)
        assert len(item) > 0


# Property 34: Step-by-step format with visuals
# For any evidence collection instructions, the guide should be formatted
# as numbered steps and include at least one visual aid reference.
def test_property_34_step_by_step_format_with_visuals():
    """
    Property 34: Step-by-step format with visuals
    Validates: Requirement 7.4
    
    Instructions must be numbered steps with visual aid references.
    """
    response = client.get("/api/evidence/guide?case_type=assault")
    assert response.status_code == 200
    
    data = response.json()
    
    # Verify step-by-step instructions exist
    assert 'step_by_step_instructions' in data
    steps = data['step_by_step_instructions']
    
    # Verify steps are numbered sequentially
    assert len(steps) > 0
    for i, step in enumerate(steps):
        assert 'step_number' in step
        assert step['step_number'] == i + 1
        assert 'title' in step
        assert 'instruction' in step
        assert 'details' in step
    
    # Verify at least one step has a visual aid reference
    has_visual_aid = any(step.get('visual_aid') is not None for step in steps)
    assert has_visual_aid, "At least one step should have a visual aid reference"
    
    # Verify visual aids available list exists
    assert 'visual_aids_available' in data
    assert len(data['visual_aids_available']) > 0


# Property 35: Evidence type checklists
# For any evidence type (physical, digital, testimonial, documentary),
# the Platform should provide a checklist with at least 5 items.
def test_property_35_evidence_type_checklists():
    """
    Property 35: Evidence type checklists
    Validates: Requirement 7.5
    
    Each checklist must have at least 5 items.
    """
    response = client.get("/api/evidence/guide?case_type=fraud")
    assert response.status_code == 200
    
    data = response.json()
    
    # Verify checklists exist
    assert 'evidence_checklists' in data
    checklists = data['evidence_checklists']
    
    # Verify at least one checklist
    assert len(checklists) > 0
    
    # Verify each checklist has at least 5 items
    for checklist in checklists:
        assert 'title' in checklist
        assert 'items' in checklist
        assert len(checklist['items']) >= 5, \
            f"Checklist '{checklist['title']}' has {len(checklist['items'])} items, expected at least 5"
        
        # Verify each item has required fields
        for item in checklist['items']:
            assert 'item' in item
            assert 'required' in item
            assert isinstance(item['item'], str)
            assert len(item['item']) > 0
            assert isinstance(item['required'], bool)


# Property 36: Tampering warnings
# For any Evidence_Guide generated, the guide should include a warning
# about evidence tampering and its legal consequences.
def test_property_36_tampering_warnings():
    """
    Property 36: Tampering warnings
    Validates: Requirement 7.6
    
    Every guide must include tampering warning with legal consequences.
    """
    # Test multiple case types
    case_types = ['harassment', 'fraud', 'cybercrime', 'general']
    
    for case_type in case_types:
        response = client.get(f"/api/evidence/guide?case_type={case_type}")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify tampering warning exists
        assert 'tampering_warning' in data
        warning = data['tampering_warning']
        
        # Verify required fields
        assert 'title' in warning
        assert 'content' in warning
        assert 'legal_consequences' in warning
        
        # Verify content is substantial
        assert len(warning['content']) > 0
        assert len(warning['legal_consequences']) > 0
        
        # Verify warning mentions legal consequences
        legal_text = warning['legal_consequences'].lower()
        assert any(word in legal_text for word in ['section', 'ipc', 'imprisonment', 'punishment'])


# Property 37: Digital communication procedures
# For any case involving digital communications, the Evidence_Guide should
# include specific procedures for screenshots and backups.
def test_property_37_digital_communication_procedures():
    """
    Property 37: Digital communication procedures
    Validates: Requirement 7.7
    
    Every guide must include screenshot and backup procedures.
    """
    response = client.get("/api/evidence/guide?case_type=cybercrime")
    assert response.status_code == 200
    
    data = response.json()
    
    # Verify digital communication procedures exist
    assert 'digital_communication_procedures' in data
    procedures = data['digital_communication_procedures']
    
    # Verify required sections
    assert 'title' in procedures
    assert 'screenshot_guidelines' in procedures
    assert 'backup_procedures' in procedures
    assert 'authentication_tips' in procedures
    
    # Verify screenshot guidelines are substantial
    assert len(procedures['screenshot_guidelines']) > 0
    for guideline in procedures['screenshot_guidelines']:
        assert isinstance(guideline, str)
        assert len(guideline) > 0
    
    # Verify backup procedures are substantial
    assert len(procedures['backup_procedures']) > 0
    for procedure in procedures['backup_procedures']:
        assert isinstance(procedure, str)
        assert len(procedure) > 0
    
    # Verify authentication tips exist
    assert len(procedures['authentication_tips']) > 0


# Integration test: Verify all properties together
def test_all_properties_integration():
    """
    Integration test verifying all properties work together.
    """
    response = client.get("/api/evidence/guide?case_type=harassment&language=en")
    assert response.status_code == 200
    
    data = response.json()
    
    # Property 31: Case-specific
    assert data['case_type'] == 'harassment'
    assert len(data['case_specific_guidance']['key_evidence_types']) > 0
    
    # Property 32: Digital preservation (at least 3 instructions)
    assert len(data['digital_preservation']['instructions']) >= 3
    
    # Property 33: Admissibility requirements
    assert len(data['admissibility_requirements']['content']) > 0
    
    # Property 34: Step-by-step with visuals
    assert len(data['step_by_step_instructions']) > 0
    assert data['step_by_step_instructions'][0]['step_number'] == 1
    
    # Property 35: Checklists with at least 5 items
    for checklist in data['evidence_checklists']:
        assert len(checklist['items']) >= 5
    
    # Property 36: Tampering warning
    assert 'tampering_warning' in data
    assert len(data['tampering_warning']['content']) > 0
    
    # Property 37: Digital communication procedures
    assert len(data['digital_communication_procedures']['screenshot_guidelines']) > 0
    assert len(data['digital_communication_procedures']['backup_procedures']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
