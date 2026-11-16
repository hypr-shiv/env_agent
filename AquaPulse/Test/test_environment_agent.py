import sys
import os
import json

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Build", "backend"))
sys.path.insert(0, backend_path)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.agents.environment_agent import environment_agent, EnvironmentAgent

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

def test_water_quality_telemetry():
    print("--- 1. Testing Water Quality Telemetry Retrieval & Physical Bounds ---")
    telemetry = environment_agent.get_water_quality_telemetry("Satpati")
    assert telemetry["found"] is True, "Failed to retrieve Satpati telemetry"
    assert "Satpati" in telemetry["station_name"]
    assert 10.0 <= telemetry["sst_celsius"] <= 35.0, f"Unrealistic SST: {telemetry['sst_celsius']}"
    assert 0.0 <= telemetry["dissolved_oxygen"] <= 14.0, f"Unrealistic DO: {telemetry['dissolved_oxygen']}"
    assert 20.0 <= telemetry["salinity_ppt"] <= 40.0, f"Unrealistic Salinity: {telemetry['salinity_ppt']}"
    assert telemetry["chlorophyll_a"] > 0
    print(f"[PASS] Retrieved Satpati Buoy Telemetry: SST={telemetry['sst_celsius']}°C, DO={telemetry['dissolved_oxygen']} mg/L, Chlorophyll-a={telemetry['chlorophyll_a']} mg/m³, Salinity={telemetry['salinity_ppt']} ppt")

def test_marine_health_evaluator():
    print("\n--- 2. Testing Marine Habitat Health Index (MHHI) Evaluator ---")
    # Scenario A: Healthy Coastal Waters (DO=6.4, pH=7.9, Chlorophyll=2.1)
    healthy = environment_agent.evaluate_marine_health_index(
        dissolved_oxygen=6.4,
        chlorophyll_a=2.1,
        salinity=34.2,
        sst=28.4,
        ph=7.9
    )
    assert healthy["overall_health"] == "GOOD"
    assert healthy["mpcb_sw2_compliance"] is True
    print("[PASS] Scenario A (Healthy): Status=GOOD, MPCB SW-II Compliant=True")

    # Scenario B: Critical Hypoxia (DO=2.5 mg/L, below minimum 4.0 mg/L)
    hypoxic = environment_agent.evaluate_marine_health_index(
        dissolved_oxygen=2.5,
        chlorophyll_a=7.5,
        salinity=33.0,
        sst=29.0,
        ph=7.4
    )
    assert hypoxic["overall_health"] == "DEGRADED"
    assert hypoxic["mpcb_sw2_compliance"] is False
    print(f"[PASS] Scenario B (Hypoxic DO=2.5): Status={hypoxic['overall_health']}, Compliance={hypoxic['mpcb_sw2_compliance']}")

def test_bloom_and_pollution_analyzer():
    print("\n--- 3. Testing Harmful Algal Bloom (Red Tide) Analyzer ---")
    # Low risk
    low_risk = environment_agent.analyze_bloom_and_effluent_risk("Satpati", chlorophyll=2.1, do=6.4)
    assert low_risk["bloom_risk_level"] == "LOW"
    print(f"[PASS] Low Risk: {low_risk['bloom_risk_level']} — {low_risk['advisory']}")

    # High risk (Eutrophic bloom collapse)
    high_risk = environment_agent.analyze_bloom_and_effluent_risk("Satpati", chlorophyll=9.2, do=2.1)
    assert high_risk["bloom_risk_level"] == "HIGH"
    print(f"[PASS] High Risk: {high_risk['bloom_risk_level']} — {high_risk['advisory']}")

def test_environment_rag_retrieval():
    print("\n--- 4. Testing Environmental Advisory RAG Retrieval ---")
    rag_mpcb = environment_agent.retrieve_environment_rag("What are the MPCB dissolved oxygen standards for coastal waters?")
    assert any("sw2" in doc["id"].lower() or "standard" in doc["id"].lower() for doc in rag_mpcb)
    print(f"[PASS] RAG retrieved: '{rag_mpcb[0]['title']}'")

    rag_bloom = environment_agent.retrieve_environment_rag("Are there any red tide or harmful algal bloom warnings?")
    assert any("algal" in doc["id"].lower() for doc in rag_bloom)
    print(f"[PASS] RAG retrieved: '{rag_bloom[0]['title']}'")

def test_output_schema_conformance():
    print("\n--- 5. Testing Exact JSON Output Schema Conformance ---")
    query = "What is the water quality in Palghar?"
    location = {"name": "Satpati", "district": "Palghar", "state": "Maharashtra"}

    result = environment_agent.run_as_dict(query, location)

    # Check all required keys
    missing_keys = EXPECTED_OUTPUT_KEYS - set(result.keys())
    assert not missing_keys, f"Result is missing required keys: {missing_keys}"

    # Check key types and constraints
    assert result["agent_name"] == "Environment Agent"
    assert result["status"] in ("success", "partial", "error")
    assert isinstance(result["answer"], str) and len(result["answer"]) > 20
    assert isinstance(result["data"], dict)
    assert isinstance(result["sources"], list) and len(result["sources"]) > 0
    assert isinstance(result["warnings"], list)
    assert result["confidence"] is not None and 0.0 <= result["confidence"] <= 1.0

    print("[PASS] Output strictly conforms to requested schema:")
    print(json.dumps(result, indent=2))

def run_all_environment_tests():
    test_water_quality_telemetry()
    test_marine_health_evaluator()
    test_bloom_and_pollution_analyzer()
    test_environment_rag_retrieval()
    test_output_schema_conformance()
    print("\n===========================================================")
    print("ALL ENVIRONMENT AGENT PRODUCTION UNIT TESTS PASSED! (100%)")
    print("===========================================================")

if __name__ == "__main__":
    run_all_environment_tests()

