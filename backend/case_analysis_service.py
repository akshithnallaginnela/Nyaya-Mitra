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
        recommendations = self._generate_recommendations(breakdown, weaknesses, missing_elements)
        
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
        Identify case weaknesses with student-friendly actionable guidance.
        
        Args:
            breakdown: Score breakdown
            complaint: Complaint details
            
        Returns:
            List of weakness descriptions with HOW-TO fix guidance
        """
        weaknesses = []
        
        if breakdown.evidence_strength < 15:
            weaknesses.append(
                "📉 Weak Evidence — Your evidence is not strong enough yet. "
                "HOW TO FIX: Collect physical proof like screenshots, photos, CCTV footage, emails, or written documents. "
                "Even WhatsApp chats or SMS messages count as evidence. Save everything digitally AND as printouts."
            )
        
        if len(complaint.witness_statements) == 0:
            weaknesses.append(
                "👤 No Witness Statements — You haven't mentioned any witnesses. "
                "HOW TO FIX: Think of anyone who saw or heard what happened — classmates, friends, roommates, "
                "shopkeepers nearby, or college staff. Ask them to write down what they saw with their name, date, "
                "and signature. Even a simple handwritten note counts as a statement."
            )
        
        if breakdown.legal_basis < 15:
            weaknesses.append(
                "⚖️ Unclear Legal Basis — Your case doesn't reference specific laws. "
                "HOW TO FIX: Use the Legal Chat feature of Nyaya Mitra to ask 'Which IPC/BNS sections apply to [your situation]?' "
                "Common sections students need: Section 354 (assault on woman), Section 506 (criminal intimidation), "
                "Section 420 (cheating), Section 499 (defamation), Article 21 (right to life & personal liberty). "
                "Adding the right legal sections greatly strengthens your case."
            )
        
        if breakdown.procedural_compliance < 10:
            weaknesses.append(
                "📝 Missing Legal Procedures — Key steps haven't been taken yet. "
                "HOW TO FIX: Depending on your situation, consider these steps: "
                "(1) File a written complaint with your college/university grievance cell, "
                "(2) File an FIR at the nearest police station (they CANNOT refuse — cite Section 154 CrPC), "
                "(3) Send a legal notice via registered post to the other party, "
                "(4) File a complaint on the National/State Human Rights Commission website if applicable. "
                "Keep acknowledgment receipts of every complaint you file."
            )
        
        if breakdown.timeline_reasonableness < 5:
            weaknesses.append(
                "🕐 Incomplete Timeline — Your timeline of events is missing or unclear. "
                "HOW TO FIX: Write down EVERY event with exact dates and times, starting from the first incident. "
                "Example format: '15-Jan-2026, 3:30 PM — Incident happened in college canteen.' "
                "Include when you reported it, to whom, and what response you got. A clear timeline shows "
                "you acted promptly and helps establish credibility."
            )
        
        return weaknesses
    
    def _identify_missing_elements(self, complaint: ComplaintDetails) -> List[str]:
        """
        Identify missing elements with student-friendly guidance on how to obtain them.
        
        Args:
            complaint: Complaint details
            
        Returns:
            List of missing element descriptions with actionable steps
        """
        missing = []
        
        if len(complaint.evidence) == 0:
            missing.append(
                "📷 Documentary Evidence — You need proof! Collect: screenshots of messages/emails, "
                "photographs of damage or incidents, CCTV footage (request from college security office in writing), "
                "any written documents, agreements, or letters related to the issue."
            )
        
        if len(complaint.witness_statements) == 0:
            missing.append(
                "🗣️ Witness Statements — Ask anyone who saw/heard what happened to write: "
                "'I, [Name], witnessed [what happened] on [date] at [place]. Signed: [Name], Date: [Date].' "
                "This can be handwritten on plain paper. Get at least 2 witnesses if possible."
            )
        
        if len(complaint.procedures_followed) == 0:
            missing.append(
                "📋 Formal Complaints Filed — You should file at least one formal complaint. Options: "
                "(1) College Internal Complaints Committee (ICC) for harassment, "
                "(2) University Grievance Redressal Cell for academic issues, "
                "(3) Police FIR for criminal matters, "
                "(4) District Consumer Forum for service/payment disputes. "
                "Always get a written acknowledgment with date and reference number."
            )
        
        if len(complaint.timeline) == 0:
            missing.append(
                "📅 Dated Timeline — Create a chronological list: Date → What happened → Where → Who was involved → "
                "What action you took. Start from the very first incident. This is crucial for any legal proceeding."
            )
        
        if len(complaint.documentation) == 0:
            missing.append(
                "📄 Supporting Documents — Gather: ID proof, college ID, fee receipts, "
                "rent agreements (for housing disputes), medical reports (if injured — visit a government hospital "
                "for a medico-legal case report), bank statements showing transactions, or any contracts/agreements."
            )
        
        # Check for specific legal references
        if "ipc" not in complaint.allegations.lower() and "section" not in complaint.allegations.lower() and "bns" not in complaint.allegations.lower():
            missing.append(
                "⚖️ Legal Section References — Your case needs applicable law references. "
                "Use Nyaya Mitra's Chat feature and ask: 'What legal sections apply to [describe your situation]?' "
                "Then add those sections (e.g., IPC Section 420, BNS Section 318) to your allegations."
            )
        
        return missing
    
    def _generate_recommendations(
        self,
        breakdown: ScoreBreakdown,
        weaknesses: List[str],
        missing_elements: List[str]
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
                "🔍 Strengthen Your Evidence — Collect at least 3-4 pieces of proof: "
                "screenshots (with timestamps visible), photographs, written communications, "
                "official documents, or receipts. Store both digital and physical copies."
            )
            recommendations.append(
                "👥 Get Witness Support — Identify 2-3 people who can back your account. "
                "Ask them to write a signed statement with their contact details. "
                "Even shopkeepers, security guards, or auto drivers near the incident location can be witnesses."
            )
        
        # Legal basis recommendations
        if breakdown.legal_basis < 15:
            recommendations.append(
                "📚 Find Applicable Laws — Use Nyaya Mitra's Legal Chat to ask about laws that apply to your case. "
                "For example, ask: 'What IPC sections apply to [your situation]?' "
                "Then mention those specific sections in your allegations."
            )
            recommendations.append(
                "✍️ Write Detailed Allegations — Describe exactly WHAT happened, WHEN, WHERE, "
                "WHO was involved, and WHAT impact it had on you. The more specific you are, the stronger your case."
            )
        
        # Procedural recommendations
        if breakdown.procedural_compliance < 10:
            recommendations.append(
                "🏛️ File Formal Complaints — Visit these in order: "
                "(1) College grievance cell or ICC, "
                "(2) Local police station for FIR (they cannot refuse — if they do, go to the SP office or file online at your state's citizen portal), "
                "(3) Send a legal notice via registered post. "
                "Keep a copy of every complaint and its acknowledgment receipt."
            )
        
        # Timeline recommendations
        if breakdown.timeline_reasonableness < 5:
            recommendations.append(
                "📅 Build a Clear Timeline — Open a notebook or document and list every event: "
                "'Date | Time | What happened | Where | Who was present.' "
                "Start from the very first incident. This helps lawyers and judges understand your case quickly."
            )
        
        # General recommendations based on score
        total_score = (
            breakdown.evidence_strength +
            breakdown.legal_basis +
            breakdown.procedural_compliance +
            breakdown.timeline_reasonableness
        )
        
        if total_score > self.STRONG_CASE_THRESHOLD:
            recommendations.append(
                "✅ Your case looks strong! Next steps: "
                "(1) Consult a lawyer — use Nyaya Mitra's Legal Aid Search to find free legal aid near you, "
                "(2) File your case formally, "
                "(3) Keep all original documents safe."
            )
        elif total_score >= self.WEAK_CASE_THRESHOLD:
            recommendations.append(
                "📈 Your case has potential but needs more work. "
                "Focus on the weaknesses listed above. Use Nyaya Mitra's other features: "
                "Legal Chat for law references, Document Generator for notices, and Legal Aid Search for free lawyers."
            )
        else:
            recommendations.append(
                "💪 Don't be discouraged by a low score — it means you need to gather more information first. "
                "Focus on collecting evidence and filing formal complaints. "
                "Use Nyaya Mitra's Legal Chat to understand your rights, and Legal Aid Search to find free legal help near your location."
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
