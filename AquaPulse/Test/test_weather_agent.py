import sys
import os
import json
from datetime import datetime

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Build", "backend"))
sys.path.insert(0, backend_path)

from app.agents.weather_agent import weather_agent, WeatherAgent
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

def test_observation_tool():
    print("--- 1. Testing Marine Weather Observation Retrieval & Validation ---")
    obs = weather_agent.get_marine_weather_observation("Satpati")
    assert obs["found"] is True, "Failed to retrieve Satpati observation"
    assert obs["location"] == "Satpati"
    assert obs["wind_speed_knots"] > 0
    assert obs["wave_height_meters"] > 0
    assert obs["data_mode"] in ("live", "historical", "mock")
    print(f"[PASS] Retrieved Satpati observation: Wind={obs['wind_speed_knots']}kts, Waves={obs['wave_height_meters']}m, Condition='{obs['sea_condition']}'")

def test_tide_forecast_tool():
    print("\n--- 2. Testing Palghar Tidal Prediction Tool ---")
    tides = weather_agent.get_tide_forecast("Satpati")
    assert "next_high_tide" in tides
    assert "next_low_tide" in tides
    assert tides["next_high_tide"]["height_meters"] > tides["next_low_tide"]["height_meters"]
    assert "creek_navigation_advisory" in tides
    print(f"[PASS] Tidal predictions generated: High Tide={tides['next_high_tide']['time']} ({tides['next_high_tide']['height_meters']}m), Low Tide={tides['next_low_tide']['time']} ({tides['next_low_tide']['height_meters']}m)")

def test_safe_to_sail_matrix():
    print("\n--- 3. Testing Safe-to-Sail Multi-Vessel Matrix ---")
    # Scenario A: Calm conditions (Wind 8 kts, Wave 0.8m)
    calm = weather_agent.evaluate_safe_to_sail(wind_speed_knots=8, wave_height_meters=0.8)
    assert calm["overall_index"] == "SAFE"
    assert calm["vessel_breakdown"]["traditional_canoes"]["status"] == "SAFE"
    assert calm["vessel_breakdown"]["motorized_craft"]["status"] == "SAFE"
    assert calm["vessel_breakdown"]["mechanized_trawlers"]["status"] == "SAFE"
    print("[PASS] Scenario A (Calm): All 3 vessel categories SAFE")

    # Scenario B: Moderate conditions (Wind 15 kts, Wave 1.3m)
    moderate = weather_agent.evaluate_safe_to_sail(wind_speed_knots=15, wave_height_meters=1.3)
    assert moderate["vessel_breakdown"]["traditional_canoes"]["status"] == "CAUTION"
    assert moderate["vessel_breakdown"]["motorized_craft"]["status"] == "SAFE"
    print("[PASS] Scenario B (Moderate): Traditional=CAUTION, Motorized=SAFE")

    # Scenario C: Severe Gale conditions (Wind 32 kts, Wave 3.4m)
    severe = weather_agent.evaluate_safe_to_sail(wind_speed_knots=32, wave_height_meters=3.4)
    assert severe["overall_index"] == "UNSAFE"
    assert severe["vessel_breakdown"]["traditional_canoes"]["status"] == "UNSAFE"
    assert severe["vessel_breakdown"]["motorized_craft"]["status"] == "UNSAFE"
    assert severe["vessel_breakdown"]["mechanized_trawlers"]["status"] == "UNSAFE"
    print("[PASS] Scenario C (Gale 32kts): All vessel categories UNSAFE")

def test_weather_rag_retrieval():
    print("\n--- 4. Testing Weather Advisory RAG Retrieval ---")
    rag_monsoon = weather_agent.retrieve_weather_advisory_rag("When is the monsoon fishing ban in Palghar?")
    assert any("monsoon" in doc["title"].lower() for doc in rag_monsoon)
    print(f"[PASS] RAG retrieved: '{rag_monsoon[0]['title']}'")

    rag_tides = weather_agent.retrieve_weather_advisory_rag("Can deep trawlers enter Satpati creek at low tide?")
    assert any("tide" in doc["title"].lower() or "swell" in doc["title"].lower() for doc in rag_tides)
    print(f"[PASS] RAG retrieved: '{rag_tides[0]['title']}'")

def test_output_schema_conformance():
    print("\n--- 5. Testing Exact JSON Output Schema Conformance ---")
    query = "What is the sea condition off Dahanu?"
    location = {"name": "Dahanu", "district": "Palghar", "state": "Maharashtra"}
    
    result = weather_agent.run_as_dict(query, location)

    # Check all required keys
    missing_keys = EXPECTED_OUTPUT_KEYS - set(result.keys())
    assert not missing_keys, f"Result is missing required keys: {missing_keys}"

    # Check key types and constraints
    assert result["agent_name"] == "Weather Agent"
    assert result["status"] in ("success", "partial", "error")
    assert isinstance(result["answer"], str) and len(result["answer"]) > 20
    assert isinstance(result["data"], dict)
    assert isinstance(result["sources"], list) and len(result["sources"]) > 0
    assert isinstance(result["warnings"], list)
    assert result["location"] == "Dahanu" or (isinstance(result["location"], dict) and result["location"].get("name") == "Dahanu")
    assert result["confidence"] is not None and 0.0 <= result["confidence"] <= 1.0

    print("[PASS] Output strictly conforms to requested schema:")
    print(json.dumps(result, indent=2))

def run_all_weather_tests():
    test_observation_tool()
    test_tide_forecast_tool()
    test_safe_to_sail_matrix()
    test_weather_rag_retrieval()
    test_output_schema_conformance()
    print("\n=======================================================")
    print("ALL WEATHER AGENT PRODUCTION UNIT TESTS PASSED! (100%)")
    print("=======================================================")

if __name__ == "__main__":
    run_all_weather_tests()
