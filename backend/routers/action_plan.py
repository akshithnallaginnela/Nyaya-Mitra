"""
Action Plan API endpoints for generating and managing action plans.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from database import get_db_session as get_db
from models.user import User
from models.action_plan import ActionPlan
from utils.jwt import get_current_user
from action_plan_service import (
    get_action_plan_service,
    ActionPlanRequest,
    ActionPlanResponse
)


router = APIRouter(prefix="/api/action-plan", tags=["action-plan"])


# Request/Response models
class ActionPlanCreateRequest(BaseModel):
    """Request model for creating an action plan."""
    case_type: str = Field(..., description="Type of legal case")
    situation_details: Optional[str] = Field(None, description="Additional situation details")
    urgency_level: Optional[str] = Field("medium", description="Overall urgency: low, medium, high, critical")


class ActionPlanUpdateRequest(BaseModel):
    """Request model for updating an action plan."""
    status: Optional[str] = Field(None, description="Status: active, completed, archived")
    progress: Optional[Dict[str, Any]] = Field(None, description="Progress tracking data")


class ActionPlanListItem(BaseModel):
    """Action plan list item model."""
    id: str
    case_type: str
    total_steps: int
    estimated_total_time: str
    status: str
    professional_help_recommended: bool
    created_at: datetime
    updated_at: datetime


class ActionPlanListResponse(BaseModel):
    """Response model for action plan list."""
    action_plans: List[ActionPlanListItem]
    total: int
    page: int
    page_size: int


class ActionPlanDetailResponse(BaseModel):
    """Response model for action plan details."""
    id: str
    case_type: str
    situation_details: Optional[str]
    total_steps: int
    estimated_total_time: str
    steps: List[Dict]
    urgent_deadlines: List[str]
    professional_help_recommended: bool
    status: str
    progress: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


@router.post("/generate", response_model=ActionPlanDetailResponse)
async def generate_action_plan(
    request: ActionPlanCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a new action plan based on case type and situation.
    
    This endpoint:
    1. Generates an action plan using the action plan service
    2. Stores the action plan in the database
    3. Returns the complete action plan with all steps
    
    Args:
        request: Action plan creation request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        ActionPlanDetailResponse with complete action plan
        
    Raises:
        HTTPException: If action plan generation fails
    """
    try:
        # Generate action plan using service
        service = get_action_plan_service()
        service_request = ActionPlanRequest(
            case_type=request.case_type,
            situation_details=request.situation_details,
            urgency_level=request.urgency_level
        )
        
        plan_response = service.generate_action_plan(service_request)
        
        # Store action plan in database
        action_plan = ActionPlan(
            user_id=current_user.id,
            case_type=plan_response.case_type,
            situation_details=request.situation_details,
            total_steps=plan_response.total_steps,
            estimated_total_time=plan_response.estimated_total_time,
            steps=plan_response.steps,
            urgent_deadlines=plan_response.urgent_deadlines,
            professional_help_recommended=plan_response.professional_help_recommended,
            status="active",
            progress={}
        )
        
        db.add(action_plan)
        db.commit()
        db.refresh(action_plan)
        
        return ActionPlanDetailResponse(
            id=str(action_plan.id),
            case_type=action_plan.case_type,
            situation_details=action_plan.situation_details,
            total_steps=action_plan.total_steps,
            estimated_total_time=action_plan.estimated_total_time,
            steps=action_plan.steps,
            urgent_deadlines=action_plan.urgent_deadlines,
            professional_help_recommended=action_plan.professional_help_recommended,
            status=action_plan.status,
            progress=action_plan.progress,
            created_at=action_plan.created_at,
            updated_at=action_plan.updated_at
        )
        
    except Exception as e:
        print(f"Error generating action plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating the action plan. Please try again."
        )


