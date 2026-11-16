import re
import json
import logging
from typing import Dict, Any, List, Tuple
from app.core.ollama_client import ollama_client

logger = logging.getLogger("aquapulse.router")

ROUTING_PROMPT = """
You are the central intent classification router for AquaPulse (Palghar, Maharashtra).
Given a user query, identify the required specialist agent(s) from:
- 'weather': Marine weather, sea conditions, wind, wave height, sailing safety.
- 'fisheries': Fish species availability, fishing zones, fish identification from photo/name.
- 'disaster': Cyclones, storms, tsunamis, high-swell alerts, emergency contacts.
- 'market': Wholesale fish prices, modal rates at landing centers (Satpati, Arnala, Dahanu).
- 'environment': Water quality, SST, chlorophyll, salinity, algal blooms, pollution telemetry.
- 'scheme': Government fisheries subsidies, PMMSY, diesel refund, KCC loans.
- 'complaint': Public grievances, illegal trawling reports, harbor facility issues.

Respond ONLY with valid JSON in this format:
{
  "intent": "<short_intent_name>",
  "target_agents": ["<agent_id>", ...],
  "reasoning": "<short_justification>"
}
"""

def rule_based_classification(query: str, attachments: List[Any] = None) -> Tuple[str, List[str], str]:
    """
    Deterministic rule-based intent classifier with English, Hindi, and Marathi keyword support.
    Guarantees immediate, zero-latency classification for canonical and conversational queries.
    """
    q = query.lower().strip()
    words = set(re.findall(r'\w+', q))

    # 0. Conversational Greetings / Capabilities
    greeting_exact = {"hello", "hi", "hey", "namaste", "namaskar", "help", "madat"}
    if words.intersection(greeting_exact) or any(k in q for k in ["who are you", "what can you do", "about aquapulse", "features", "kon ahes", "kay karu shakto"]):
        return ("assistant_greeting", ["assistant_greeting"], "Conversational greeting or capability orientation.")

    # Multi-agent complex query 1: "Can I go fishing tomorrow?" / "Should I sail?"
    if any(k in q for k in ["can i go fishing", "safe to go fishing", "should i go fishing", "can i sail tomorrow", "go fishing tomorrow", "daryat jau ka", "fishing la jau ka"]):
        return (
            "comprehensive_fishing_safety",
            ["weather", "disaster", "fisheries"],
            "Safety evaluation requires marine weather, active disaster alerts, and target species/season info."
        )

    # Multi-agent complex query 2: "Identify this fish and tell me its market price"
    has_image = bool(attachments and len(attachments) > 0)
    has_identify = any(k in q for k in ["identify this fish", "identify", "which fish is this", "recognize fish", "species in image"]) or has_image
    has_price = any(k in q for k in ["price", "market", "rate", "cost", "value", "mandi", "bhav", "bhaav", "kimat", "दर", "भाव"])

    if has_identify and has_price:
        return (
            "fish_identification_and_pricing",
            ["fisheries", "market"],
            "Vision/species identification delegates to Fisheries Agent, followed by Market Agent rate lookup."
        )

    if has_identify and not has_price:
        return (
            "fish_identification",
            ["fisheries"],
            "Specimen visual identification delegates to Fisheries Agent & Vision Classifier."
        )

    # Disaster Agent (Cyclones, Tsunamis, Early Warnings, Emergency Helplines)
    disaster_keywords = [
        "cyclone", "storm", "warning", "tsunami", "high swell", "emergency", "evacuation",
        "alert", "helpline", "toofan", "vadvad", "vadal", "dhoka", "apatti", "chetavani",
        "sankat", "चक्रीवादळ", "वादळ", "धोका", "इशारा", "आपत्ती"
    ]
    if any(k in q for k in disaster_keywords):
        return ("disaster_warning", ["disaster"], "Query pertains to emergency disaster warnings or cyclone status.")

    # Market Agent (Prices, Wholesale Mandi, APMC, Rates, Realization)
    market_keywords = [
        "price", "market rate", "cost per kg", "wholesale", "mandi", "market", "auction",
        "bhav", "bhaav", "daam", "kimat", "kimmat", "bajar", "vikri", "apmc", "cooperative fee",
        "rate", "rates", "cost", "bombay duck price", "pomfret price",
        "भाव", "किंमत", "दर", "बाजार", "विक्री"
    ]
    if any(k in q for k in market_keywords) or (("rate" in words or "price" in words or "cost" in words) and any(f in q for f in ["fish", "pomfret", "bombil", "bombay duck", "mackerel", "surmai", "prawn", "paplet"])):
        return ("market_pricing", ["market"], "Query pertains to fish market auction prices.")

    # Government Scheme Agent (PMMSY, Subsidies, Diesel Refund, KCC, Loans, Insurance)
    scheme_keywords = [
        "scheme", "subsidy", "pmmsy", "diesel refund", "diesel", "vat", "hsd", "fuel refund",
        "kcc", "kisan credit", "loan", "grant", "government", "insurance", "gais", "assistance",
        "yojana", "anudan", "karj", "vima", "sarkari", "योजना", "अनुदान", "कर्ज", "विमा", "मदत"
    ]
    if any(k in q for k in scheme_keywords):
        return ("government_schemes", ["scheme"], "Query pertains to government fisheries schemes or subsidies.")

    # Complaint Agent (Grievances, Violations, Illegal Trawling, Reporting)
    complaint_keywords = [
        "complaint", "grievance", "illegal trawling", "report pollution", "register", "violation",
        "takraar", "takrar", "shikayat", "nondva", "arji", "तक्रार", "गाऱ्हाणे", "नोंदवा"
    ]
    if any(k in q for k in complaint_keywords):
        return ("public_complaint", ["complaint"], "Query pertains to registering or tracking a grievance.")

    # Environment Agent (Water Quality, SST, Salinity, Chlorophyll, Algal Blooms, Tarapur MIDC, Effluent)
    env_keywords = [
        "water quality", "environment", "salinity", "chlorophyll", "algal bloom", "red tide",
        "pollution telemetry", "effluent", "tarapur", "midc", "dissolved oxygen", "ph level",
        "pradushan", "paryavaran", "pani gunvatta", "प्रदूषण", "पर्यावरण"
    ]
    if any(k in q for k in env_keywords):
        return ("coastal_environment", ["environment"], "Query pertains to oceanographic or water quality indicators.")

    # Weather Agent (Marine Weather, Sea Condition, Wind, Wave, Swell, Tide, Safe to Sail, Monsoon Ban)
    weather_keywords = [
        "weather", "wind", "wave", "sea condition", "sea status", "how is the sea", "tide", "high tide", "low tide",
        "safe to sail", "monsoon ban", "fishing ban", "monsoon", "breeze", "swell", "water temp", "sea temp", "hawa", "havaman", "mosam",
        "vara", "wara", "lata", "lahar", "bharti", "oti", "samudra", "हवामान", "वारा", "लाटा", "भरती", "ओहोटी", "समुद्र"
    ]
    if any(k in q for k in weather_keywords):
        return ("marine_weather", ["weather"], "Query pertains to marine weather or sea conditions.")

    # Fisheries Agent (Commercial Fish Species, Catch, PFZ, Mesh Size, Legal Size, Habits, Banned Practices)
    fisheries_keywords = [
        "fish species", "species available", "what fish", "catch", "pfz", "potential fishing zone", "mesh size",
        "legal size", "minimum size", "banned practice", "banned", "prohibited", "led fishing", "light fishing",
        "bull trawling", "pair trawling", "purse seine", "pomfret", "bombil", "bombay duck", "mackerel", "surmai",
        "prawn", "shark", "harvesting", "matsya", "machli", "masa", "mase", "masoli", "paplet", "bangda", "kolambi",
        "जाळी", "मासे", "मासोळी", "मासेमारी", "पापलेट", "बोंबील", "बांगडा", "सुरमई", "कोळंबी"
    ]
    if any(k in q for k in fisheries_keywords):
        return ("fisheries_information", ["fisheries"], "Query pertains to commercial fish species or fishing zones.")

    # Check for general coastal inquiry keywords
    coastal_keywords = ["palghar", "satpati", "dahanu", "arnala", "kelve", "vasai", "harbor", "bunder"]
    if any(k in q for k in coastal_keywords):
        return ("general_fisheries_query", ["weather", "fisheries"], "Default coastal informational query.")

    # Unsupported / Out-of-Domain Query Detection
    return (
        "unsupported_question",
        ["unknown"],
        "Query is outside the operational scope of AquaPulse (Palghar coastal and marine fisheries system)."
    )

async def classify_intent(query: str, attachments: List[Any] = None) -> Tuple[str, List[str], str]:
    """
    Classifies intent using Ollama Llama 3.2:3b if reachable,
    otherwise instantly falls back to rule-based classification.
    """
    if not ollama_client.is_reachable():
        return rule_based_classification(query, attachments)

    try:
        raw_response = await ollama_client.generate(
            prompt=f"User Query: '{query}'",
            system_prompt=ROUTING_PROMPT,
            json_format=True
        )
        data = json.loads(raw_response)
        intent = data.get("intent", "general_query")
        target_agents = data.get("target_agents", ["weather"])
        reasoning = data.get("reasoning", "LLM Classification")

        # Validate target agents
        valid_agents = {"weather", "fisheries", "disaster", "market", "environment", "scheme", "complaint", "unknown"}
        filtered = [a for a in target_agents if a in valid_agents]
        if filtered:
            return intent, filtered, reasoning
        return rule_based_classification(query, attachments)
    except Exception as e:
        logger.warning(f"Ollama intent classification fallback due to: {e}")
        return rule_based_classification(query, attachments)

