import sys
import os
import json

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Build", "backend"))
sys.path.insert(0, backend_path)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.agents.market_agent import market_agent, MarketAgent
from app.schemas.agent_contract import AgentInput, LocationInfo

EXPECTED_OUTPUT_KEYS = {
    "agent_name",
    "status",
    "answer",
    "data",
    "sources",
    "location",
    "timestamp",
    "confidence",
    "warnings"
}

def test_market_rate_retrieval():
    print("--- 1. Testing Daily Market Rate Retrieval & Price Consistency ---")
    # A. Specific lookup: Silver Pomfret (Paplet)
    paplet = market_agent.get_species_market_rates("What is today's Pomfret price in Satpati?")
    assert paplet["found"] is True
    assert "Pomfret" in paplet["species_english"]
    assert paplet["modal_price"] >= 700.0
    assert paplet["price_min"] <= paplet["modal_price"] <= paplet["price_max"]
    assert "Satpati" in paplet["market_name"]
    print(f"[PASS] Specific lookup (Pomfret): Modal=Rs {paplet['modal_price']}/kg, Range={paplet['price_range']} at {paplet['market_name']}")

    # B. Specific lookup: Bombay Duck (Bombil)
    bombil = market_agent.get_species_market_rates("What is the rate for Bombil?")
    assert bombil["found"] is True
    assert "Bombay Duck" in bombil["species_english"]
    assert bombil["modal_price"] >= 100.0
    assert bombil["price_min"] <= bombil["modal_price"] <= bombil["price_max"]
    print(f"[PASS] Specific lookup (Bombil): Modal=Rs {bombil['modal_price']}/kg, Range={bombil['price_range']}")

    # C. General wholesale market overview
    overview = market_agent.get_species_market_rates("What are today's fish market rates?")
    assert overview["found"] is True
    assert "all_rates" in overview and len(overview["all_rates"]) >= 4
    print(f"[PASS] General market overview: Retrieved {len(overview['all_rates'])} species wholesale rates")

def test_harbor_price_comparison():
    print("\n--- 2. Testing Multi-Harbor Price Realization Comparison ---")
    comp = market_agent.compare_harbor_prices("Silver Pomfret")
    assert "Satpati Fish Market" in comp["market_prices"]
    assert "Arnala Bunder" in comp["market_prices"]
    assert "Dahanu APMC Yard" in comp["market_prices"]
    assert comp["highest_modal_price"] > 0
    assert comp["price_differential"] >= 0
    assert "best_realization_harbor" in comp
    print(f"[PASS] Harbor comparison (Pomfret): Highest paying harbor={comp['best_realization_harbor']} (Rs {comp['highest_modal_price']}/kg), Differential=Rs {comp['price_differential']}/kg")

def test_cold_storage_and_logistics():
    print("\n--- 3. Testing Cold Storage & Logistics Advisory ---")
    logistics = market_agent.get_logistics_and_cold_storage("Satpati")
    assert len(logistics["cold_storage_facilities"]) >= 1
    assert "NH-48" in logistics["transit_routes"]["destination_mumbai"]
    assert "ice_preservation_ratio" in logistics["transit_routes"]
    print(f"[PASS] Cold storage & transit advisory: Facility='{logistics['cold_storage_facilities'][0]['facility']}', Transit='{logistics['transit_routes']['destination_mumbai']}'")

def test_market_rag_retrieval():
    print("\n--- 4. Testing Market Advisory RAG Retrieval ---")
    rag_bylaws = market_agent.retrieve_market_rag("What is the maximum cooperative auction commission under APMC bylaws?")
    assert any("bylaws" in doc["id"].lower() for doc in rag_bylaws)
    print(f"[PASS] RAG retrieved: '{rag_bylaws[0]['title']}'")

    rag_grading = market_agent.retrieve_market_rag("What are the export size grades for Pomfret?")
    assert any("grading" in doc["id"].lower() or "export" in doc["id"].lower() for doc in rag_grading)
    print(f"[PASS] RAG retrieved: '{rag_grading[0]['title']}'")

def test_output_schema_conformance():
    print("\n--- 5. Testing Exact JSON Output Schema Conformance ---")
    query = "What is today's Pomfret price?"
    location = {"name": "Satpati", "district": "Palghar", "state": "Maharashtra"}

    result = market_agent.run_as_dict(query, location)

    # Check all required keys
    missing_keys = EXPECTED_OUTPUT_KEYS - set(result.keys())
    assert not missing_keys, f"Result is missing required keys: {missing_keys}"

    # Check key types and constraints
    assert result["agent_name"] == "Market Agent"
    assert result["status"] in ("success", "partial", "error")
    assert isinstance(result["answer"], str) and len(result["answer"]) > 20
    assert isinstance(result["data"], dict)
    assert isinstance(result["sources"], list) and len(result["sources"]) > 0
    assert isinstance(result["warnings"], list)
    assert result["confidence"] is not None and 0.0 <= result["confidence"] <= 1.0

    print("[PASS] Output strictly conforms to requested schema:")
    print(json.dumps(result, indent=2))

def run_all_market_tests():
    test_market_rate_retrieval()
    test_harbor_price_comparison()
    test_cold_storage_and_logistics()
    test_market_rag_retrieval()
    test_output_schema_conformance()
    print("\n======================================================")
    print("ALL MARKET AGENT PRODUCTION UNIT TESTS PASSED! (100%)")
    print("======================================================")

if __name__ == "__main__":
    run_all_market_tests()

