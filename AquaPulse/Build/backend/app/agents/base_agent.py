from abc import ABC, abstractmethod
import time
import traceback
from typing import Optional, Dict, Any
from app.schemas.agent_contract import AgentInput, AgentOutput, AgentStatus, LocationInfo, EvidenceSource, DataMode

class BaseAgent(ABC):
    """
    Standard Base Agent Contract for all AquaPulse specialist agents:
    1. Weather
    2. Fisheries
    3. Disaster
    4. Market
    5. Environment
    6. Government Scheme
    7. Complaint
    """
    def __init__(self, agent_name: str, description: str):
        self.agent_name = agent_name
        self.description = description

    @abstractmethod
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Domain-specific logic for the specialist agent."""
        pass

    async def run_agent(
        self,
        query: str,
        location: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        attachments: Optional[list] = None
    ) -> AgentOutput:
        """
        Public execution wrapper with timing, input normalization, and defensive error boundary.
        """
        start_time = time.perf_counter()
        
        # Normalize location
        loc_obj = LocationInfo()
        if location:
            try:
                loc_obj = LocationInfo(**location)
            except Exception:
                pass

        agent_input = AgentInput(
            query=query,
            location=loc_obj,
            context=context or {},
            attachments=attachments or []
        )

        try:
            output = await self.process(agent_input)
            output.execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return output
        except Exception as e:
            execution_time = round((time.perf_counter() - start_time) * 1000, 2)
            return AgentOutput(
                agent_name=self.agent_name,
                status=AgentStatus.ERROR,
                summary=f"Error executing {self.agent_name}: {str(e)}",
                location=loc_obj,
                warnings=[f"Internal agent exception: {str(e)}", traceback.format_exc()],
                execution_time_ms=execution_time
            )

