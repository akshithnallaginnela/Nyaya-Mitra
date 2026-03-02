"""
Evidence Guide API Router
Provides endpoints for retrieving evidence documentation guides.

Requirements: 7.1 (Case-specific guidance)
"""

from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from evidence_guide_generator import get_evidence_guide_generator
from evidence_guide_content import CaseType


router = APIRouter(prefix="/api/evidence", tags=["evidence"])


# Response models
class VisualAidResponse(BaseModel):
    """Visual aid reference information"""
    icon: str
    description: str
    reference: str


class StepResponse(BaseModel):
    """Step-by-step instruction"""
    step_number: int
    title: str
    instruction: str
    visual_aid: Optional[Dict[str, str]] = None
    details: List[str]


class ChecklistItemResponse(BaseModel):
    """Checklist item"""
    item: str
    required: bool
    visual_aid: Optional[str] = None


class ChecklistResponse(BaseModel):
    """Evidence checklist"""
    title: str
    icon: str
    items: List[ChecklistItemResponse]


class TamperingWarningResponse(BaseModel):
    """Tampering warning information"""
    title: str
    content: List[str]
    legal_consequences: str


class AdmissibilityRequirementsResponse(BaseModel):
    """Admissibility requirements information"""
    title: str
    content: List[str]
    key_laws: List[str]


class DigitalPreservationResponse(BaseModel):
    """Digital preservation instructions"""
    title: str
    instructions: List[str]
    best_practices: List[str]


class DigitalCommunicationResponse(BaseModel):
    """Digital communication procedures"""
    title: str
    screenshot_guidelines: List[str]
    backup_procedures: List[str]
    authentication_tips: List[str]


class CaseSpecificGuidanceResponse(BaseModel):
    """Case-specific guidance"""
    key_evidence_types: List[str]
    specific_instructions: List[str]
    relevant_laws: List[str]


class EvidenceGuideResponse(BaseModel):
    """Complete evidence guide response"""
    case_type: str
    language: str
    title: str
    description: str
    tampering_warning: TamperingWarningResponse
    case_specific_guidance: CaseSpecificGuidanceResponse
    step_by_step_instructions: List[StepResponse]
    digital_preservation: DigitalPreservationResponse
    digital_communication_procedures: DigitalCommunicationResponse
    admissibility_requirements: AdmissibilityRequirementsResponse
    evidence_checklists: List[ChecklistResponse]
    visual_aids_available: List[str]
    total_steps: int
    total_checklists: int



@router.get("/guide", response_model=EvidenceGuideResponse)
async def get_evidence_guide(
    case_type: Optional[str] = Query(
        None,
        description="Type of legal case (defamation, harassment, extortion, assault, fraud, cybercrime, false_accusation, general)"
    ),
    case_description: Optional[str] = Query(
        None,
        description="Description of the case for automatic case type detection"
    ),
    language: str = Query(
        "en",
        description="Language code for the guide (en, hi, ta, te, bn, mr, gu)"
    )
):
    """
    Get evidence documentation guide for a specific case type.
    
    This endpoint provides comprehensive evidence collection guidance including:
    - Case-specific instructions
    - Step-by-step procedures with visual aids
    - Digital preservation guidelines
    - Evidence admissibility requirements
    - Tampering warnings
    - Digital communication procedures
    - Evidence type checklists
    
    Query Parameters:
        case_type: Explicit case type (optional if case_description provided)
        case_description: Case description for automatic detection (optional)
        language: Language code for multilingual support
        
    Returns:
        Complete evidence guide with all sections
        
    Requirements:
        - 7.1: Case-specific guidance
        - 7.2: Digital preservation instructions
        - 7.3: Admissibility requirements
        - 7.4: Step-by-step format with visuals
        - 7.5: Evidence type checklists
        - 7.6: Tampering warnings
        - 7.7: Digital communication procedures
    """
    try:
        # Validate case type if provided
        if case_type:
            try:
                CaseType(case_type.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid case type: {case_type}. Valid types: {', '.join([ct.value for ct in CaseType])}"
                )
        
        # Get generator and generate guide
        generator = get_evidence_guide_generator()
        guide = generator.generate_complete_guide(
            case_type=case_type,
            case_description=case_description,
            language=language
        )
        
        # Convert to response model
        return EvidenceGuideResponse(**guide)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating evidence guide: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating the evidence guide. Please try again."
        )


@router.get("/case-types", response_model=List[str])
async def get_case_types():
    """
    Get list of all supported case types.
    
    Returns:
        List of case type strings
    """
    from evidence_guide_content import EvidenceGuideContent
    return EvidenceGuideContent.get_all_case_types()
