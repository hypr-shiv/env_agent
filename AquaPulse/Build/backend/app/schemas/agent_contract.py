from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class AgentStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"
    CLARIFICATION_NEEDED = "clarification_needed"

class DataMode(str, Enum):
    LIVE = "live"
    HISTORICAL = "historical"
    MOCK = "mock"
    SYNTHETIC = "synthetic"

class SourceType(str, Enum):
    OFFICIAL_API = "official_api"
    CURATED_DATABASE = "curated_database"
    RAG_DOCUMENT = "rag_document"
    ML_MODEL = "ml_model"
    COMMUNITY_REPORT = "community_report"

class Coordinates(BaseModel):
    lat: float
    lng: float

class LocationInfo(BaseModel):
    name: str = "Palghar Coastal Zone"
    district: str = "Palghar"
    state: str = "Maharashtra"
    coordinates: Optional[Coordinates] = None

class EvidenceSource(BaseModel):
    source_name: str
    source_type: SourceType = SourceType.CURATED_DATABASE
    data_mode: DataMode = DataMode.LIVE
    url_or_ref: Optional[str] = None
    observation_time: Optional[datetime] = None
    retrieval_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 1.0

class AgentInput(BaseModel):
    query: str
    location: Optional[LocationInfo] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    attachments: Optional[List[Dict[str, Any]]] = None

class AgentOutput(BaseModel):
    agent_name: str
    status: AgentStatus = AgentStatus.SUCCESS
    summary: str
    data: Dict[str, Any] = Field(default_factory=dict)
    location: LocationInfo = Field(default_factory=LocationInfo)
    sources: List[EvidenceSource] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    needs_followup: bool = False
    followup_question: Optional[str] = None
    execution_time_ms: Optional[float] = None

