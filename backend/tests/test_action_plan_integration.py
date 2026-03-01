"""
Tests for action plan integration with chat system.

This test file verifies:
1. Action plan model creation and storage
2. Action plan generation via chat commands
3. Action plan retrieval and update endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from main import app
from database import Base, get_db_session
from models.user import User
from models.action_plan import ActionPlan
from models.conversation import Conversation, Message
from utils.jwt import create_access_token


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_action_plan_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_session] = override_get_db


@pytest.fixture(scope="function")
def test_db():
    """Create test database and tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    db = TestingSessionLocal()
    try:
        user = User(
            email="test@example.com",
            full_name="Test User",
            preferred_language="en",
            is_active=True
        )
        user.set_password("TestPass123!")
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers with JWT token."""
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestActionPlanModel:
    """Test ActionPlan model."""
    
    def test_create_action_plan(self, test_db, test_user):
        """Test creating an action plan in the database."""
        db = TestingSessionLocal()
        try:
            action_plan = ActionPlan(
                user_id=test_user.id,
                case_type="false_accusation",
                situation_details="Test situation",
                total_steps=5,
                estimated_total_time="10 hours",
                steps=[
                    {
                        "step_number": 1,
                        "title": "Test Step",
                        "description": "Test description",
                        "timeline": "Within 24 hours",
                        "time_estimate": "2 hours",
                        "urgency": 10,
                        "is_legal_deadline": False,
                        "requires_professional": False,
                        "alternatives": []
                    }
                ],
                urgent_deadlines=["Step 1: Test Step - Within 24 hours"],
                professional_help_recommended=True,
                status="active",
                progress={}
            )
            
            db.add(action_plan)
            db.commit()
            db.refresh(action_plan)
            
            assert action_plan.id is not None
            assert action_plan.user_id == test_user.id
            assert action_plan.case_type == "false_accusation"
            assert action_plan.total_steps == 5
            assert action_plan.status == "active"
            assert len(action_plan.steps) == 1
            
        finally:
            db.close()
    
    def test_action_plan_status_validation(self, test_db, test_user):
        """Test action plan status validation."""
        db = TestingSessionLocal()
        try:
            action_plan = ActionPlan(
                user_id=test_user.id,
                case_type="general",
                total_steps=1,
                estimated_total_time="1 hour",
                steps=[],
                urgent_deadlines=[],
                professional_help_recommended=False,
                status="invalid_status"
            )
            
            db.add(action_plan)
            with pytest.raises(ValueError, match="Invalid status"):
                db.commit()
                
        finally:
            db.rollback()
            db.close()
    
    def test_action_plan_cascade_delete(self, test_db, test_user):
        """Test that action plans are deleted when user is deleted."""
        db = TestingSessionLocal()
        try:
            # Create action plan
            action_plan = ActionPlan(
                user_id=test_user.id,
                case_type="general",
                total_steps=1,
                estimated_total_time="1 hour",
                steps=[],
                urgent_deadlines=[],
                professional_help_recommended=False,
                status="active"
            )
            
            db.add(action_plan)
            db.commit()
            
            action_plan_id = action_plan.id
            
            # Delete user
            db.delete(test_user)
            db.commit()
            
            # Verify action plan is deleted
            deleted_plan = db.query(ActionPlan).filter(ActionPlan.id == action_plan_id).first()
            assert deleted_plan is None
            
        finally:
            db.close()


class TestActionPlanAPI:
    """Test action plan API endpoints."""
    
    def test_generate_action_plan(self, client, auth_headers, test_user):
        """Test generating an action plan via API."""
        response = client.post(
            "/api/action-plan/generate",
            json={
                "case_type": "false_accusation",
                "situation_details": "I've been falsely accused of cheating",
                "urgency_level": "high"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["case_type"] == "false_accusation"
        assert data["total_steps"] > 0
        assert "estimated_total_time" in data
        assert len(data["steps"]) > 0
        assert "urgent_deadlines" in data
        assert "professional_help_recommended" in data
        assert data["status"] == "active"
    
    def test_list_action_plans(self, client, auth_headers, test_user):
        """Test listing action plans."""
        # Create action plans
        for i in range(3):
            client.post(
                "/api/action-plan/generate",
                json={
                    "case_type": "general",
                    "situation_details": f"Test situation {i}",
                    "urgency_level": "medium"
                },
                headers=auth_headers
            )
        
        # List action plans
        response = client.get(
            "/api/action-plan/list",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 3
        assert len(data["action_plans"]) == 3
        assert data["page"] == 1
        assert data["page_size"] == 20
    
    def test_get_action_plan(self, client, auth_headers, test_user):
        """Test retrieving a specific action plan."""
        # Create action plan
        create_response = client.post(
            "/api/action-plan/generate",
            json={
                "case_type": "harassment",
                "situation_details": "Test harassment case",
                "urgency_level": "high"
            },
            headers=auth_headers
        )
        
        action_plan_id = create_response.json()["id"]
        
        # Get action plan
        response = client.get(
            f"/api/action-plan/{action_plan_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == action_plan_id
        assert data["case_type"] == "harassment"
        assert data["situation_details"] == "Test harassment case"
    
    def test_update_action_plan(self, client, auth_headers, test_user):
        """Test updating an action plan."""
        # Create action plan
        create_response = client.post(
            "/api/action-plan/generate",
            json={
                "case_type": "general",
                "situation_details": "Test case",
                "urgency_level": "medium"
            },
            headers=auth_headers
        )
        
        action_plan_id = create_response.json()["id"]
        
        # Update action plan
        response = client.patch(
            f"/api/action-plan/{action_plan_id}",
            json={
                "status": "completed",
                "progress": {"step_1": "completed", "step_2": "in_progress"}
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "completed"
        assert data["progress"]["step_1"] == "completed"
        assert data["progress"]["step_2"] == "in_progress"
    
    def test_delete_action_plan(self, client, auth_headers, test_user):
        """Test deleting an action plan."""
        # Create action plan
        create_response = client.post(
            "/api/action-plan/generate",
            json={
                "case_type": "general",
                "situation_details": "Test case",
                "urgency_level": "medium"
            },
            headers=auth_headers
        )
        
        action_plan_id = create_response.json()["id"]
        
        # Delete action plan
        response = client.delete(
            f"/api/action-plan/{action_plan_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Action plan deleted successfully"
        
        # Verify deletion
        get_response = client.get(
            f"/api/action-plan/{action_plan_id}",
            headers=auth_headers
        )
        
        assert get_response.status_code == 404


class TestChatActionPlanIntegration:
    """Test action plan generation via chat commands."""
    
    def test_chat_action_plan_command(self, client, auth_headers, test_user):
        """Test generating action plan via chat command."""
        response = client.post(
            "/api/chat/query",
            json={
                "query": "I need an action plan for a false accusation case. What steps should I take?",
                "language": "en"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "action plan" in data["response"].lower()
        assert "step" in data["response"].lower()
        assert data["confidence"] == 1.0
        assert data["needs_clarification"] == False
    
    def test_chat_action_plan_stored(self, client, auth_headers, test_user):
        """Test that action plan generated via chat is stored in database."""
        # Generate action plan via chat
        chat_response = client.post(
            "/api/chat/query",
            json={
                "query": "Create an action plan for harassment case",
                "language": "en"
            },
            headers=auth_headers
        )
        
        assert chat_response.status_code == 200
        
        # Verify action plan is stored
        list_response = client.get(
            "/api/action-plan/list",
            headers=auth_headers
        )
        
        assert list_response.status_code == 200
        data = list_response.json()
        
        assert data["total"] >= 1
        assert any(plan["case_type"] == "harassment" for plan in data["action_plans"])
    
    def test_chat_regular_query_no_action_plan(self, client, auth_headers, test_user):
        """Test that regular queries don't trigger action plan generation."""
        response = client.post(
            "/api/chat/query",
            json={
                "query": "What is defamation under Indian law?",
                "language": "en"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify no action plan was created
        list_response = client.get(
            "/api/action-plan/list",
            headers=auth_headers
        )
        
        assert list_response.status_code == 200
        data = list_response.json()
        
        # Should be 0 since this was a regular query
        assert data["total"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
