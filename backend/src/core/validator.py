"""
Validator - Validate IR and ShotPlan
"""

from typing import Dict, Any, Tuple, List, Optional

class Validator:
    """
    Validate Intermediate Representation and Shot Plan
    """
    
    def validate_parameters(
        self,
        ir: Dict[str, Any],
        shot_plan: Dict[str, Any],
        quality_mode: str,
    ) -> Tuple[bool, List[str]]:
        """
        Validate generation parameters
        
        Args:
            ir: Intermediate Representation
            shot_plan: Shot Plan
            quality_mode: Quality mode
            
        Returns:
            Tuple of (is_valid, list of suggestions/errors)
        """
        suggestions = []
        
        # Validate duration
        total_duration = shot_plan.get("duration_s", 0)
        if total_duration > 60:
            suggestions.append("Total duration exceeds 60 seconds limit")
            
        # Validate shot count
        shots = shot_plan.get("shots", [])
        if len(shots) > 10:
            suggestions.append("Shot count exceeds 10 shots limit")
            
        # Validate quality mode
        if quality_mode not in ["fast", "balanced", "high"]:
            suggestions.append(f"Invalid quality mode: {quality_mode}")
            
        return len(suggestions) == 0, suggestions
        
    def validate_refinement(
        self,
        feedback: str,
        targeted_fields: List[str],
    ) -> Tuple[bool, str]:
        """
        Validate revision feedback
        
        Args:
            feedback: User feedback string
            targeted_fields: Identified fields to modify
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not feedback or len(feedback.strip()) < 2:
            return False, "Feedback is too short"
            
        if len(feedback) > 500:
            return False, "Feedback exceeds 500 characters"
            
        return True, ""