@router.get("/list", response_model=ActionPlanListResponse)
async def list_action_plans(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of user's action plans.
    
    Args:
        page: Page number (default: 1)
        page_size: Number of action plans per page (default: 20)
        status_filter: Optional status filter (active, completed, archived)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        ActionPlanListResponse with paginated action plans
    """
    try:
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Build query
        query = db.query(ActionPlan).filter(
            ActionPlan.user_id == current_user.id
        )
        
        # Apply status filter if provided
        if status_filter:
            query = query.filter(ActionPlan.status == status_filter)
        
        # Get total count
        total = query.count()
        
        # Get action plans with pagination
        action_plans = query.order_by(
            ActionPlan.updated_at.desc()
        ).offset(offset).limit(page_size).all()
        
        # Build response
        plan_items = [
            ActionPlanListItem(
                id=str(plan.id),
                case_type=plan.case_type,
                total_steps=plan.total_steps,
                estimated_total_time=plan.estimated_total_time,
                status=plan.status,
                professional_help_recommended=plan.professional_help_recommended,
                created_at=plan.created_at,
                updated_at=plan.updated_at
            )
            for plan in action_plans
        ]
        
        return ActionPlanListResponse(
            action_plans=plan_items,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        print(f"Error retrieving action plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving action plans."
        )


@router.get("/{action_plan_id}", response_model=ActionPlanDetailResponse)
async def get_action_plan(
    action_plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed action plan by ID.
    
    Args:
        action_plan_id: ID of the action plan
        current_user: Authenticated user
        db: Database session
        
    Returns:
        ActionPlanDetailResponse with complete action plan details
        
    Raises:
        HTTPException: If action plan not found or unauthorized
    """
    try:
        # Retrieve action plan
        action_plan = db.query(ActionPlan).filter(
            ActionPlan.id == action_plan_id,
            ActionPlan.user_id == current_user.id
        ).first()
        
        if not action_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Action plan not found"
            )
        
        return ActionPlanDetailResponse(
            id=str(action_plan.id),
            case_type=action_plan.case_type,
            situation_details=action_plan.situation_details,
            total_steps=action_plan.total_steps,
            estimated_total_time=action_plan.estimated_total_time,
            steps=action_plan.steps,
            urgent_deadlines=action_plan.urgent_deadlines,
            professional_help_recommended=action_plan.professional_help_recommended,
            status=action_plan.status,
            progress=action_plan.progress,
            created_at=action_plan.created_at,
            updated_at=action_plan.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving action plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the action plan."
        )


@router.patch("/{action_plan_id}", response_model=ActionPlanDetailResponse)
async def update_action_plan(
    action_plan_id: str,
    request: ActionPlanUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an action plan's status or progress.
    
    Args:
        action_plan_id: ID of the action plan
        request: Update request with status and/or progress
        current_user: Authenticated user
        db: Database session
        
    Returns:
        ActionPlanDetailResponse with updated action plan
        
    Raises:
        HTTPException: If action plan not found or unauthorized
    """
    try:
        # Retrieve action plan
        action_plan = db.query(ActionPlan).filter(
            ActionPlan.id == action_plan_id,
            ActionPlan.user_id == current_user.id
        ).first()
        
        if not action_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Action plan not found"
            )
        
        # Update fields if provided
        if request.status is not None:
            action_plan.status = request.status
        
        if request.progress is not None:
            action_plan.progress = request.progress
        
        db.commit()
        db.refresh(action_plan)
        
        return ActionPlanDetailResponse(
            id=str(action_plan.id),
            case_type=action_plan.case_type,
            situation_details=action_plan.situation_details,
            total_steps=action_plan.total_steps,
            estimated_total_time=action_plan.estimated_total_time,
            steps=action_plan.steps,
            urgent_deadlines=action_plan.urgent_deadlines,
            professional_help_recommended=action_plan.professional_help_recommended,
            status=action_plan.status,
            progress=action_plan.progress,
            created_at=action_plan.created_at,
            updated_at=action_plan.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating action plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the action plan."
        )


@router.delete("/{action_plan_id}")
async def delete_action_plan(
    action_plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an action plan.
    
    Args:
        action_plan_id: ID of the action plan
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If action plan not found or unauthorized
    """
    try:
        # Retrieve action plan
        action_plan = db.query(ActionPlan).filter(
            ActionPlan.id == action_plan_id,
            ActionPlan.user_id == current_user.id
        ).first()
        
        if not action_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Action plan not found"
            )
        
        db.delete(action_plan)
        db.commit()
        
        return {"message": "Action plan deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting action plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the action plan."
        )
