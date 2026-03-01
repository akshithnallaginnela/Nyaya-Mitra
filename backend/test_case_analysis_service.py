"""
Tests for case analysis service.
"""
import pytest
from case_analysis_service import (
    CaseAnalysisService,
    ComplaintDetails,
    get_case_analysis_service
)


class TestCaseAnalysisService:
    """Test suite for CaseAnalysisService."""
    
    def test_initialization(self):
        """Test service initialization."""
        service = CaseAnalysisService()
        assert service is not None
        assert service.WEAK_CASE_THRESHOLD == 40
        assert service.STRONG_CASE_THRESHOLD == 70
    
    def test_analyze_case_strong_case(self):
        """Test analyzing a strong case."""
        service = CaseAnalysisService()
        
        complaint = ComplaintDetails(
            evidence=[
                "Written contract signed by both parties",
                "Email correspondence showing agreement",
                "Bank statements showing payment",
                "Photographs of the incident"
            ],
            allegations="The defendant violated IPC Section 420 by committing fraud. They took money under false pretenses and failed to deliver the promised services as per our written agreement dated January 1, 2024.",
            procedures_followed=[
                "Filed FIR at local police station",
                "Sent legal notice through registered post",
                "Filed complaint in consumer court"
            ],
            timeline={
                "2024-01-01": "Signed agreement and made payment",
                "2024-02-01": "Defendant failed to deliver",
                "2024-02-15": "Sent legal notice",
                "2024-03-01": "Filed FIR"
            },
            witness_statements=[
                "Witness A saw the transaction",
                "Witness B can confirm the agreement terms"
            ],
            documentation=[
                "Contract copy",
                "Payment receipt",
                "Legal notice copy"
            ]
        )
        
        result = service.analyze_case(complaint)
        
        assert result.validity_score >= 70
        assert result.requires_legal_consultation is True
        assert len(result.strengths) > 0
        assert result.score_breakdown.evidence_strength > 25
        assert result.score_breakdown.legal_basis >= 15
        assert result.score_breakdown.procedural_compliance > 15
    
    def test_analyze_case_weak_case(self):
        """Test analyzing a weak case."""
        service = CaseAnalysisService()
        
        complaint = ComplaintDetails(
            evidence=["Someone told me about it"],
            allegations="I think something bad happened",
            procedures_followed=[],
            timeline={},
            witness_statements=[],
            documentation=[]
        )
        
        result = service.analyze_case(complaint)
        
        assert result.validity_score < 40
        assert result.requires_legal_consultation is False
        assert len(result.weaknesses) > 0
        assert len(result.missing_elements) > 0
        assert len(result.recommendations) > 0
    
    def test_analyze_case_medium_case(self):
        """Test analyzing a medium strength case."""
        service = CaseAnalysisService()
        
        complaint = ComplaintDetails(
            evidence=[
                "Text messages from the accused",
                "Witness statement"
            ],
            allegations="The accused harassed me repeatedly over the past month, violating my privacy and causing mental distress.",
            procedures_followed=["Filed complaint at police station"],
            timeline={
                "2024-01-15": "First incident occurred",
                "2024-02-01": "Filed complaint"
            },
            witness_statements=["Friend witnessed one incident"],
            documentation=[]
        )
        
        result = service.analyze_case(complaint)
        
        assert 40 <= result.validity_score <= 70
        assert result.requires_legal_consultation is False
    
    def test_evidence_strength_scoring(self):
        """Test evidence strength scoring."""
        service = CaseAnalysisService()
        
        # Strong evidence
        strong_complaint = ComplaintDetails(
            evidence=[
                "Signed document",
                "Video recording",
                "Email correspondence",
                "Witness affidavit"
            ],
            allegations="Test",
            witness_statements=["Witness 1", "Witness 2"]
        )
        
        strong_score = service._analyze_evidence_strength(strong_complaint)
        assert strong_score >= 30
        
        # Weak evidence
        weak_complaint = ComplaintDetails(
            evidence=["Hearsay", "Rumor"],
            allegations="Test",
            witness_statements=[]
        )
        
        weak_score = service._analyze_evidence_strength(weak_complaint)
        assert weak_score < 15
    
    def test_legal_basis_scoring(self):
        """Test legal basis scoring."""
        service = CaseAnalysisService()
        
        # Strong legal basis
        strong_complaint = ComplaintDetails(
            evidence=[],
            allegations="The defendant violated IPC Section 420 by committing fraud. The act constitutes a criminal offense under Indian law. Multiple sections of the IPC apply to this case including provisions for cheating and dishonesty.",
            documentation=["Legal notice", "Contract", "Receipt"]
        )
        
        strong_score = service._analyze_legal_basis(strong_complaint)
        assert strong_score >= 20
        
        # Weak legal basis
        weak_complaint = ComplaintDetails(
            evidence=[],
            allegations="Bad thing happened",
            documentation=[]
        )
        
        weak_score = service._analyze_legal_basis(weak_complaint)
        assert weak_score < 10
    
    def test_procedural_compliance_scoring(self):
        """Test procedural compliance scoring."""
        service = CaseAnalysisService()
        
        # Good compliance
        good_complaint = ComplaintDetails(
            evidence=[],
            allegations="Test",
            procedures_followed=[
                "Filed FIR at police station",
                "Sent legal notice",
                "Filed court petition"
            ]
        )
        
        good_score = service._analyze_procedural_compliance(good_complaint)
        assert good_score >= 15
        
        # No compliance
        no_complaint = ComplaintDetails(
            evidence=[],
            allegations="Test",
            procedures_followed=[]
        )
        
        no_score = service._analyze_procedural_compliance(no_complaint)
        assert no_score == 0
    
    def test_timeline_reasonableness_scoring(self):
        """Test timeline reasonableness scoring."""
        service = CaseAnalysisService()
        
        # Good timeline
        good_complaint = ComplaintDetails(
            evidence=[],
            allegations="Test",
            timeline={
                "2024-01-01": "Incident occurred",
                "2024-01-05": "Filed complaint",
                "2024-01-10": "Received response",
                "2024-01-15": "Sent notice"
            }
        )
        
        good_score = service._analyze_timeline_reasonableness(good_complaint)
        assert good_score >= 7
        
        # No timeline
        no_complaint = ComplaintDetails(
            evidence=[],
            allegations="Test",
            timeline={}
        )
        
        no_score = service._analyze_timeline_reasonableness(no_complaint)
        assert no_score == 0
    
    def test_identify_strengths(self):
        """Test strength identification."""
        service = CaseAnalysisService()
        
        from case_analysis_service import ScoreBreakdown
        
        strong_breakdown = ScoreBreakdown(
            evidence_strength=35,
            legal_basis=25,
            procedural_compliance=18,
            timeline_reasonableness=8
        )
        
        complaint = ComplaintDetails(
            evidence=["Doc1", "Doc2"],
            allegations="Test",
            witness_statements=["W1", "W2"]
        )
        
        strengths = service._identify_strengths(strong_breakdown, complaint)
        
        assert len(strengths) > 0
        assert any("evidence" in s.lower() for s in strengths)
    
    def test_identify_weaknesses(self):
        """Test weakness identification."""
        service = CaseAnalysisService()
        
        from case_analysis_service import ScoreBreakdown
        
        weak_breakdown = ScoreBreakdown(
            evidence_strength=10,
            legal_basis=8,
            procedural_compliance=5,
            timeline_reasonableness=3
        )
        
        complaint = ComplaintDetails(
            evidence=["Weak evidence"],
            allegations="Test",
            witness_statements=[]
        )
        
        weaknesses = service._identify_weaknesses(weak_breakdown, complaint)
        
        assert len(weaknesses) > 0
        assert any("evidence" in w.lower() or "witness" in w.lower() for w in weaknesses)
    
    def test_identify_missing_elements(self):
        """Test missing element identification."""
        service = CaseAnalysisService()
        
        incomplete_complaint = ComplaintDetails(
            evidence=[],
            allegations="Something happened",
            procedures_followed=[],
            timeline={},
            witness_statements=[],
            documentation=[]
        )
        
        missing = service._identify_missing_elements(incomplete_complaint)
        
        assert len(missing) > 0
        assert any("evidence" in m.lower() for m in missing)
        assert any("witness" in m.lower() for m in missing)
        assert any("timeline" in m.lower() for m in missing)
    
    def test_generate_recommendations(self):
        """Test recommendation generation."""
        service = CaseAnalysisService()
        
        from case_analysis_service import ScoreBreakdown
        
        weak_breakdown = ScoreBreakdown(
            evidence_strength=10,
            legal_basis=8,
            procedural_compliance=5,
            timeline_reasonableness=3
        )
        
        weaknesses = ["Weak evidence", "No procedures"]
        missing = ["Timeline", "Witnesses"]
        total_score = (
            weak_breakdown.evidence_strength + weak_breakdown.legal_basis +
            weak_breakdown.procedural_compliance + weak_breakdown.timeline_reasonableness
        )
        
        recommendations = service._generate_recommendations(
            weak_breakdown,
            weaknesses,
            missing,
            total_score
        )
        
        assert len(recommendations) > 0
        assert any("evidence" in r.lower() for r in recommendations)
    
    def test_score_bounds(self):
        """Test that scores are within valid bounds."""
        service = CaseAnalysisService()
        
        # Maximum case
        max_complaint = ComplaintDetails(
            evidence=["Doc1", "Doc2", "Doc3", "Doc4", "Doc5"],
            allegations="Very detailed allegations with IPC Section 420 and CrPC references. This is a comprehensive description of the offense committed under Indian law with multiple legal sections applicable.",
            procedures_followed=["FIR", "Notice", "Court", "Police"],
            timeline={f"2024-01-{i:02d}": f"Event {i}" for i in range(1, 11)},
            witness_statements=["W1", "W2", "W3"],
            documentation=["D1", "D2", "D3"]
        )
        
        result = service.analyze_case(max_complaint)
        
        assert 0 <= result.validity_score <= 100
        assert 0 <= result.score_breakdown.evidence_strength <= 40
        assert 0 <= result.score_breakdown.legal_basis <= 30
        assert 0 <= result.score_breakdown.procedural_compliance <= 20
        assert 0 <= result.score_breakdown.timeline_reasonableness <= 10
    
    def test_requires_legal_consultation_threshold(self):
        """Test legal consultation recommendation threshold."""
        service = CaseAnalysisService()
        
        # Score above 70
        strong_complaint = ComplaintDetails(
            evidence=["Doc1", "Doc2", "Doc3"],
            allegations="Detailed allegations with IPC Section 420 and other legal references. Comprehensive description of fraud and cheating under Indian law.",
            procedures_followed=["FIR", "Notice", "Court"],
            timeline={"2024-01-01": "Event 1", "2024-01-15": "Event 2", "2024-02-01": "Event 3"},
            witness_statements=["W1", "W2"],
            documentation=["D1", "D2"]
        )
        
        result = service.analyze_case(strong_complaint)
        
        if result.validity_score > 70:
            assert result.requires_legal_consultation is True


def test_get_case_analysis_service_singleton():
    """Test get_case_analysis_service returns singleton instance."""
    service1 = get_case_analysis_service()
    service2 = get_case_analysis_service()
    
    assert service1 is service2


def test_get_case_analysis_service_creates_instance():
    """Test get_case_analysis_service creates CaseAnalysisService instance."""
    # Reset singleton
    import case_analysis_service
    case_analysis_service._case_analysis_service = None
    
    service = get_case_analysis_service()
    assert isinstance(service, CaseAnalysisService)
