from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from app.orchestrator.graph import invoke_orchestrator

router = APIRouter(prefix="/chat", tags=["Multi-Agent Orchestrator"])

class ChatRequest(BaseModel):
    query: str = Field(..., description="User query in English or romanized Marathi")
    session_id: Optional[str] = Field(None, description="Client session identifier")
    location: Optional[Dict[str, Any]] = Field(default_factory=lambda: {"name": "Palghar", "district": "Palghar", "state": "Maharashtra"})
    attachments: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class AgentResultResponse(BaseModel):
    agent_name: str
    status: str
    answer: str
    source: Dict[str, Any]
    location: Dict[str, Any]
    timestamp: str
    confidence: float
    warnings: List[str]

class ChatResponse(BaseModel):
    user_query: str
    session_id: str
    intent: str
    target_agents: List[str]
    activated_agents: Optional[List[str]] = None
    final_answer: str
    final_response: Optional[str] = None
    agent_results: Dict[str, AgentResultResponse]
    sources: List[Dict[str, Any]]
    warnings: List[str]
    validation_passed: bool
    completed_at: str

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    """
    Main entrypoint for AquaPulse Multi-Agent LangGraph conversation.
    Routes to single or multiple specialist agents, validates results,
    and returns synthesized advisory.
    """
    try:
        state = invoke_orchestrator(
            query=payload.query,
            location=payload.location,
            session_id=payload.session_id,
            attachments=payload.attachments
        )

        formatted_results = {}
        for k, v in state.get("agent_results", {}).items():
            formatted_results[k] = AgentResultResponse(
                agent_name=v["agent_name"],
                status=v["status"],
                answer=v["answer"],
                source=v.get("source", {}),
                location=v.get("location", {}),
                timestamp=v["timestamp"],
                confidence=v.get("confidence", 1.0),
                warnings=v.get("warnings", [])
            )

        return ChatResponse(
            user_query=state["user_query"],
            session_id=state["session_id"],
            intent=state["intent"],
            target_agents=state["target_agents"],
            activated_agents=state["target_agents"],
            final_answer=state["final_answer"],
            final_response=state["final_answer"],
            agent_results=formatted_results,
            sources=state.get("sources", []),
            warnings=state.get("warnings", []),
            validation_passed=state.get("validation_passed", True),
            completed_at=state.get("completed_at", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration failure: {str(e)}")

