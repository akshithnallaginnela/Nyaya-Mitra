"""
Unit tests for action plan generation service.
"""
import pytest
from action_plan_service import (
    ActionPlanService,
    ActionPlanRequest,
    ActionPlanResponse,
    ActionStep,
    ActionUrgency,
    get_action_plan_service
)


class TestActionPlanService:
    """Test suite for ActionPlanService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = ActionPlanService()
    
    def test_generate_action_plan_false_accusation(self):
        """Test action plan generation for false accusation case"""
        request = ActionPlanRequest(
            case_type="false_accusation",
            situation_details="Accused of cheating in exam"
        )
        
        response = self.service.generate_action_plan(request)
        
        # Verify response structure
        assert isinstance(response, ActionPlanResponse)
        assert response.case_type == "false_accusation"
        assert response.total_steps > 0
        assert len(response.steps) == response.total_steps
        assert isinstance(response.estimated_total_time, str)
        assert isinstance(response.urgent_deadlines, list)
        assert isinstance(response.professional_help_recommended, bool)
    
    def test_generate_action_plan_extortion(self):
        """Test action plan generation for extortion case"""
        request = ActionPlanRequest(
            case_type="extortion",
            situation_details="Being threatened for money"
        )
        
        response = self.service.generate_action_plan(request)
        
        assert response.case_type == "extortion"
        assert response.total_steps > 0
        assert len(response.steps) > 0
    
    def test_generate_action_plan_harassment(self):
        """Test action plan generation for harassment case"""
        request = ActionPlanRequest(
            case_type="harassment",
            situation_details="Facing workplace harassment"
        )
        
        response = self.service.generate_action_plan(request)
        
        assert response.case_type == "harassment"
        assert response.total_steps > 0
    
    def test_generate_action_plan_defamation(self):
        """Test action plan generation for defamation case"""
        request = ActionPlanRequest(
            case_type="defamation",
            situation_details="False statements posted online"
        )
        
        response = self.service.generate_action_plan(request)
        
        assert response.case_type == "defamation"
        assert response.total_steps > 0
    
    def test_generate_action_plan_general(self):
        """Test action plan generation for general case"""
        request = ActionPlanRequest(
            case_type="general",
            situation_details="Need legal guidance"
        )
        
        response = self.service.generate_action_plan(request)
        
        assert response.case_type == "general"
        assert response.total_steps > 0
    
    def test_generate_action_plan_unknown_case_type(self):
        """Test action plan generation for unknown case type defaults to general"""
        request = ActionPlanRequest(
            case_type="unknown_case_type",
            situation_details="Some situation"
        )
        
        response = self.service.generate_action_plan(request)
        
        # Should default to general template
        assert response.total_steps > 0
        assert len(response.steps) > 0
    
    def test_numbered_steps_structure(self):
        """
        Test Property 13: Numbered steps structure
        Validates: Requirements 3.1
        
        For any action plan generated, the plan should contain a list of steps
        where each step has a sequential number starting from 1.
        """
        request = ActionPlanRequest(case_type="false_accusation")
        response = self.service.generate_action_plan(request)
        
        # Verify steps are numbered sequentially starting from 1
        for idx, step in enumerate(response.steps, start=1):
            assert step["step_number"] == idx
        
        # Verify all steps have step_number field
        assert all("step_number" in step for step in response.steps)
    
    def test_timeline_presence(self):
        """
        Test Property 14: Timeline presence
        Validates: Requirements 3.2
        
        For any action plan generated, each step should include a timeline field
        with specific time information.
        """
        request = ActionPlanRequest(case_type="extortion")
        response = self.service.generate_action_plan(request)
        
        # Verify all steps have timeline field
        for step in response.steps:
            assert "timeline" in step
            assert isinstance(step["timeline"], str)
            assert len(step["timeline"]) > 0
    
    def test_deadline_highlighting(self):
        """
        Test Property 15: Deadline highlighting
        Validates: Requirements 3.3
        
        For any action plan containing legal deadlines, those deadlines should be
        marked with a highlight flag or prominent indicator.
        """
        request = ActionPlanRequest(case_type="false_accusation")
        response = self.service.generate_action_plan(request)
        
        # Find steps with legal deadlines
        deadline_steps = [step for step in response.steps if step["is_legal_deadline"]]
        
        # Verify deadline steps are in urgent_deadlines list
        assert len(response.urgent_deadlines) == len(deadline_steps)
        
        # Verify all steps have is_legal_deadline field
        assert all("is_legal_deadline" in step for step in response.steps)
    
    def test_urgency_ordering(self):
        """
        Test Property 16: Urgency ordering
        Validates: Requirements 3.4
        
        For any action plan with steps of varying urgency levels, urgent steps
        (urgency > 7/10) should appear before non-urgent steps.
        """
        request = ActionPlanRequest(case_type="harassment")
        response = self.service.generate_action_plan(request)
        
        # Verify steps are sorted by urgency (descending)
        urgencies = [step["urgency"] for step in response.steps]
        assert urgencies == sorted(urgencies, reverse=True)
        
        # Verify urgent steps (>7) come before non-urgent steps (<=7)
        found_non_urgent = False
        for step in response.steps:
            if step["urgency"] <= 7:
                found_non_urgent = True
            elif found_non_urgent:
                # Found an urgent step after a non-urgent step - should not happen
                pytest.fail("Urgent step found after non-urgent step")
    
    def test_time_estimate_presence(self):
        """
        Test Property 17: Time estimate presence
        Validates: Requirements 3.5
        
        For any action plan generated, each step should include an estimated
        time requirement field.
        """
        request = ActionPlanRequest(case_type="defamation")
        response = self.service.generate_action_plan(request)
        
        # Verify all steps have time_estimate field
        for step in response.steps:
            assert "time_estimate" in step
            assert isinstance(step["time_estimate"], str)
            assert len(step["time_estimate"]) > 0
    
    def test_alternatives_when_applicable(self):
        """
        Test that alternatives are included when applicable
        Validates: Requirements 3.6
        """
        request = ActionPlanRequest(case_type="false_accusation")
        response = self.service.generate_action_plan(request)
        
        # Verify steps have alternatives field
        assert all("alternatives" in step for step in response.steps)
        
        # At least some steps should have alternatives
        steps_with_alternatives = [
            step for step in response.steps 
            if step["alternatives"] and len(step["alternatives"]) > 0
        ]
        assert len(steps_with_alternatives) > 0
    
    def test_action_step_to_dict(self):
        """Test ActionStep to_dict conversion"""
        step = ActionStep(
            step_number=1,
            title="Test Step",
            description="Test description",
            timeline="Within 24 hours",
            time_estimate="1-2 hours",
            urgency=10,
            is_legal_deadline=True,
            requires_professional=False,
            alternatives=["Alternative 1", "Alternative 2"]
        )
        
        step_dict = step.to_dict()
        
        assert step_dict["step_number"] == 1
        assert step_dict["title"] == "Test Step"
        assert step_dict["description"] == "Test description"
        assert step_dict["timeline"] == "Within 24 hours"
        assert step_dict["time_estimate"] == "1-2 hours"
        assert step_dict["urgency"] == 10
        assert step_dict["is_legal_deadline"] is True
        assert step_dict["requires_professional"] is False
        assert len(step_dict["alternatives"]) == 2
    
    def test_action_step_to_dict_no_alternatives(self):
        """Test ActionStep to_dict with no alternatives"""
        step = ActionStep(
            step_number=1,
            title="Test Step",
            description="Test description",
            timeline="Within 24 hours",
            time_estimate="1 hour",
            urgency=5,
            is_legal_deadline=False,
            requires_professional=False,
            alternatives=None
        )
        
        step_dict = step.to_dict()
        assert step_dict["alternatives"] == []
    
    def test_calculate_total_time_hours(self):
        """Test total time calculation with hours"""
        steps = [
            ActionStep(1, "Step 1", "Desc", "Timeline", "2-3 hours", 10, False, False),
            ActionStep(2, "Step 2", "Desc", "Timeline", "1 hour", 8, False, False),
        ]
        
        total_time = self.service._calculate_total_time(steps)
        assert "hours" in total_time.lower()
    
    def test_calculate_total_time_minutes(self):
        """Test total time calculation with minutes"""
        steps = [
            ActionStep(1, "Step 1", "Desc", "Timeline", "30 minutes", 10, False, False),
        ]
        
        total_time = self.service._calculate_total_time(steps)
        assert "minutes" in total_time.lower()
    
    def test_get_available_case_types(self):
        """Test getting available case types"""
        case_types = self.service.get_available_case_types()
        
        assert isinstance(case_types, list)
        assert len(case_types) > 0
        assert "false_accusation" in case_types
        assert "extortion" in case_types
        assert "harassment" in case_types
        assert "defamation" in case_types
        assert "general" in case_types
    
    def test_singleton_service(self):
        """Test singleton pattern for service"""
        service1 = get_action_plan_service()
        service2 = get_action_plan_service()
        
        assert service1 is service2
    
    def test_professional_help_recommended(self):
        """Test professional help recommendation"""
        request = ActionPlanRequest(case_type="false_accusation")
        response = self.service.generate_action_plan(request)
        
        # False accusation should recommend professional help
        assert response.professional_help_recommended is True
    
    def test_urgent_deadlines_extraction(self):
        """Test extraction of urgent deadlines"""
        request = ActionPlanRequest(case_type="extortion")
        response = self.service.generate_action_plan(request)
        
        # Verify urgent_deadlines contains only steps with is_legal_deadline=True
        deadline_steps = [step for step in response.steps if step["is_legal_deadline"]]
        assert len(response.urgent_deadlines) == len(deadline_steps)
        
        # Verify format of urgent deadlines
        for deadline in response.urgent_deadlines:
            assert "Step" in deadline
            assert ":" in deadline
    
    def test_empty_situation_details(self):
        """Test action plan generation with no situation details"""
        request = ActionPlanRequest(
            case_type="general",
            situation_details=None
        )
        
        response = self.service.generate_action_plan(request)
        assert response.total_steps > 0
    
    def test_case_type_normalization(self):
        """Test case type normalization (spaces to underscores, lowercase)"""
        request = ActionPlanRequest(
            case_type="False Accusation",  # With space and capital letters
            situation_details="Test"
        )
        
        response = self.service.generate_action_plan(request)
        # Should still work due to normalization
        assert response.total_steps > 0
    
    def test_all_steps_have_required_fields(self):
        """Test that all steps have all required fields"""
        request = ActionPlanRequest(case_type="harassment")
        response = self.service.generate_action_plan(request)
        
        required_fields = [
            "step_number", "title", "description", "timeline",
            "time_estimate", "urgency", "is_legal_deadline",
            "requires_professional", "alternatives"
        ]
        
        for step in response.steps:
            for field in required_fields:
                assert field in step, f"Missing field: {field}"
    
    def test_urgency_values_valid(self):
        """Test that urgency values are within valid range (1-10)"""
        request = ActionPlanRequest(case_type="false_accusation")
        response = self.service.generate_action_plan(request)
        
        for step in response.steps:
            assert 1 <= step["urgency"] <= 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
