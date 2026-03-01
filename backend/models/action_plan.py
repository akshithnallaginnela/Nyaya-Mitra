"""
Action Plan model for storing generated action plans.

This module implements the ActionPlan model to support storing and
retrieving action plans generated for users.

Requirements: 3.1 (Action plan generation and storage)
"""

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship, validates

from database import BaseModel

if TYPE_CHECKING:
    from models.user import User


class ActionPlan(BaseModel):
    """
    ActionPlan model for storing generated action plans.
    
    Inherits from BaseModel which provides:
    - id: UUID primary key
    - created_at: Timestamp of action plan creation
    - updated_at: Timestamp of last update
    
    Additional fields:
    - user_id: Foreign key to User model
    - case_type: Type of legal case
    - situation_details: Additional situation details
    - total_steps: Total number of steps in the plan
    - estimated_total_time: Estimated time to complete all steps
    - steps: JSON array of action steps
    - urgent_deadlines: JSON array of urgent deadlines
    - professional_help_recommended: Whether professional help is recommended
    - status: Current status of the action plan (active, completed, archived)
    - progress: JSON object tracking completion of steps
    
    Relationships:
    - user: Many-to-one relationship with User
    """
    
    __tablename__ = "action_plans"
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    case_type = Column(
        String(100),
        nullable=False
    )
    
    situation_details = Column(
        Text,
        nullable=True
    )
    
    total_steps = Column(
        Integer,
        nullable=False
    )
    
    estimated_total_time = Column(
        String(100),
        nullable=False
    )
    
    steps = Column(
        JSON,
        nullable=False
    )
    
    urgent_deadlines = Column(
        JSON,
        nullable=False,
        default=[]
    )
    
    professional_help_recommended = Column(
        Boolean,
        nullable=False,
        default=False
    )
    
    status = Column(
        String(20),
        nullable=False,
        default="active"
    )
    
    progress = Column(
        JSON,
        nullable=True,
        default={}
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="action_plans"
    )
    
    @validates('status')
    def validate_status(self, key: str, status: str) -> str:
        """
        Validate action plan status.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            status: Status to validate
            
        Returns:
            str: Validated status
            
        Raises:
            ValueError: If status is invalid
        """
        valid_statuses = {'active', 'completed', 'archived'}
        
        if status not in valid_statuses:
            raise ValueError(
                f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        return status
    
    @validates('total_steps')
    def validate_total_steps(self, key: str, total_steps: int) -> int:
        """
        Validate total steps count.
        
        Args:
            key: Field name (automatically provided by SQLAlchemy)
            total_steps: Total steps to validate
            
        Returns:
            int: Validated total steps
            
        Raises:
            ValueError: If total steps is invalid
        """
        if total_steps < 1:
            raise ValueError("Total steps must be at least 1")
        
        return total_steps
    
    def __repr__(self) -> str:
        """String representation of ActionPlan model."""
        return f"<ActionPlan(id={self.id}, user_id={self.user_id}, case_type={self.case_type}, status={self.status})>"
