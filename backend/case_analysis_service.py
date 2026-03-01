"""
Case validity analysis service for evaluating legal complaints.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field


class ComplaintDetails(BaseModel):
    """Model for complaint details input."""
    evidence: List[str] = Field(..., description="List of evidence items")
    allegations: str = Field(..., description="Description of allegations")
    procedures_followed: List[str] = Field(default=[], description="Legal procedures followed")
    timeline: Dict[str, str] = Field(default={}, description="Timeline of events")
    witness_statements: List[str] = Field(default=[], description="Witness statements")
    documentation: List[str] = Field(default=[], description="Supporting documentation")


class ScoreBreakdown(BaseModel):
    """Model for score breakdown."""
    evidence_strength: float = Field(..., ge=0, le=40, description="Evidence strength score (0-40)")
    legal_basis: float = Field(..., ge=0, le=30, description="Legal basis score (0-30)")
    procedural_compliance: float = Field(..., ge=0, le=20, description="Procedural compliance score (0-20)")
    timeline_reasonableness: float = Field(..., ge=0, le=10, description="Timeline reasonableness score (0-10)")


class CaseAnalysisResult(BaseModel):
    """Model for case analysis result."""
    validity_score: float = Field(..., ge=0, le=100, description="Overall validity score (0-100)")
    score_breakdown: ScoreBreakdown
    strengths: List[str] = Field(default=[], description="Case strengths")
    weaknesses: List[str] = Field(default=[], description="Case weaknesses")
    missing_elements: List[str] = Field(default=[], description="Missing elements")
    recommendations: List[str] = Field(default=[], description="Recommendations for improvement")
    requires_legal_consultation: bool = Field(default=False, description="Whether legal consultation is recommended")


class CaseAnalysisService:
    """Service for analyzing case validity and strength."""
    
    # Scoring thresholds
    WEAK_CASE_THRESHOLD = 40
    STRONG_CASE_THRESHOLD = 70
    
    # Evidence quality keywords
    STRONG_EVIDENCE_KEYWORDS = [
        "document", "written", "signed", "recorded", "photograph", "video",
        "audio", "email", "message", "contract", "agreement", "receipt",
        "witness", "testimony", "statement", "affidavit"
    ]
    
    WEAK_EVIDENCE_KEYWORDS = [
        "verbal", "hearsay", "rumor", "assumption", "belief", "think",
        "maybe", "possibly", "allegedly"
    ]
    
    # Legal procedure keywords
    PROCEDURE_KEYWORDS = [
        "fir", "complaint", "police", "station", "report", "notice",
        "legal notice", "court", "petition", "application", "summons"
    ]
    
    def __init__(self):
        """Initialize case analysis service."""
        pass
    
    def analyze_case(self, complaint: ComplaintDetails) -> CaseAnalysisResult:
        """
        Analyze a case and generate validity score.
        
        Args:
            complaint: Complaint details
            
        Returns:
            CaseAnalysisResult with score and recommendations
        """
        # Calculate individual scores
        evidence_score = self._analyze_evidence_strength(complaint)
        legal_basis_score = self._analyze_legal_basis(complaint)
        procedural_score = self._analyze_procedural_compliance(complaint)
        timeline_score = self._analyze_timeline_reasonableness(complaint)
        
        # Create score breakdown
        breakdown = ScoreBreakdown(
            evidence_strength=evidence_score,
            legal_basis=legal_basis_score,
            procedural_compliance=procedural_score,
            timeline_reasonableness=timeline_score
        )
        
        # Calculate total score
        total_score = (
            evidence_score +
            legal_basis_score +
            procedural_score +
            timeline_score
        )
        
        # Identify strengths and weaknesses
        strengths = self._identify_strengths(breakdown, complaint)
        weaknesses = self._identify_weaknesses(breakdown, complaint)
        missing_elements = self._identify_missing_elements(complaint)
        recommendations = self._generate_recommendations(breakdown, weaknesses, missing_elements, total_score)
        
        # Determine if legal consultation is needed
        requires_consultation = total_score > self.STRONG_CASE_THRESHOLD
        
        return CaseAnalysisResult(
            validity_score=total_score,
            score_breakdown=breakdown,
            strengths=strengths,
            weaknesses=weaknesses,
            missing_elements=missing_elements,
            recommendations=recommendations,
            requires_legal_consultation=requires_consultation
        )
    
    def _analyze_evidence_strength(self, complaint: ComplaintDetails) -> float:
        """
        Analyze evidence strength (0-40 points).
        
        Criteria:
        - Number of evidence items (0-15 points)
        - Quality of evidence (0-15 points)
        - Witness statements (0-10 points)
        
        Args:
            complaint: Complaint details
            
        Returns:
            Evidence strength score (0-40)
        """
        score = 0.0
        
        # Number of evidence items (0-15 points)
        evidence_count = len(complaint.evidence)
        if evidence_count == 0:
            score += 0
        elif evidence_count == 1:
            score += 5
        elif evidence_count == 2:
            score += 10
        else:  # 3 or more
            score += 15
        
        # Quality of evidence (0-15 points)
        evidence_text = " ".join(complaint.evidence).lower()
        
        strong_count = sum(1 for keyword in self.STRONG_EVIDENCE_KEYWORDS if keyword in evidence_text)
        weak_count = sum(1 for keyword in self.WEAK_EVIDENCE_KEYWORDS if keyword in evidence_text)
        
        if strong_count > 0:
            quality_score = min(15, strong_count * 3)
            score += quality_score
        
        if weak_count > 0:
            penalty = min(5, weak_count * 2)
            score = max(0, score - penalty)
        
        # Witness statements (0-10 points)
        witness_count = len(complaint.witness_statements)
        if witness_count == 0:
            score += 0
        elif witness_count == 1:
            score += 5
        else:  # 2 or more
            score += 10
        
        return min(40.0, score)
    
    def _analyze_legal_basis(self, complaint: ComplaintDetails) -> float:
        """
        Analyze legal basis (0-30 points).
        
        Criteria:
        - Clarity of allegations (0-15 points)
        - Legal references (0-10 points)
        - Documentation (0-5 points)
        
        Args:
            complaint: Complaint details
            
        Returns:
            Legal basis score (0-30)
        """
        score = 0.0
        
        # Clarity of allegations (0-15 points)
        allegations_length = len(complaint.allegations)
        if allegations_length < 50:
            score += 3  # Too brief
        elif allegations_length < 200:
            score += 10  # Good detail
        else:
            score += 15  # Comprehensive
        
        # Check for specific legal terms
        allegations_lower = complaint.allegations.lower()
        legal_terms = ["ipc", "section", "crpc", "law", "act", "offense", "crime", "violation"]
        legal_term_count = sum(1 for term in legal_terms if term in allegations_lower)
        
        if legal_term_count > 0:
            score += min(10, legal_term_count * 2)
        
        # Documentation (0-5 points)
        doc_count = len(complaint.documentation)
        if doc_count > 0:
            score += min(5, doc_count * 2)
        
        return min(30.0, score)
    
    def _analyze_procedural_compliance(self, complaint: ComplaintDetails) -> float:
        """
        Analyze procedural compliance (0-20 points).
        
        Criteria:
        - Procedures followed (0-20 points)
        
        Args:
            complaint: Complaint details
            
        Returns:
            Procedural compliance score (0-20)
        """
        score = 0.0
        
        procedure_count = len(complaint.procedures_followed)
        
        if procedure_count == 0:
            score = 0
        elif procedure_count == 1:
            score = 8
        elif procedure_count == 2:
            score = 15
        else:  # 3 or more
            score = 20
        
        # Check for important procedures
        procedures_text = " ".join(complaint.procedures_followed).lower()
        important_procedures = ["fir", "complaint", "police", "notice", "court"]
        
        important_count = sum(1 for proc in important_procedures if proc in procedures_text)
        if important_count > 0:
            bonus = min(5, important_count * 2)
            score = min(20, score + bonus)
        
        return min(20.0, score)
    
    def _analyze_timeline_reasonableness(self, complaint: ComplaintDetails) -> float:
        """
        Analyze timeline reasonableness (0-10 points).
        
        Criteria:
        - Timeline completeness (0-5 points)
        - Timeline consistency (0-5 points)
        
        Args:
            complaint: Complaint details
            
        Returns:
            Timeline reasonableness score (0-10)
        """
        score = 0.0
        
        timeline_entries = len(complaint.timeline)
        
        # Timeline completeness (0-5 points)
        if timeline_entries == 0:
            score += 0
        elif timeline_entries == 1:
            score += 2
        elif timeline_entries == 2:
            score += 4
        else:  # 3 or more
            score += 5
        
        # Timeline consistency (0-5 points)
        # Check if timeline has key events
        if timeline_entries > 0:
            timeline_text = " ".join(complaint.timeline.values()).lower()
            key_events = ["incident", "complaint", "report", "notice", "response"]
            event_count = sum(1 for event in key_events if event in timeline_text)
            
            if event_count > 0:
                score += min(5, event_count * 2)
        
        return min(10.0, score)
    
    def _identify_strengths(
        self,
        breakdown: ScoreBreakdown,
        complaint: ComplaintDetails
    ) -> List[str]:
        """
        Identify case strengths.
        
        Args:
            breakdown: Score breakdown
            complaint: Complaint details
            
        Returns:
            List of strength descriptions
        """
        strengths = []
        
        if breakdown.evidence_strength >= 30:
            strengths.append("Strong documentary evidence supporting the case")
        
        if len(complaint.witness_statements) >= 2:
            strengths.append("Multiple witness statements corroborating the allegations")
        
        if breakdown.legal_basis >= 20:
            strengths.append("Clear legal basis with specific references to applicable laws")
        
        if breakdown.procedural_compliance >= 15:
            strengths.append("Proper legal procedures have been followed")
        
        if breakdown.timeline_reasonableness >= 7:
            strengths.append("Well-documented timeline of events")
        
        return strengths
    
    def _identify_weaknesses(
        self,
        breakdown: ScoreBreakdown,
        complaint: ComplaintDetails
    ) -> List[str]:
        """
        Identify case weaknesses.
        
        Args:
            breakdown: Score breakdown
            complaint: Complaint details
            
        Returns:
            List of weakness descriptions
        """
        weaknesses = []
        
        if breakdown.evidence_strength < 15:
            weaknesses.append("Insufficient or weak evidence to support allegations")
        
        if len(complaint.witness_statements) == 0:
            weaknesses.append("No witness statements to corroborate the case")
        
        if breakdown.legal_basis < 15:
            weaknesses.append("Unclear legal basis or lack of specific legal references")
        
        if breakdown.procedural_compliance < 10:
            weaknesses.append("Important legal procedures may not have been followed")
        
        if breakdown.timeline_reasonableness < 5:
            weaknesses.append("Incomplete or unclear timeline of events")
        
        return weaknesses
    
    def _identify_missing_elements(self, complaint: ComplaintDetails) -> List[str]:
        """
        Identify missing elements in the complaint.
        
        Args:
            complaint: Complaint details
            
        Returns:
            List of missing element descriptions
        """
        missing = []
        
        if len(complaint.evidence) == 0:
            missing.append("Documentary evidence (photos, videos, documents, messages)")
        
        if len(complaint.witness_statements) == 0:
            missing.append("Witness statements or testimonies")
        
        if len(complaint.procedures_followed) == 0:
            missing.append("Documentation of legal procedures followed (FIR, complaints, notices)")
        
        if len(complaint.timeline) == 0:
            missing.append("Detailed timeline of events with dates")
        
        if len(complaint.documentation) == 0:
            missing.append("Supporting documentation (medical reports, receipts, contracts)")
        
        # Check for specific legal references
        if "ipc" not in complaint.allegations.lower() and "section" not in complaint.allegations.lower():
            missing.append("Specific legal sections or laws that apply to the case")
        
        return missing
    
    def _generate_recommendations(
        self,
        breakdown: ScoreBreakdown,
        weaknesses: List[str],
        missing_elements: List[str],
        total_score: float
    ) -> List[str]:
        """
        Generate recommendations for improving the case.
        
        Args:
            breakdown: Score breakdown
            weaknesses: List of weaknesses
            missing_elements: List of missing elements
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Evidence-related recommendations
        if breakdown.evidence_strength < 20:
            recommendations.append(
                "Gather more documentary evidence such as photographs, videos, written communications, or official documents"
            )
            recommendations.append(
                "Obtain witness statements from people who can corroborate your account"
            )
        
        # Legal basis recommendations
        if breakdown.legal_basis < 15:
            recommendations.append(
                "Identify specific IPC or CrPC sections that apply to your case"
            )
            recommendations.append(
                "Clearly document all allegations with specific details and dates"
            )
        
        # Procedural recommendations
        if breakdown.procedural_compliance < 10:
            recommendations.append(
                "File an FIR or formal complaint with the police if you haven't already"
            )
            recommendations.append(
                "Send legal notices to relevant parties through registered post"
            )
        
        # Timeline recommendations
        if breakdown.timeline_reasonableness < 5:
            recommendations.append(
                "Create a detailed timeline of all events with specific dates and times"
            )
        
        # General recommendations
        if missing_elements:
            recommendations.append(
                f"Address the following missing elements: {', '.join(missing_elements[:3])}"
            )
        
        # Always recommend legal consultation for serious cases
        if total_score > self.STRONG_CASE_THRESHOLD:
            recommendations.append(
                "⚠️ Your case appears to have merit. Strongly recommend consulting with a qualified lawyer immediately"
            )
        elif total_score < self.WEAK_CASE_THRESHOLD:
            recommendations.append(
                "Consider strengthening your case before proceeding. Consult with a legal aid provider for guidance"
            )
        
        return recommendations


# Singleton instance
_case_analysis_service: Optional[CaseAnalysisService] = None


def get_case_analysis_service() -> CaseAnalysisService:
    """
    Get or create singleton case analysis service instance.
    
    Returns:
        CaseAnalysisService instance
    """
    global _case_analysis_service
    if _case_analysis_service is None:
        _case_analysis_service = CaseAnalysisService()
    return _case_analysis_service
