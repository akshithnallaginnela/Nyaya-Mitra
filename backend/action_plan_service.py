"""
Action Plan Generation Service

This service generates structured, step-by-step action plans for legal situations
with timelines, urgency levels, and time estimates.

Requirements validated:
- 3.1: Generate numbered steps based on case type
- 3.2: Add specific timelines for each step
- 3.3: Identify and highlight legal deadlines
- 3.4: Sort steps by urgency (urgent first)
- 3.5: Add time estimates for each step
- 3.6: Include alternative approaches when applicable
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field


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


class ActionPlanRequest(BaseModel):
    """Request model for action plan generation"""
    case_type: str = Field(..., description="Type of legal case")
    situation_details: Optional[str] = Field(None, description="Additional situation details")
    urgency_level: Optional[str] = Field("medium", description="Overall urgency: low, medium, high, critical")


class ActionPlanResponse(BaseModel):
    """Response model for action plan"""
    case_type: str
    total_steps: int
    estimated_total_time: str
    steps: List[Dict]
    urgent_deadlines: List[str]
    professional_help_recommended: bool


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
                    "alternatives": ["If digital evidence, use cloud backup services", "Request copies from relevant authorities"]
                },
                {
                    "title": "Gather Counter-Evidence",
                    "description": "Collect evidence that disproves the accusation: alibis, witness statements, digital records, CCTV footage, or any documentation showing your whereabouts or actions.",
                    "timeline": "Within 48 hours",
                    "time_estimate": "3-4 hours",
                    "urgency": ActionUrgency.CRITICAL.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": ["If evidence is with third parties, send formal requests immediately", "Contact witnesses for written statements"]
                },
                {
                    "title": "File Written Response",
                    "description": "Prepare and submit a written response to the accusation with your version of events and supporting evidence. Keep copies of all submissions.",
                    "timeline": "Within 7 days of receiving accusation",
                    "time_estimate": "4-6 hours",
                    "urgency": ActionUrgency.HIGH.value,
                    "is_legal_deadline": True,
                    "requires_professional": True,
                    "alternatives": ["Consider having a lawyer review before submission", "Use legal aid services for drafting assistance"]
                },
                {
                    "title": "Consult Legal Aid",
                    "description": "Contact free legal aid services to understand your rights and get professional guidance on next steps.",
                    "timeline": "Within 3 days",
                    "time_estimate": "2-3 hours",
                    "urgency": ActionUrgency.HIGH.value,
                    "is_legal_deadline": False,
                    "requires_professional": True,
                    "alternatives": ["Contact State Legal Services Authority", "Reach out to college legal cell", "Contact National Legal Services Authority helpline"]
                },
                {
                    "title": "Preserve All Communications",
                    "description": "Stop all direct communication with the accuser. Save and backup all existing communications. Any future communication should be in writing and preferably through legal counsel.",
                    "timeline": "Immediately and ongoing",
                    "time_estimate": "1 hour initial setup",
                    "urgency": ActionUrgency.HIGH.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": ["Use email for necessary communications", "CC a trusted third party on all communications"]
                },
                {
                    "title": "Prepare Witness List",
                    "description": "Identify and contact potential witnesses who can support your case. Get their written statements and contact information.",
                    "timeline": "Within 5 days",
                    "time_estimate": "3-5 hours",
                    "urgency": ActionUrgency.MEDIUM.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": ["Request affidavits from key witnesses", "Record video statements if written statements are difficult"]
                }
            ],
            "extortion": [
                {
                    "title": "Ensure Personal Safety",
                    "description": "If you feel threatened, contact police immediately. Inform trusted family members or friends about the situation. Avoid being alone in vulnerable situations.",
                    "timeline": "Immediately",
                    "time_estimate": "30 minutes",
                    "urgency": ActionUrgency.CRITICAL.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": ["Contact campus security", "Stay in public places", "Inform college authorities"]
                },
                {
                    "title": "Document All Threats",
                    "description": "Save all threatening messages, emails, calls, or communications. Take screenshots with dates and times. Do not delete anything.",
                    "timeline": "Within 24 hours",
                    "time_estimate": "1-2 hours",
                    "urgency": ActionUrgency.CRITICAL.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": ["Use call recording apps (where legal)", "Forward threatening emails to a secure backup account"]
                },
                {
                    "title": "File Police Complaint (FIR)",
                    "description": "File an FIR under IPC Section 384 (extortion) at your local police station. Bring all evidence. Get a copy of the FIR.",
                    "timeline": "Within 48 hours",
                    "time_estimate": "2-4 hours",
                    "urgency": ActionUrgency.CRITICAL.value,
                    "is_legal_deadline": True,
                    "requires_professional": False,
                    "alternatives": ["File online FIR if available in your state", "Contact women's helpline if applicable", "Seek help from legal aid to accompany you"]
                },
                {
                    "title": "Do Not Comply with Demands",
                    "description": "Do not pay money or comply with any demands. This can be used as evidence against you and encourages further extortion.",
                    "timeline": "Ongoing",
                    "time_estimate": "N/A",
                    "urgency": ActionUrgency.CRITICAL.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": ["If already paid, document the transaction as evidence", "Inform police of any payments made"]
                },
                {
                    "title": "Seek Legal Counsel",
                    "description": "Contact a lawyer specializing in criminal law. Many offer free initial consultations. Legal aid services are available for students.",
                    "timeline": "Within 3 days",
                    "time_estimate": "2-3 hours",
                    "urgency": ActionUrgency.HIGH.value,
                    "is_legal_deadline": False,
                    "requires_professional": True,
                    "alternatives": ["Contact District Legal Services Authority", "Reach out to college legal cell", "Contact cyber crime cell if extortion is online"]
                },
                {
                    "title": "Inform College Authorities",
                    "description": "If the extortion involves college-related matters or persons, inform your college administration and seek their support.",
                    "timeline": "Within 2 days",
                    "time_estimate": "1-2 hours",
                    "urgency": ActionUrgency.MEDIUM.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": ["Contact student welfare office", "Reach out to anti-ragging committee if relevant"]
                }
            ],
            "harassment": [
                {
                    "title": "Document All Incidents",
                    "description": "Maintain a detailed log of all harassment incidents with dates, times, locations, witnesses, and descriptions. Save all evidence (messages, emails, photos).",
                    "timeline": "Immediately and ongoing",
                    "time_estimate": "1 hour initial, 15 min per incident",
                    "urgency": ActionUrgency.CRITICAL.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": ["Use a diary or digital document", "Share copies with a trusted person"]
                },
                {
                    "title": "Send Cease and Desist Notice",
                    "description": "Send a formal written notice to the harasser demanding they stop the behavior. Send via registered post and keep proof of delivery.",
                    "timeline": "Within 3 days",
                    "time_estimate": "2-3 hours",
                    "urgency": ActionUrgency.HIGH.value,
                    "is_legal_deadline": False,
                    "requires_professional": True,
                    "alternatives": ["Use legal aid services to draft the notice", "Send via email with read receipt"]
                },
                {
                    "title": "File Complaint with Authorities",
                    "description": "File a complaint with police (IPC Section 354A for sexual harassment) or college Internal Complaints Committee (ICC) if applicable.",
                    "timeline": "Within 7 days",
                    "time_estimate": "3-4 hours",
                    "urgency": ActionUrgency.HIGH.value,
                    "is_legal_deadline": True,
                    "requires_professional": False,
                    "alternatives": ["File with both police and college ICC", "Contact women's helpline for support", "File online complaint if available"]
                },
                {
                    "title": "Gather Witness Statements",
                    "description": "Identify witnesses to the harassment and obtain their written statements. Include their contact information.",
                    "timeline": "Within 5 days",
                    "time_estimate": "2-4 hours",
                    "urgency": ActionUrgency.MEDIUM.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": ["Request video or audio statements", "Get statements notarized for added credibility"]
                },
                {
                    "title": "Seek Counseling Support",
                    "description": "Contact college counseling services or mental health professionals. Harassment can be traumatic and professional support is important.",
                    "timeline": "Within 1 week",
                    "time_estimate": "1-2 hours",
                    "urgency": ActionUrgency.MEDIUM.value,
                    "is_legal_deadline": False,
                    "requires_professional": True,
                    "alternatives": ["Contact helplines like iCall or Vandrevala Foundation", "Join support groups"]
                },
                {
                    "title": "Consult Legal Aid",
                    "description": "Seek legal advice on your rights and options. Free legal aid is available through State Legal Services Authority.",
                    "timeline": "Within 1 week",
                    "time_estimate": "2-3 hours",
                    "urgency": ActionUrgency.MEDIUM.value,
                    "is_legal_deadline": False,
                    "requires_professional": True,
                    "alternatives": ["Contact National Commission for Women", "Reach out to student legal aid clinics"]
                }
            ],
            "defamation": [
                {
                    "title": "Preserve Defamatory Content",
                    "description": "Take screenshots or save copies of all defamatory statements with timestamps, URLs, and context. Do not delete or alter anything.",
                    "timeline": "Within 24 hours",
                    "time_estimate": "1-2 hours",
                    "urgency": ActionUrgency.CRITICAL.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": ["Use web archiving services", "Get notarized copies of physical defamatory material"]
                },
                {
                    "title": "Send Legal Notice",
                    "description": "Send a legal notice to the person/entity making defamatory statements demanding retraction and apology. Send via registered post.",
                    "timeline": "Within 7 days",
                    "time_estimate": "3-4 hours",
                    "urgency": ActionUrgency.HIGH.value,
                    "is_legal_deadline": False,
                    "requires_professional": True,
                    "alternatives": ["Hire a lawyer to draft the notice", "Use legal aid services", "Send via email with delivery confirmation"]
                },
                {
                    "title": "Gather Evidence of Falsity",
                    "description": "Collect evidence proving the statements are false: documents, witness statements, records, or any proof contradicting the defamatory claims.",
                    "timeline": "Within 5 days",
                    "time_estimate": "3-5 hours",
                    "urgency": ActionUrgency.HIGH.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": ["Request official records from institutions", "Obtain character certificates"]
                },
                {
                    "title": "Document Damages",
                    "description": "Document any harm caused by the defamation: loss of opportunities, emotional distress, damage to reputation. Collect evidence of impact.",
                    "timeline": "Within 1 week",
                    "time_estimate": "2-3 hours",
                    "urgency": ActionUrgency.MEDIUM.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": ["Get statements from affected parties", "Document financial losses"]
                },
                {
                    "title": "File Civil/Criminal Suit",
                    "description": "If the defamer doesn't retract, file a civil suit for damages or criminal complaint under IPC Section 499-500. Consult a lawyer for the best approach.",
                    "timeline": "Within 30 days of notice",
                    "time_estimate": "5-8 hours",
                    "urgency": ActionUrgency.MEDIUM.value,
                    "is_legal_deadline": True,
                    "requires_professional": True,
                    "alternatives": ["File civil suit for monetary compensation", "File criminal complaint for punishment", "Pursue both civil and criminal remedies"]
                },
                {
                    "title": "Request Content Removal",
                    "description": "If defamation is online, report to the platform/website and request removal. Cite violation of terms of service and provide evidence.",
                    "timeline": "Within 3 days",
                    "time_estimate": "1-2 hours",
                    "urgency": ActionUrgency.HIGH.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": ["Contact cyber crime cell for assistance", "File complaint with IT Act provisions"]
                }
            ],
            "general": [
                {
                    "title": "Understand Your Legal Rights",
                    "description": "Research and understand your legal rights related to your situation. Use reliable sources like government websites and legal aid resources.",
                    "timeline": "Within 2 days",
                    "time_estimate": "2-3 hours",
                    "urgency": ActionUrgency.HIGH.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": ["Consult with legal aid services", "Use online legal resources"]
                },
                {
                    "title": "Gather All Relevant Documents",
                    "description": "Collect all documents, evidence, and information related to your case. Organize them chronologically with proper labels.",
                    "timeline": "Within 3 days",
                    "time_estimate": "3-4 hours",
                    "urgency": ActionUrgency.HIGH.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": ["Create digital copies of all documents", "Maintain both physical and digital records"]
                },
                {
                    "title": "Consult Legal Professional",
                    "description": "Seek advice from a qualified lawyer or legal aid service. Many offer free initial consultations for students.",
                    "timeline": "Within 5 days",
                    "time_estimate": "2-3 hours",
                    "urgency": ActionUrgency.HIGH.value,
                    "is_legal_deadline": False,
                    "requires_professional": True,
                    "alternatives": ["Contact State Legal Services Authority", "Reach out to college legal cell", "Use online legal consultation services"]
                },
                {
                    "title": "Document Everything",
                    "description": "Maintain detailed records of all communications, events, and actions taken. Include dates, times, and witnesses.",
                    "timeline": "Ongoing",
                    "time_estimate": "15-30 min daily",
                    "urgency": ActionUrgency.MEDIUM.value,
                    "is_legal_deadline": False,
                    "requires_professional": False,
                    "alternatives": ["Use a diary or digital document", "Take photos/screenshots of relevant evidence"]
                },
                {
                    "title": "Explore Resolution Options",
                    "description": "Consider all available options: negotiation, mediation, filing complaints, or legal action. Discuss with your lawyer which approach is best.",
                    "timeline": "Within 1 week",
                    "time_estimate": "2-3 hours",
                    "urgency": ActionUrgency.MEDIUM.value,
                    "is_legal_deadline": False,
                    "requires_professional": True,
                    "alternatives": ["Try mediation before litigation", "Explore alternative dispute resolution"]
                }
            ]
        }
    
    def generate_action_plan(self, request: ActionPlanRequest) -> ActionPlanResponse:
        """
        Generate an action plan based on case type and situation.
        
        Args:
            request: ActionPlanRequest with case type and details
            
        Returns:
            ActionPlanResponse with numbered steps, timelines, and urgency
        """
        # Get template for case type (default to general if not found)
        case_type = request.case_type.lower().replace(" ", "_")
        template_steps = self.case_type_templates.get(case_type, self.case_type_templates["general"])
        
        # Create ActionStep objects
        action_steps = []
        for idx, step_data in enumerate(template_steps, start=1):
            action_step = ActionStep(
                step_number=idx,
                title=step_data["title"],
                description=step_data["description"],
                timeline=step_data["timeline"],
                time_estimate=step_data["time_estimate"],
                urgency=step_data["urgency"],
                is_legal_deadline=step_data["is_legal_deadline"],
                requires_professional=step_data["requires_professional"],
                alternatives=step_data.get("alternatives")
            )
            action_steps.append(action_step)
        
        # Sort by urgency (urgent first) - Requirement 3.4
        action_steps.sort(key=lambda x: x.urgency, reverse=True)
        
        # Renumber steps after sorting
        for idx, step in enumerate(action_steps, start=1):
            step.step_number = idx
        
        # Extract urgent deadlines - Requirement 3.3
        urgent_deadlines = [
            f"Step {step.step_number}: {step.title} - {step.timeline}"
            for step in action_steps
            if step.is_legal_deadline
        ]
        
        # Calculate total estimated time
        total_time = self._calculate_total_time(action_steps)
        
        # Check if professional help is recommended
        professional_help = any(step.requires_professional for step in action_steps)
        
        # Convert steps to dictionaries
        steps_dict = [step.to_dict() for step in action_steps]
        
        return ActionPlanResponse(
            case_type=request.case_type,
            total_steps=len(action_steps),
            estimated_total_time=total_time,
            steps=steps_dict,
            urgent_deadlines=urgent_deadlines,
            professional_help_recommended=professional_help
        )
    
    def _calculate_total_time(self, steps: List[ActionStep]) -> str:
        """
        Calculate total estimated time for all steps.
        
        Args:
            steps: List of action steps
            
        Returns:
            String representation of total time
        """
        total_hours = 0
        
        for step in steps:
            # Parse time estimate (e.g., "2-3 hours", "30 minutes")
            time_str = step.time_estimate.lower()
            
            if "hour" in time_str:
                # Extract hours (take average if range)
                parts = time_str.split("-")
                if len(parts) == 2:
                    hours = (float(parts[0]) + float(parts[1].split()[0])) / 2
                else:
                    hours = float(time_str.split()[0])
                total_hours += hours
            elif "min" in time_str:
                # Extract minutes
                parts = time_str.split("-")
                if len(parts) == 2:
                    minutes = (float(parts[0]) + float(parts[1].split()[0])) / 2
                else:
                    minutes = float(time_str.split()[0])
                total_hours += minutes / 60
        
        # Format output
        if total_hours < 1:
            return f"{int(total_hours * 60)} minutes"
        elif total_hours < 24:
            return f"{total_hours:.1f} hours"
        else:
            days = total_hours / 8  # Assuming 8 working hours per day
            return f"{days:.1f} days"
    
    def get_available_case_types(self) -> List[str]:
        """
        Get list of available case types.
        
        Returns:
            List of case type names
        """
        return list(self.case_type_templates.keys())


# Singleton instance
_action_plan_service: Optional[ActionPlanService] = None


def get_action_plan_service() -> ActionPlanService:
    """
    Get or create singleton action plan service instance.
    
    Returns:
        ActionPlanService instance
    """
    global _action_plan_service
    if _action_plan_service is None:
        _action_plan_service = ActionPlanService()
    return _action_plan_service
