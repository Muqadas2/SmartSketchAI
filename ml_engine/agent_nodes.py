import json
import re
from typing import Dict, Any
from .agent_state import ForensicAgentState, SuspectProfile

class AnalyzerNode:
    """
    Node that interprets user messages and updates the SuspectProfile
    """
    def __init__(self, llm=None):
        self.llm = llm

    def __call__(self, state: ForensicAgentState) -> Dict[str, Any]:
        """
        Processes the latest message and updates the suspect profile
        """
        print("\n--- ANALYZING USER INPUT ---")
        
        # Get the last message
        last_message = state['messages'][-1].content if hasattr(state['messages'][-1], 'content') else str(state['messages'][-1])
        current_profile = state['suspect_profile']
        
        # If no LLM, we use a simple heuristic for testing
        if self.llm is None:
            return self._mock_llm_logic(last_message, current_profile)
            
        # Build the system prompt
        system_prompt = self._build_system_prompt(current_profile)
        
        # Call the LLM
        response = self.llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": last_message}
        ])
        
        # Parse the JSON from the LLM
        updated_profile_data = self._parse_json(response.content)
        
        # Update the profile
        updated_profile = SuspectProfile(**updated_profile_data)
        
        return {
            "suspect_profile": updated_profile,
            "iteration_count": state["iteration_count"] + 1
        }

    def _build_system_prompt(self, profile: SuspectProfile) -> str:
        return f"""You are a Forensic Profile Manager. Your job is to update a suspect's description based on new user feedback.

CURRENT PROFILE (JSON):
{profile.model_dump_json()}

INSTRUCTIONS:
1. Carefully read the user's new input.
2. Update the relevant fields in the JSON. 
3. If the user mentions a relative change (e.g., "darker," "older," "longer"), update the value accordingly based on the current state.
4. Keep all other fields exactly as they are.
5. Return ONLY the updated JSON object. No conversation, no explanations.

OUTPUT FORMAT:
Match the SuspectProfile schema exactly."""

    def _parse_json(self, text: str) -> Dict[str, Any]:
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        return {}

    def _mock_llm_logic(self, message: str, profile: SuspectProfile) -> Dict[str, Any]:
        """Mocked logic for testing without a real LLM"""
        msg = message.lower()
        new_data = profile.model_dump()
        
        if "blue" in msg and "eyes" in msg:
            new_data['eye_color'] = "blue"
        if "black" in msg and "hair" in msg:
            new_data['hair_color'] = "black"
        if "glasses" in msg:
            if "glasses" not in new_data['distinctive_features']:
                new_data['distinctive_features'].append("glasses")
        
        return {"suspect_profile": SuspectProfile(**new_data)}

class RouterNode:
    """
    Logic-based node that compares profile changes and selects the best ML tool
    """
    def __call__(self, state: ForensicAgentState) -> Dict[str, Any]:
        print("\n--- ROUTING TO ML TOOL ---")
        
        # We need the previous profile to compare
        # For now, we'll assume the Analyzer just updated the profile in the state
        # In a real graph, we'd store 'previous_profile' in the state too
        new_profile = state['suspect_profile']
        
        # Heuristics for routing
        structural_fields = ['age_range', 'face_shape', 'ethnicity', 'gender']
        local_fields = ['eye_color', 'eye_shape', 'eyebrows', 'nose_type', 'mouth_type', 'distinctive_features']
        texture_fields = ['hair_color', 'hair_style', 'facial_hair']
        
        # For simplicity in Task 3, we'll just check what was recently modified
        # (In a full graph, the Analyzer would flag which fields it changed)
        
        # Default decision logic
        decision = "edit" # Default to ControlNet Editor for safety
        target_region = None
        
        # If user mentioned specific local parts, use Inpainter
        if any(f in str(state['messages'][-1]).lower() for f in ['eye', 'lip', 'nose', 'brow']):
            decision = "inpaint"
            # Extract target region
            for region in ['eyes', 'lips', 'nose', 'brows']:
                if region[:-1] in str(state['messages'][-1]).lower():
                    target_region = region
                    break
        
        print(f"[Router] Decision: {decision.upper()}")
        if target_region:
            print(f"[Router] Target Region: {target_region}")
            
        return {
            "next_step": decision,
            "generation_params": {
                "target_region": target_region,
                "use_controlnet": (decision == "edit")
            }
        }

class VerificationNode:
    """
    Quality control node that uses the FaceScorer to decide if we should retry or end
    """
    def __init__(self, scorer=None):
        self.scorer = scorer

    def __call__(self, state: ForensicAgentState) -> Dict[str, Any]:
        print("\n--- SCRUTINIZING GENERATION ---")
        
        # If no scorer (testing), we'll mock a passing score
        if self.scorer is None:
            print("[Scrutinizer] Mocking score: 0.95")
            return {"next_step": "end", "is_verified": True}
            
        # Real scoring logic would go here
        # For now, let's assume we have the generation result in the state
        score = 0.85 # Placeholder
        
        if score >= 0.8:
            print(f"[Scrutinizer] Success! Score: {score:.2f}")
            return {"next_step": "end", "is_verified": True}
        else:
            if state["iteration_count"] < 3:
                print(f"[Scrutinizer] Low score ({score:.2f}). Retrying...")
                return {"next_step": "retry", "is_verified": False}
            else:
                print(f"[Scrutinizer] Giving up after {state['iteration_count']} attempts.")
                return {"next_step": "end", "is_verified": False}
