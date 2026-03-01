"""
Case analysis API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.user import User
from models.case_analysis import CaseAnalysis
from utils.jwt import get_current_user
from case_analysis_service import (
    get_case_analysis_service,
    ComplaintDetails,
    CaseAnalysisResult
)


router = APIRouter(prefix="/api/case", tags=["case"])


# Request/Response models
class CaseAnalyzeRequest(BaseModel):
    """Request model for case analysis."""
    evidence: List[str]
    allegations: str
    procedures_followed: List[str] = []
    timeline: dict = {}
    witness_statements: List[str] = []
    documentation: List[str] = []


class ScoreBreakdownResponse(BaseModel):
    """Score breakdown response model."""
    evidence_strength: float
    legal_basis: float
    procedural_compliance: float
    timeline_reasonableness: float


class CaseAnalyzeResponse(BaseModel):
    """Response model for case analysis."""
    analysis_id: int
    validity_score: float
    score_breakdown: ScoreBreakdownResponse
    strengths: List[str]
    weaknesses: List[str]
    missing_elements: List[str]
    recommendations: List[str]
    requires_legal_consultation: bool
    created_at: datetime


class CaseHistoryItem(BaseModel):
    """Case history item model."""
    id: int
    validity_score: float
    created_at: datetime
    complaint_summary: str


class CaseHistoryResponse(BaseModel):
    """Case history response model."""
    analyses: List[CaseHistoryItem]
    total: int
    page: int
    page_size: int


@router.post("/analyze", response_model=CaseAnalyzeResponse)
async def analyze_case(
    request: CaseAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze a case and generate validity score.
    
    This endpoint:
    1. Accepts complaint details
    2. Runs validity scoring algorithm
    3. Generates detailed breakdown and recommendations
    4. Adds legal consultation recommendation for high scores (>70)
    5. Saves analysis to database
    6. Returns complete analysis results
    
    Args:
        request: Case analysis request with complaint details
        current_user: Authenticated user
        db: Database session
        
    Returns:
        CaseAnalyzeResponse with validity score and recommendations
        
    Raises:
        HTTPException: If analysis fails
    """
    try:
        # Create complaint details
        complaint = ComplaintDetails(
            evidence=request.evidence,
            allegations=request.allegations,
            procedures_followed=request.procedures_followed,
            timeline=request.timeline,
            witness_statements=request.witness_statements,
            documentation=request.documentation
        )
        
        # Analyze case
        service = get_case_analysis_service()
        result = service.analyze_case(complaint)
        
        # Save to database
        case_analysis = CaseAnalysis(
            user_id=current_user.id,
            complaint_details={
                "evidence": request.evidence,
                "allegations": request.allegations,
                "procedures_followed": request.procedures_followed,
                "timeline": request.timeline,
                "witness_statements": request.witness_statements,
                "documentation": request.documentation
            },
            validity_score=result.validity_score,
            score_breakdown={
                "evidence_strength": result.score_breakdown.evidence_strength,
                "legal_basis": result.score_breakdown.legal_basis,
                "procedural_compliance": result.score_breakdown.procedural_compliance,
                "timeline_reasonableness": result.score_breakdown.timeline_reasonableness
            },
            strengths=result.strengths,
            weaknesses=result.weaknesses,
            missing_elements=result.missing_elements,
            recommendations=result.recommendations
        )
        
        db.add(case_analysis)
        db.commit()
        db.refresh(case_analysis)
        
        return CaseAnalyzeResponse(
            analysis_id=case_analysis.id,
            validity_score=result.validity_score,
            score_breakdown=ScoreBreakdownResponse(
                evidence_strength=result.score_breakdown.evidence_strength,
                legal_basis=result.score_breakdown.legal_basis,
                procedural_compliance=result.score_breakdown.procedural_compliance,
                timeline_reasonableness=result.score_breakdown.timeline_reasonableness
            ),
            strengths=result.strengths,
            weaknesses=result.weaknesses,
            missing_elements=result.missing_elements,
            recommendations=result.recommendations,
            requires_legal_consultation=result.requires_legal_consultation,
            created_at=case_analysis.created_at
        )
        
    except Exception as e:
        print(f"Error analyzing case: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while analyzing the case. Please try again."
        )


@router.get("/history", response_model=CaseHistoryResponse)
async def get_case_history(
    page: int = 1,
    page_size: int = 20,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's case analysis history.
    
    Args:
        page: Page number (default: 1)
        page_size: Number of analyses per page (default: 20)
        min_score: Minimum validity score filter (optional)
        max_score: Maximum validity score filter (optional)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        CaseHistoryResponse with paginated case analyses
    """
    try:
        # Build query
        query = db.query(CaseAnalysis).filter(
            CaseAnalysis.user_id == current_user.id
        )
        
        # Apply score filters
        if min_score is not None:
            query = query.filter(CaseAnalysis.validity_score >= min_score)
        if max_score is not None:
            query = query.filter(CaseAnalysis.validity_score <= max_score)
        
        # Get total count
        total = query.count()
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get analyses with pagination
        analyses = query.order_by(
            CaseAnalysis.created_at.desc()
        ).offset(offset).limit(page_size).all()
        
        # Build response
        history_items = []
        for analysis in analyses:
            # Create summary from allegations
            allegations = analysis.complaint_details.get("allegations", "")
            summary = allegations[:100] + "..." if len(allegations) > 100 else allegations
            
            history_items.append(CaseHistoryItem(
                id=analysis.id,
                validity_score=analysis.validity_score,
                created_at=analysis.created_at,
                complaint_summary=summary
            ))
        
        return CaseHistoryResponse(
            analyses=history_items,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        print(f"Error retrieving case history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving case history."
        )


@router.get("/history/{analysis_id}", response_model=CaseAnalyzeResponse)
async def get_case_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed case analysis by ID.
    
    Args:
        analysis_id: ID of the case analysis
        current_user: Authenticated user
        db: Database session
        
    Returns:
        CaseAnalyzeResponse with full analysis details
        
    Raises:
        HTTPException: If analysis not found or unauthorized
    """
    try:
        # Get analysis
        analysis = db.query(CaseAnalysis).filter(
            CaseAnalysis.id == analysis_id,
            CaseAnalysis.user_id == current_user.id
        ).first()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case analysis not found"
            )
        
        # Determine if legal consultation is required
        requires_consultation = analysis.validity_score > 70
        
        return CaseAnalyzeResponse(
            analysis_id=analysis.id,
            validity_score=analysis.validity_score,
            score_breakdown=ScoreBreakdownResponse(
                evidence_strength=analysis.score_breakdown.get("evidence_strength", 0),
                legal_basis=analysis.score_breakdown.get("legal_basis", 0),
                procedural_compliance=analysis.score_breakdown.get("procedural_compliance", 0),
                timeline_reasonableness=analysis.score_breakdown.get("timeline_reasonableness", 0)
            ),
            strengths=analysis.strengths or [],
            weaknesses=analysis.weaknesses or [],
            missing_elements=analysis.missing_elements or [],
            recommendations=analysis.recommendations or [],
            requires_legal_consultation=requires_consultation,
            created_at=analysis.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving case analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the case analysis."
        )
