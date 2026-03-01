"""
Action Plan Generation Service

This service generates structured, step-by-step action plans for legal situations
with timelines, urgency levels, and time estimates.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class ActionUrgency(Enum):
    """Urgency levels for action steps"""
    CRITICAL = 10  # Immediate action required
    HIGH = 8      # Action needed within days
    MEDIUM = 5    # Action needed within weeks
    LOW = 3       # Action can wait


@dataclass
class ActionStep:
    """Represents a single step in an action plan"""
    step_number: int
    title: str
    description: str
    timeline: str  # e.g., "Within 24 hours", "By March 15, 2024"
    time_estimate: str  # e.g., "2-3 hours", "30 minutes"
    urgency: int  # 1-10 scale
    is_legal_deadline: bool
    requires_professional: bool
    alternatives: Optional[List[str]] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "step_number": self.step_number,
            "title": self.title,
            "description": self.description,
            "timeline": self.timeline,
            "time_estimate": self.time_estimate,
            "urgency": self.urgency,
            "is_legal_deadline": self.is_legal_deadline,
            "requires_professional": self.requires_professional,
            "alternatives": self.alternatives or []
        }


class ActionPlanService:
    """Service for generating action plans based on case type and situation"""
    
    def __init__(self):
        self.case_type_templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, List[Dict]]:
        """Initialize action plan templates for different case types"""
        return {
            "false_accusation": [
                {
                    "title": "Document the Accusation",
                    "description": "Collect all written evidence of the accusation including emails, messages, letters, or formal complaints. Take screenshots with timestamps.",
                    "timeline": "Within 24 hours",
                    "time_estimate": "1-2 hours",
                    "urgency": ActionUrgency.CRITICAL.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": None
                },
                {
                    "title": "Gather Counter-Evidence",
                    "description": "Collect evidence that disproves the accusation: alibis, witness statements, digital records, CCTV footage, or any documentation showing your whereabouts or actions.",
                    "timeline": "Within 48 hours",
                    "time_estimate": "3-4 hours",
                    "urgency": ActionUrgency.CRITICAL.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": ["If evidence is with third parties, send formal requests immediately"]
                },
                {
                    "title": "File Written Response",
                    "description": "Prepare and submit a written response to the accusation with your version of events and supporting evidence. Keep copies of all submissions.",
                    "timeline": "Within 7 days of receiving accusation",
                    "time_estimate": "4-6 hours",
                    "urgency": ActionUrgency.HIGH.value,
                    "is_legal_deadline": True,
                    "requires_professional": True,
                    "alternatives": ["Consider having a lawyer review before submission"]
                },
                {
                    "title": "Consult Legal Aid",
                    "description": "Contact free legal aid services to understand your rights and get professional guidance on next steps.",
                    "timeline": "Within 3 days",
                    "time_estimate": "2-3 hours",
                    "urgency": ActionUrgency.HIGH.value,
                    "is_legal_deadline": False,
                    "requires_professional": True,
                    "alternatives":