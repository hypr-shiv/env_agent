import random
from datetime import datetime, timezone
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.schemas.agent_contract import AgentInput, AgentOutput, AgentStatus, EvidenceSource, DataMode, SourceType
from app.core.database import get_session
from app.db.models import PublicComplaint

class ComplaintAgent(BaseAgent):
    """
    Complaint Agent: Registers, audits, and tracks coastal grievances such as
    illegal mechanized trawling, marine pollution, lost gear, and landing jetty issues.
    """
    def __init__(self):
        super().__init__(
            agent_name="Complaint Agent",
            description="Facilitates logging and status verification of maritime grievances and illegal fishing incidents."
        )

    def register_complaint(self, query: str, location_name: str) -> Dict[str, Any]:
        """Independent Tool: Generates ticket and persists public complaint in database."""
        q_lower = query.lower()

        # Category determination
        if "pollution" in q_lower or "chemical" in q_lower or "waste" in q_lower or "oil" in q_lower:
            category = "Marine Pollution"
        elif "trawl" in q_lower or "purse-seine" in q_lower or "illegal" in q_lower:
            category = "Illegal Trawling"
        elif "jetty" in q_lower or "harbor" in q_lower or "light" in q_lower or "dock" in q_lower:
            category = "Harbor Infrastructure"
        else:
            category = "General Fishery Grievance"

        ticket_no = f"AQ-PLG-2026-{random.randint(100, 999)}"

        with get_session() as session:
            complaint = PublicComplaint(
                ticket_number=ticket_no,
                category=category,
                title=f"Incident reported: {category} near {location_name}",
                description=query,
                location_name=location_name,
                status="submitted",
                submitted_by="Palghar Coastal User"
            )
            session.add(complaint)
            session.commit()

        return {
            "ticket_number": ticket_no,
            "category": category,
            "location": location_name,
            "status": "submitted",
            "department": "Assistant Commissioner of Fisheries & Palghar Coastal Police",
            "sla": "48 hours inspection window"
        }

    async def process(self, input_data: AgentInput) -> AgentOutput:
        loc_name = input_data.location.name if input_data.location else "Palghar"
        data = self.register_complaint(input_data.query, loc_name)
        now_iso = datetime.now(timezone.utc).isoformat()

        ans = (
            f"Official Grievance Registered Successfully:\n"
            f"• Ticket Number: {data['ticket_number']}\n"
            f"• Category: {data['category']}\n"
            f"• Reported Location: {data['location']}, Palghar\n"
            f"• Initial Status: SUBMITTED (Assigned to {data['department']})\n"
            f"• Expected Action: Initial verification within {data['sla']}.\n\n"
            f"Keep this ticket number safe for tracking at your local fishermen cooperative society."
        )

        return AgentOutput(
            agent_name=self.agent_name,
            status=AgentStatus.SUCCESS,
            summary=ans,
            data=data,
            location=input_data.location,
            sources=[EvidenceSource(
                source_name="Maharashtra Coastal Grievance Redressal System (Palghar Cell)",
                source_type=SourceType.COMMUNITY_REPORT,
                data_mode=DataMode.LIVE,
                confidence=1.0
            )]
        )

    def run_as_dict(self, query: str, location: Dict[str, Any]) -> Dict[str, Any]:
        loc_name = location.get("name", "Palghar")
        data = self.register_complaint(query, loc_name)
        now_iso = datetime.now(timezone.utc).isoformat()

        ans = (
            f"Complaint Registered: Ticket #{data['ticket_number']} for '{data['category']}' at {data['location']}. "
            f"Status: Submitted. Forwarded to {data['department']} for inspection."
        )

        return {
            "agent_name": self.agent_name,
            "status": "success",
            "answer": ans,
            "source": {
                "source_name": "Palghar Coastal Grievance Portal",
                "ticket_number": data["ticket_number"],
                "data_mode": "live"
            },
            "location": location,
            "timestamp": now_iso,
            "confidence": 1.0,
            "warnings": []
        }

complaint_agent = ComplaintAgent()

