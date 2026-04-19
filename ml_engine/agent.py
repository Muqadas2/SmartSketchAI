from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from .agent_state import ForensicAgentState, SuspectProfile
from .agent_nodes import AnalyzerNode, RouterNode, VerificationNode

class SmartSketchAgent:
    """
    Assembled LangGraph Agent for SmartSketch forensic workflow
    """
    def __init__(self, llm=None, pipeline=None):
        self.llm = llm
        self.pipeline = pipeline
        
        # Initialize nodes
        self.analyzer = AnalyzerNode(llm=llm)
        self.router = RouterNode()
        self.verifier = VerificationNode(scorer=pipeline.scorer if pipeline else None)
        
        # Build Graph
        self.workflow = StateGraph(ForensicAgentState)
        
        # Add Nodes
        self.workflow.add_node("analyze", self.analyzer)
        self.workflow.add_node("route", self.router)
        self.workflow.add_node("artist", self._artist_node)
        self.workflow.add_node("verify", self.verifier)
        
        # Define Edges
        self.workflow.set_entry_point("analyze")
        self.workflow.add_edge("analyze", "route")
        
        # Conditional Edge from Router
        self.workflow.add_conditional_edges(
            "route",
            lambda x: x["next_step"],
            {
                "inpaint": "artist",
                "edit": "artist",
                "generate": "artist"
            }
        )
        
        # Edge from Artist to Verify
        self.workflow.add_edge("artist", "verify")
        
        # Conditional Edge from Verify (The Self-Correction Loop)
        self.workflow.add_conditional_edges(
            "verify",
            lambda x: x["next_step"],
            {
                "retry": "artist",
                "end": END
            }
        )
        
        # Compile with checkpointer
        self.memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.memory)

    def _artist_node(self, state: ForensicAgentState) -> Dict[str, Any]:
        """Node that calls the actual ML Pipeline"""
        print(f"\n--- ML ARTIST EXECUTING: {state['next_step'].upper()} ---")
        
        if self.pipeline is None:
            print("[Artist] Mocking image generation...")
            return {"current_image": "mock_image_data", "generation_id": "gen_123"}
            
        # Real pipeline call logic based on state['next_step']
        # This will be refined as we link to the real pipeline
        return {"current_image": "real_image_data"}

    def run(self, message: str, thread_id: str = "default"):
        """Run a single turn of the agent"""
        config = {"configurable": {"thread_id": thread_id}}
        
        # Initial state if thread is new
        # Note: LangGraph handles initial state via the config/thread_id
        
        inputs = {
            "messages": [message],
            "suspect_profile": SuspectProfile(),
            "iteration_count": 0,
            "next_step": "analyze"
        }
        
        final_state = self.app.invoke(inputs, config)
        return final_state
