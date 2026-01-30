"""
Prompt Compiler - Compile Wan2.6 prompts from ShotPlan
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel

class CompiledPrompt(BaseModel):
    compiled_prompt: str
    compiled_negative_prompt: str
    params: Dict[str, Any]

class PromptCompiler:
    """
    Compile high-level shot descriptions into low-level Wan2.6 prompts
    """
    
    def compile_shot_prompt(
        self,
        shot: Dict[str, Any],
        shot_plan: Dict[str, Any],
        ir: Dict[str, Any],
        negative_prompt_base: str = "",
        prompt_extend: bool = False,
    ) -> CompiledPrompt:
        """
        Compile a single shot prompt
        
        Args:
            shot: Shot dictionary
            shot_plan: Full shot plan
            ir: Intermediate Representation
            negative_prompt_base: Base negative prompt from template
            prompt_extend: Whether to enable prompt extension
            
        Returns:
            CompiledPrompt object
        """
        # Extract components
        visual = shot.get("visual_prompt", "") or shot.get("visual", "")
        camera = shot.get("camera", "")
        lighting = shot.get("lighting", "")
        style = ir.get("style", {}).get("visual", "")
        
        # Construct prompt
        # Format: [Visual Description], [Camera Movement], [Lighting], [Style]
        components = [visual]
        if camera:
            components.append(f"Camera: {camera}")
        if lighting:
            components.append(f"Lighting: {lighting}")
        if style:
            components.append(f"Style: {style}")
            
        final_prompt = ", ".join([c for c in components if c])
        
        # Construct parameters
        params = {
            "size": "1280*720", # Default, should come from config
            "duration": shot.get("duration_s", 5),
            "seed": shot.get("seed", 12345), # Should be randomized if not set
            "prompt_extend": prompt_extend,
            "watermark": False,
        }
        
        return CompiledPrompt(
            compiled_prompt=final_prompt,
            compiled_negative_prompt=negative_prompt_base,
            params=params,
        )
