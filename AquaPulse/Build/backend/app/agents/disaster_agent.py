from datetime import datetime, timezone
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.schemas.agent_contract import AgentInput, AgentOutput, AgentStatus, EvidenceSource, DataMode, SourceType
from app.core.database import get_session
from app.db.models import DisasterAlertRecord

class DisasterAgent(BaseAgent):
    """
    Disaster Agent: High-priority early warning system for cyclones,
    high-swell surge alerts, tsunamis, and coastal evacuation protocols.
    """
    def __init__(self):
        super().__init__(
            agent_name="Disaster Agent",
            description="Monitors IMD/INCOIS cyclone warnings, storm surges, and emergency helplines for Palghar coast."
        )

    def get_active_alerts(self, location_name: str) -> List[Dict[str, Any]]:
        """Independent Tool: Queries active disaster alerts for Palghar district."""
        with get_session() as session:
            alerts = session.query(DisasterAlertRecord).filter(
                DisasterAlertRecord.is_active == True
            ).all()

            results = []
            for a in alerts:
                results.append({
                    "title": a.title,
                    "alert_type": a.alert_type,
                    "severity": a.severity,
                    "description": a.description,
                    "affected_locations": a.affected_locations,
                    "emergency_helpline": a.emergency_helpline,
                    "source": a.source,
                    "issued_at": a.issued_at.isoformat() if a.issued_at else None
                })
            return results

    async def process(self, input_data: AgentInput) -> AgentOutput:
        loc_name = input_data.location.name if input_data.location else "Palghar"
        alerts = self.get_active_alerts(loc_name)
        now_iso = datetime.now(timezone.utc).isoformat()

        if not alerts:
            ans = (
                f"Disaster & Coastal Safety Status for {loc_name}:\n"
                f"• Active Warnings: NO CYCLONE OR STORM SURGE WARNINGS CURRENTLY ACTIVE.\n"
                f"• Coastal Alert Status: GREEN (Normal conditions).\n"
                f"• Palghar Emergency Helpline: 1077 (District Disaster Management Cell, 24x7)."
            )
            return AgentOutput(
                agent_name=self.agent_name,
                status=AgentStatus.SUCCESS,
                summary=ans,
                data={"active_alerts": []},
                location=input_data.location,
                sources=[EvidenceSource(
                    source_name="India Meteorological Department (IMD) / INCOIS Disaster Watch",
                    source_type=SourceType.OFFICIAL_API,
                    data_mode=DataMode.LIVE,
                    confidence=0.98
                )]
            )

        alert = alerts[0]
        ans = (
            f"⚠️ Coastal Safety Advisory: {alert['title']}\n"
            f"• Alert Level: {alert['severity'].upper()} ({alert['alert_type']})\n"
            f"• Advisory: {alert['description']}\n"
            f"• Affected Zones: {', '.join(alert.get('affected_locations', ['Palghar Coastal Belt']))}\n"
            f"• Emergency Contact: {alert.get('emergency_helpline', '1077 (Palghar Control Room)')}"
        )

        return AgentOutput(
            agent_name=self.agent_name,
            status=AgentStatus.SUCCESS,
            summary=ans,
            data={"active_alerts": alerts},
            location=input_data.location,
            sources=[EvidenceSource(
                source_name=alert.get("source", "INCOIS ESSO Early Warning System"),
                source_type=SourceType.OFFICIAL_API,
                data_mode=DataMode.LIVE,
                confidence=0.99
            )],
            warnings=[f"Active {alert['severity']} warning: {alert['title']}"]
        )

    def run_as_dict(self, query: str, location: Dict[str, Any]) -> Dict[str, Any]:
        loc_name = location.get("name", "Palghar")
        alerts = self.get_active_alerts(loc_name)
        now_iso = datetime.now(timezone.utc).isoformat()

        if not alerts:
            return {
                "agent_name": self.agent_name,
                "status": "success",
                "answer": (
                    f"No active cyclone or severe storm warnings for {loc_name}. "
                    f"Coastal Status: GREEN (Normal). Palghar Emergency Helpline: 1077."
                ),
                "source": {"source_name": "IMD / INCOIS Disaster Watch", "data_mode": "live"},
                "location": location,
                "timestamp": now_iso,
                "confidence": 0.98,
                "warnings": []
            }

        top = alerts[0]
        return {
            "agent_name": self.agent_name,
            "status": "success",
            "answer": (
                f"Alert [{top['severity'].upper()}]: {top['title']}. {top['description']} "
                f"Emergency Control: {top['emergency_helpline']}."
            ),
            "source": {"source_name": top.get("source", "INCOIS / IMD"), "data_mode": "live"},
            "location": location,
            "timestamp": now_iso,
            "confidence": 0.99,
            "warnings": [f"{top['alert_type']} ({top['severity']}) in effect"]
        }

disaster_agent = DisasterAgent()

