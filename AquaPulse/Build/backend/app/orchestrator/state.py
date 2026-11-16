from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime

class StructuredAgentResult(TypedDict, total=False):
    agent_name: str
    status: str            # "success" | "partial" | "error" | "clarification_needed"
    answer: str
    source: Dict[str, Any] # source_name, data_mode, retrieval_time, url
    location: Dict[str, Any]
    timestamp: str
    confidence: float
    warnings: List[str]

class AquaPulseState(TypedDict, total=False):
    """
    Central shared state for AquaPulse LangGraph Multi-Agent Orchestrator.
    """
    # Request Info
    user_query: str
    session_id: str
    location: Dict[str, Any] # {"name": "Palghar", "district": "Palghar", "state": "Maharashtra"}
    attachments: List[Dict[str, Any]]
    
    # Routing & Intent
    intent: str
    target_agents: List[str] # ["weather"], ["fisheries", "market"], etc.
    routing_reasoning: str
    
    # Agent Execution Results
    agent_results: Dict[str, StructuredAgentResult]
    executed_agents: List[str]
    
    # Validation & Quality Checks
    validation_passed: bool
    validation_notes: List[str]
    retry_count: int
    execution_limit: int
    
    # Final Output
    final_answer: str
    sources: List[Dict[str, Any]]
    warnings: List[str]
    error_message: Optional[str]
    
    # Tracing
    created_at: str
    completed_at: Optional[str]
    total_execution_ms: Optional[float]

