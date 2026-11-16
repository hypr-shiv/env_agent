import sys
import os
import json

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Build", "backend"))
sys.path.insert(0, backend_path)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.agents.fisheries_agent import fisheries_agent, FisheriesAgent
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

def test_species_catalog_tool():
    print("--- 1. Testing Species Catalog & Biological Profiles ---")
    # A. Specific species lookup: Bombay Duck (Bombil)
    bombil = fisheries_agent.get_species_profile("What is the harvesting season for Bombil in Satpati?")
    assert bombil["found"] is True
    assert "profile" in bombil
    assert bombil["profile"]["english_name"] == "Bombay Duck"
    assert "Harpadon nehereus" in bombil["profile"]["scientific_name"]
    assert "18 cm" in bombil["profile"]["minimum_legal_size"]
    print(f"[PASS] Specific lookup (Bombil): Scientific='{bombil['profile']['scientific_name']}', Gear='{bombil['profile']['gear']}', MLS='{bombil['profile']['minimum_legal_size']}'")

    # B. Specific species lookup: Silver Pomfret (Paplet)
    paplet = fisheries_agent.get_species_profile("Tell me about Paplet fish")
    assert paplet["found"] is True
    assert paplet["profile"]["english_name"] == "Silver Pomfret"
    assert "Pampus argenteus" in paplet["profile"]["scientific_name"]
    print(f"[PASS] Specific lookup (Paplet): Scientific='{paplet['profile']['scientific_name']}', Season='{paplet['profile']['peak_season']}'")

    # C. General Palghar catalog
    catalog = fisheries_agent.get_species_profile("Which fish species are available in Palghar?")
    assert catalog["found"] is True
    assert "catalog" in catalog and len(catalog["catalog"]) >= 5
    print(f"[PASS] General catalog lookup: Found {len(catalog['catalog'])} commercial marine species for Palghar")

def test_pfz_advisory_tool():
    print("\n--- 2. Testing Potential Fishing Zones (PFZ) Advisory ---")
    pfz = fisheries_agent.get_pfz_advisory("Satpati")
    assert pfz["location"] == "Satpati"
    assert "bearing" in pfz["recommended_bearing"].lower() or "°" in pfz["recommended_bearing"]
    assert pfz["distance_nautical_miles"] > 10.0
    assert len(pfz["target_pelagic_species"]) >= 2
    assert "sst_gradient" in pfz["oceanographic_indicators"]
    print(f"[PASS] PFZ Advisory generated for Satpati: Bearing={pfz['recommended_bearing']}, Distance={pfz['distance_nautical_miles']} NM, Targets={pfz['target_pelagic_species']}")

def test_fish_identification_tool():
    print("\n--- 3. Testing Fish Species Identification Tool ---")
    ident = fisheries_agent.identify_fish_species("Identify this pomfret fish from today's catch")
    assert "Pomfret" in ident["identified_species"]
    assert "Pampus argenteus" in ident["scientific_name"]
    assert ident["confidence"] >= 0.85
    assert "minimum_legal_size" in ident
    print(f"[PASS] Identified species: {ident['identified_species']} ({ident['local_name']}) with confidence {int(ident['confidence']*100)}%")

def test_gear_compliance_tool():
    print("\n--- 4. Testing MMFRA Gear Legality Compliance Tool ---")
    # Legal dol net
    dol = fisheries_agent.check_gear_compliance("Can I use dol net near Satpati?")
    assert dol["status"] == "PERMITTED WITH REGULATION"
    assert "40 mm" in dol["rules"]
    print(f"[PASS] Dol net compliance: {dol['status']} — {dol['rules']}")

    # Banned bull trawling
    bull = fisheries_agent.check_gear_compliance("Is pair trawling / bull trawl allowed?")
    assert bull["status"] == "STRICTLY BANNED"
    print(f"[PASS] Bull trawl compliance: {bull['status']}")

def test_fisheries_rag_retrieval():
    print("\n--- 5. Testing Fisheries Advisory RAG Retrieval ---")
    rag_mesh = fisheries_agent.retrieve_fisheries_rag("What is the legal mesh size to prevent catching juvenile fish?")
    assert any("mesh" in doc["id"].lower() for doc in rag_mesh)
    print(f"[PASS] RAG retrieved: '{rag_mesh[0]['title']}'")

    rag_banned = fisheries_agent.retrieve_fisheries_rag("Are purse-seine nets allowed within 12 nautical miles?")
    assert any("banned" in doc["id"].lower() or "mesh" in doc["id"].lower() for doc in rag_banned)
    print(f"[PASS] RAG retrieved: '{rag_banned[0]['title']}'")

def test_output_schema_conformance():
    print("\n--- 6. Testing Exact JSON Output Schema Conformance ---")
    query = "Which fish species are available in Palghar?"
    location = {"name": "Satpati", "district": "Palghar", "state": "Maharashtra"}

    result = fisheries_agent.run_as_dict(query, location)

    # Check all required keys
    missing_keys = EXPECTED_OUTPUT_KEYS - set(result.keys())
    assert not missing_keys, f"Result is missing required keys: {missing_keys}"

    # Check key types and constraints
    assert result["agent_name"] == "Fisheries Agent"
    assert result["status"] in ("success", "partial", "error")
    assert isinstance(result["answer"], str) and len(result["answer"]) > 20
    assert isinstance(result["data"], dict)
    assert isinstance(result["sources"], list) and len(result["sources"]) > 0
    assert isinstance(result["warnings"], list)
    assert result["confidence"] is not None and 0.0 <= result["confidence"] <= 1.0

    print("[PASS] Output strictly conforms to requested schema:")
    print(json.dumps(result, indent=2))

def run_all_fisheries_tests():
    test_species_catalog_tool()
    test_pfz_advisory_tool()
    test_fish_identification_tool()
    test_gear_compliance_tool()
    test_fisheries_rag_retrieval()
    test_output_schema_conformance()
    print("\n=========================================================")
    print("ALL FISHERIES AGENT PRODUCTION UNIT TESTS PASSED! (100%)")
    print("=========================================================")

if __name__ == "__main__":
    run_all_fisheries_tests()
