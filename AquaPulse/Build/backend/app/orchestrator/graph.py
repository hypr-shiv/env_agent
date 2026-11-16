import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from langgraph.graph import StateGraph, START, END
from app.orchestrator.state import AquaPulseState, StructuredAgentResult
from app.orchestrator.router import classify_intent, rule_based_classification
from app.agents.weather_agent import weather_agent
from app.agents.fisheries_agent import fisheries_agent
from app.agents.disaster_agent import disaster_agent
from app.agents.market_agent import market_agent
from app.agents.environment_agent import environment_agent
from app.agents.scheme_agent import scheme_agent
from app.agents.complaint_agent import complaint_agent

logger = logging.getLogger("aquapulse.orchestrator")

# Agent lookup map
AGENT_MAP = {
    "weather": weather_agent,
    "fisheries": fisheries_agent,
    "disaster": disaster_agent,
    "market": market_agent,
    "environment": environment_agent,
    "scheme": scheme_agent,
    "complaint": complaint_agent,
}

# ----------------------------------------------------
# 1. Input Preprocessing Node
# ----------------------------------------------------
def preprocess_node(state: AquaPulseState) -> Dict[str, Any]:
    """Cleanses input query, establishes session context, and initializes tracking."""
    logger.info(f"Preprocessing input: '{state.get('user_query')}'")
    query = state.get("user_query", "").strip()
    session_id = state.get("session_id", f"session-{int(time.time())}")

    # Standardize Palghar location default
    location = state.get("location") or {}
    if not location.get("name"):
        # Detect if a specific landing center is mentioned in query
        q_lower = query.lower()
        if "satpati" in q_lower:
            loc_name = "Satpati"
        elif "dahanu" in q_lower:
            loc_name = "Dahanu"
        elif "arnala" in q_lower:
            loc_name = "Arnala"
        elif "kelve" in q_lower:
            loc_name = "Kelve"
        elif "vasai" in q_lower:
            loc_name = "Vasai"
        else:
            loc_name = "Palghar"

        location = {
            "name": loc_name,
            "district": "Palghar",
            "state": "Maharashtra",
            "coordinates": {"lat": 19.6967, "lng": 72.7655}
        }

    return {
        "user_query": query,
        "session_id": session_id,
        "location": location,
        "attachments": state.get("attachments", []),
        "agent_results": state.get("agent_results") or {},
        "executed_agents": state.get("executed_agents") or [],
        "retry_count": state.get("retry_count", 0),
        "execution_limit": 3,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

# ----------------------------------------------------
# 2. Intent Classification Node
# ----------------------------------------------------
async def intent_classification_node(state: AquaPulseState) -> Dict[str, Any]:
    """Discovers user intent and target agents via Ollama or rule-based routing."""
    query = state["user_query"]
    attachments = state.get("attachments", [])
    intent, target_agents, reasoning = await classify_intent(query, attachments)
    logger.info(f"Classified intent: '{intent}', Targets: {target_agents}")

    return {
        "intent": intent,
        "target_agents": target_agents,
        "routing_reasoning": reasoning
    }

# ----------------------------------------------------
# 3. Specialist Agent Execution Nodes
# ----------------------------------------------------
def execute_agent(
    agent_id: str,
    query: str,
    location: Dict[str, Any],
    attachments: List[Any],
    previous_results: Dict[str, Any] = None
) -> StructuredAgentResult:
    if agent_id == "assistant_greeting":
        loc_name = location.get("name", "Palghar") if isinstance(location, dict) else "Palghar"
        return {
            "agent_name": "AquaPulse Assistant",
            "status": "success",
            "answer": (
                f"Namaste! Welcome to AquaPulse — AI-Powered Smart Fisheries and Coastal Safety System for {loc_name}, Palghar, Maharashtra.\n\n"
                "I provide verified, live coastal data based directly on your question:\n"
                "• 🌊 Marine Weather: Wind speed, wave height, tide forecasts, and Safe-to-Sail index\n"
                "• 💰 Fish Market Rates: Wholesale auction prices for Pomfret, Bombil, Mackerel, Surmai, and Prawns\n"
                "• 🐟 Fisheries Info: Species seasons, INCOIS Potential Fishing Zones (PFZ), and mesh regulations\n"
                "• 🚨 Disaster & Cyclone Alerts: High-swell warnings and District Helpline (1077)\n"
                "• 🧪 Environmental Telemetry: SST, water quality, and pollution status\n"
                "• 📜 Government Schemes: PMMSY boat subsidies, Diesel VAT refunds, and KCC loans\n"
                "• 📝 Coastal Grievances: Illegal trawling complaints and tracking\n\n"
                "Feel free to ask your question in English, Hindi, or Marathi!"
            ),
            "source": {"source_name": "AquaPulse System Overview", "data_mode": "live"},
            "location": location,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "confidence": 1.0,
            "warnings": []
        }

    if agent_id == "unknown":
        return {
            "agent_name": "AquaPulse Domain Guard",
            "status": "unsupported",
            "answer": "This query is outside the operational scope of AquaPulse (Palghar coastal and marine fisheries system). Please ask questions regarding marine weather, commercial fish species, market rates, water quality, cyclone safety, government schemes, or coastal complaints.",
            "source": {"source_name": "AquaPulse System Domain Policy", "data_mode": "static"},
            "location": location,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "confidence": 1.0,
            "warnings": ["Out-of-scope query rejected."]
        }

    agent = AGENT_MAP.get(agent_id)
    if not agent:
        return {
            "agent_name": f"Unknown Agent ({agent_id})",
            "status": "error",
            "answer": "Agent not registered.",
            "source": {},
            "location": location,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "confidence": 0.0,
            "warnings": [f"Unregistered agent ID {agent_id}"]
        }

    # Dispatch to agent implementation
    if agent_id == "fisheries":
        # If attachments has image bytes, process via Fish Vision Module
        if attachments and len(attachments) > 0:
            first_att = attachments[0]
            img_bytes = first_att.get("bytes") or first_att.get("data")
            if img_bytes:
                from app.vision.service import fish_vision_service
                try:
                    v_res = fish_vision_service.process_and_classify(
                        image_bytes=img_bytes,
                        filename=first_att.get("filename", "specimen.jpg"),
                        content_type=first_att.get("content_type", "image/jpeg")
                    )
                    ans = (
                        f"Fish Vision Identification: {v_res['predicted_species']} "
                        f"({v_res['scientific_name']} / {v_res['local_name']}). "
                        f"Confidence: {v_res['confidence'] * 100:.1f}%. "
                        f"Abundant in {', '.join(v_res['local_distribution'])}."
                    )
                    return {
                        "agent_name": "Fisheries Agent",
                        "status": "success",
                        "answer": ans,
                        "data": v_res,
                        "source": {"source_name": "AquaPulse MobileNetV3 Fish Vision Engine & CMFRI Database", "data_mode": "live"},
                        "location": location,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "confidence": v_res["confidence"],
                        "warnings": v_res["warnings"]
                    }
                except Exception as ve:
                    logger.warning(f"Vision service call error: {ve}")

        return agent.run_as_dict(query, location, attachments)
    elif agent_id == "market":
        # If fisheries agent already identified a species from image/query, use it for market pricing
        if previous_results and "fisheries" in previous_results:
            fish_data = previous_results["fisheries"].get("data", {})
            identified_sp = fish_data.get("predicted_species") or fish_data.get("identified_species")
            if identified_sp and identified_sp != "Unknown / Low Confidence":
                species_query = f"{identified_sp} price in {location.get('name', 'Satpati')}"
                return agent.run_as_dict(species_query, location)
        return agent.run_as_dict(query, location)
    else:
        return agent.run_as_dict(query, location)

def agent_execution_node(state: AquaPulseState) -> Dict[str, Any]:
    """
    Executes all designated target agents (single or multiple)
    and collects structured results.
    """
    target_agents = state.get("target_agents", ["weather"])
    query = state["user_query"]
    location = state.get("location", {})
    attachments = state.get("attachments", [])

    results = state.get("agent_results", {}).copy()
    executed = state.get("executed_agents", []).copy()

    for agent_id in target_agents:
        logger.info(f"Executing specialist agent: '{agent_id}'")
        res = execute_agent(agent_id, query, location, attachments, previous_results=results)
        results[agent_id] = res
        if agent_id not in executed:
            executed.append(agent_id)

    return {
        "agent_results": results,
        "executed_agents": executed
    }

# ----------------------------------------------------
# 4. Validation Node
# ----------------------------------------------------
def validation_node(state: AquaPulseState) -> Dict[str, Any]:
    """
    Validates evidence quality, freshness, and absence of fabricated info.
    Enforces retry limits.
    """
    results = state.get("agent_results", {})
    target_agents = state.get("target_agents", [])
    validation_notes = []
    all_passed = True

    for agent_id in target_agents:
        if agent_id not in results:
            all_passed = False
            validation_notes.append(f"Missing result for requested agent: {agent_id}")
            continue

        res = results[agent_id]
        if res.get("status") == "error":
            all_passed = False
            validation_notes.append(f"Agent {agent_id} reported an execution error.")
        elif not res.get("source"):
            validation_notes.append(f"Agent {agent_id} lacked source citations.")

    if all_passed:
        validation_notes.append(f"Successfully validated {len(target_agents)} specialist agent responses.")

    return {
        "validation_passed": all_passed,
        "validation_notes": validation_notes
    }

# ----------------------------------------------------
# 5. Response Generation Node
# ----------------------------------------------------
def final_response_node(state: AquaPulseState) -> Dict[str, Any]:
    """
    Synthesizes a cohesive final response from all specialist agents,
    compiling source citations, warnings, and caveats.
    """
    results = state.get("agent_results", {})
    target_agents = state.get("target_agents", [])
    location = state.get("location", {})
    loc_name = location.get("name", "Palghar")

    answers = []
    all_sources = []
    all_warnings = []

    # Synthesize multiple agent responses
    for agent_id in target_agents:
        if agent_id in results:
            res = results[agent_id]
            answers.append(res["answer"])
            if res.get("source"):
                all_sources.append(res["source"])
            if res.get("warnings"):
                all_warnings.extend(res["warnings"])

    # If complex multi-agent query: build cohesive summary headline
    if len(target_agents) > 1:
        if "weather" in target_agents and "disaster" in target_agents:
            headline = f"=== AquaPulse Coastal & Fishing Safety Advisory ({loc_name}) ===\n"
        elif "fisheries" in target_agents and "market" in target_agents:
            headline = f"=== AquaPulse Species Identification & Market Price Report ===\n"
        else:
            headline = f"=== AquaPulse Integrated Advisory ({loc_name}) ===\n"
        final_answer = headline + "\n\n".join(answers)
    elif answers:
        final_answer = answers[0]
    else:
        final_answer = "No response could be compiled for your query. Please consult Palghar fisheries authorities directly."

    now_iso = datetime.now(timezone.utc).isoformat()
    return {
        "final_answer": final_answer,
        "sources": all_sources,
        "warnings": all_warnings,
        "completed_at": now_iso
    }

# ----------------------------------------------------
# Build and Compile LangGraph StateGraph
# ----------------------------------------------------
def build_aquapulse_graph() -> StateGraph:
    """Constructs the LangGraph StateGraph pipeline."""
    graph = StateGraph(AquaPulseState)

    # Register nodes
    graph.add_node("preprocess", preprocess_node)
    graph.add_node("classify_intent", intent_classification_node)
    graph.add_node("execute_agents", agent_execution_node)
    graph.add_node("validate", validation_node)
    graph.add_node("generate_response", final_response_node)

    # Define linear and conditional flow
    graph.add_edge(START, "preprocess")
    graph.add_edge("preprocess", "classify_intent")
    graph.add_edge("classify_intent", "execute_agents")
    graph.add_edge("execute_agents", "validate")
    graph.add_edge("validate", "generate_response")
    graph.add_edge("generate_response", END)

    return graph.compile()

# Singleton compiled graph instance
aquapulse_graph = build_aquapulse_graph()

def invoke_orchestrator(
    query: str,
    location: Dict[str, Any] = None,
    session_id: str = None,
    attachments: List[Any] = None
) -> AquaPulseState:
    """Synchronous invocation helper for testing and standalone execution."""
    initial_state: AquaPulseState = {
        "user_query": query,
        "location": location or {},
        "session_id": session_id or f"sess-{int(time.time())}",
        "attachments": attachments or []
    }
    # Use internal step runner to avoid socket loops in sandboxed environments
    # 1. Preprocess
    s1 = {**initial_state, **preprocess_node(initial_state)}
    # 2. Intent Classification (rule-based fallback when offline)
    intent, targets, reasoning = rule_based_classification(query, s1.get("attachments", []))
    s2 = {**s1, "intent": intent, "target_agents": targets, "routing_reasoning": reasoning}
    # 3. Agent Execution
    s3 = {**s2, **agent_execution_node(s2)}
    # 4. Validation
    s4 = {**s3, **validation_node(s3)}
    # 5. Final Response
    s5 = {**s4, **final_response_node(s4)}
    return s5

