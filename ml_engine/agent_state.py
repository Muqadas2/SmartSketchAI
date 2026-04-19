from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Annotated, Any
from typing_extensions import TypedDict
import operator

class SuspectProfile(BaseModel):
    """Structured representation of a suspect's facial features"""
    gender: str = Field(default="unknown", description="Gender of the suspect")
    age_range: str = Field(default="unknown", description="Estimated age range")
    ethnicity: str = Field(default="unknown", description="Estimated ethnicity")
    face_shape: str = Field(default="neutral", description="Shape of the face (oval, square, etc.)")
    
    # Eyes
    eye_color: str = Field(default="neutral", description="Color of the eyes")
    eye_shape: str = Field(default="neutral", description="Shape/set of the eyes")
    eyebrows: str = Field(default="neutral", description="Style of eyebrows")
    
    # Hair
    hair_style: str = Field(default="neutral", description="Style of head hair")
    hair_color: str = Field(default="neutral", description="Color of head hair")
    facial_hair: str = Field(default="none", description="Beard, mustache, etc.")
    
    # Other features
    nose_type: str = Field(default="neutral", description="Shape of the nose")
    mouth_type: str = Field(default="neutral", description="Shape of the lips/mouth")
    distinctive_features: List[str] = Field(default_factory=list, description="Scars, moles, tattoos, glasses")
    
    def to_detailed_prompt(self) -> str:
        """Convert the structured profile into a descriptive prompt string for SDXL"""
        parts = []
        if self.gender != "unknown": parts.append(f"a {self.gender}")
        if self.age_range != "unknown": parts.append(f"aged {self.age_range}")
        if self.ethnicity != "unknown": parts.append(f"of {self.ethnicity} ethnicity")
        
        parts.append(f"with {self.face_shape} face shape")
        parts.append(f"{self.eye_color} {self.eye_shape} eyes")
        parts.append(f"{self.hair_color} {self.hair_style} hair")
        
        if self.facial_hair != "none":
            parts.append(f"having {self.facial_hair}")
            
        parts.append(f"a {self.nose_type} nose")
        
        if self.distinctive_features:
            features_str = ", ".join(self.distinctive_features)
            parts.append(f"distinctive features: {features_str}")
            
        return ", ".join(parts)

class ForensicAgentState(TypedDict):
    """The shared state of the LangGraph Agent"""
    # Messages use the operator.add reducer to keep a running history
    messages: Annotated[List[Any], operator.add]
    
    # The structured profile
    suspect_profile: SuspectProfile
    
    # Current visual state
    current_image: Optional[Any]  # PIL Image or path
    generation_id: Optional[str]
    
    # Control flags
    next_step: str  # 'generate', 'edit', 'inpaint', 'end'
    last_error: Optional[str]
    iteration_count: int
