"""
Case Analysis model for case validity assessment.

This module implements the CaseAnalysis model to store complaint details,
validity scores, score breakdowns, weaknesses, and recommendations for
legal case analysis.

Requirements: 2.1 (Case validity assessment)
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship, validates

from database import BaseModel

if TYPE_CHECKING:
    from models.user import User


class CaseAnalysis(BaseModel):
    """
    Case Analysis model for storing case validity assessments.
    
    Inherits from BaseModel which provides:
    - id: UUID primary key
    - created_at: Timestamp of analysis creation
    - updated_at: Timestamp of last update
    
    Additional fields:
    - user_id: Foreign key to User model
    - complaint_details: JSON object containing complaint information
    - validity_score: Integer score from 0-100 indicating case strength
    - score_breakdown: JSON object with component scores (evidence, legal_basis, procedural, timeline)
    - weaknesses: JSON array of identified weaknesses in the case
    - recommendations: JSON array of recommendations for improvement
    
    Relationships:
    - user: Many-to-one relationship with User
    """
    
    __tablename__ = "case_analyses"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    complaint_details = Column(
        JSON,
        nullable=False
    )
    
    validity_score = Column(
        Integer,
        nullable=False
    )
    
    score_breakdown = Column(
        JSON,
        nullable=False
    )
    
    weaknesses = Column(
        JSON,
        nullable=True
    )
    
    recommendations = Column(
        JSON,
        nullable=True
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="case_analyses"
    )
    
    @validates('validity_score')
    def validate_validity_score(self, key: str, score: int) -> int:
        """
        Validate validity score is within 0-100 range.
        
        As per requirement 2.1, the validity score must be an integer
        between 0 and 100 (inclusive).
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            score: Validity score to validate
            
        Returns:
            int: Validated validity score
            
        Raises:
            ValueError: If score is out of range or not an integer
        """
        if not isinstance(score, int):
            raise ValueError("Validity score must be an integer")
        
        if score < 0 or score > 100:
            raise ValueError("Validity score must be between 0 and 100 (inclusive)")
        
        return score
    
    @validates('complaint_details')
    def validate_complaint_details(self, key: str, details: Dict) -> Dict:
        """
        Validate complaint details structure.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            details: Complaint details dictionary to validate
            
        Returns:
            Dict: Validated complaint details
            
        Raises:
            ValueError: If complaint details are invalid
        """
        if not details:
            raise ValueError("Complaint details cannot be empty")
        
        if not isinstance(details, dict):
            raise ValueError("Complaint details must be a dictionary")
        
        return details
    
    @validates('score_breakdown')
    def validate_score_breakdown(self, key: str, breakdown: Dict) -> Dict:
        """
        Validate score breakdown structure.
        
        As per requirement 2.2, the score breakdown should include:
        - evidence: Evidence strength score (0-40)
        - legal_basis: Legal basis score (0-30)
        - procedural: Procedural compliance score (0-20)
        - timeline: Timeline reasonableness score (0-10)
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            breakdown: Score breakdown dictionary to validate
            
        Returns:
            Dict: Validated score breakdown
            
        Raises:
            ValueError: If score breakdown is invalid
        """
        if not breakdown:
            raise ValueError("Score breakdown cannot be empty")
        
        if not isinstance(breakdown, dict):
            raise ValueError("Score breakdown must be a dictionary")
        
        # Required components as per design document
        required_components = {'evidence', 'legal_basis', 'procedural', 'timeline'}
        missing_components = required_components - set(breakdown.keys())
        
        if missing_components:
            raise ValueError(
                f"Score breakdown missing required components: {', '.join(missing_components)}"
            )
        
        # Validate component score ranges
        component_ranges = {
            'evidence': (0, 40),
            'legal_basis': (0, 30),
            'procedural': (0, 20),
            'timeline': (0, 10)
        }
        
        for component, (min_val, max_val) in component_ranges.items():
            score = breakdown.get(component)
            if not isinstance(score, (int, float)):
                raise ValueError(f"{component} score must be a number")
            if score < min_val or score > max_val:
                raise ValueError(
                    f"{component} score must be between {min_val} and {max_val}"
                )
        
        return breakdown
    
    @validates('weaknesses')
    def validate_weaknesses(self, key: str, weaknesses: Optional[List]) -> Optional[List]:
        """
        Validate weaknesses structure.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            weaknesses: List of weaknesses to validate
            
        Returns:
            Optional[List]: Validated weaknesses list
            
        Raises:
            ValueError: If weaknesses format is invalid
        """
        if weaknesses is not None and not isinstance(weaknesses, list):
            raise ValueError("Weaknesses must be a list")
        
        return weaknesses
    
    @validates('recommendations')
    def validate_recommendations(self, key: str, recommendations: Optional[List]) -> Optional[List]:
        """
        Validate recommendations structure.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            recommendations: List of recommendations to validate
            
        Returns:
            Optional[List]: Validated recommendations list
            
        Raises:
            ValueError: If recommendations format is invalid
        """
        if recommendations is not None and not isinstance(recommendations, list):
            raise ValueError("Recommendations must be a list")
        
        return recommendations
    
    def __repr__(self) -> str:
        """String representation of CaseAnalysis model."""
        return f"<CaseAnalysis(id={self.id}, user_id={self.user_id}, validity_score={self.validity_score})>"
