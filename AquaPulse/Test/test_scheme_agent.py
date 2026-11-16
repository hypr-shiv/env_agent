import sys
import os
import json

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Build", "backend"))
sys.path.insert(0, backend_path)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.agents.scheme_agent import scheme_agent, GovernmentSchemeAgent

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

def test_scheme_search_tool():
    print("--- 1. Testing Government Scheme Search & Catalog Retriever ---")
    # A. General scheme search
    all_schemes = scheme_agent.search_schemes("Tell me about government fisheries schemes")
    assert all_schemes["found"] is True
    assert len(all_schemes["schemes"]) >= 3
    print(f"[PASS] General scheme search: Retrieved {len(all_schemes['schemes'])} active schemes")

    # B. Specific search: Motorization subsidy
    pmmsy = scheme_agent.search_schemes("boat motorization subsidy")
    assert pmmsy["found"] is True
    assert any("PMMSY" in s["scheme_code"] for s in pmmsy["schemes"])
    print(f"[PASS] Specific lookup (PMMSY Motorization): Found '{pmmsy['schemes'][0]['name']}'")

    # C. Specific search: Maharashtra Diesel tax refund
    diesel = scheme_agent.search_schemes("diesel tax refund VAT")
    assert diesel["found"] is True
    assert any("DIESEL" in s["scheme_code"] for s in diesel["schemes"])
    print(f"[PASS] Specific lookup (Diesel VAT Refund): Found '{diesel['schemes'][0]['name']}'")

def test_beneficiary_eligibility_tool():
    print("\n--- 2. Testing Beneficiary Eligibility & Subsidy Calculation ---")
    # General Category
    gen = scheme_agent.evaluate_eligibility("PMMSY-MECH-01", beneficiary_category="General")
    assert "40%" in gen["applicable_subsidy"]
    assert gen["category_tier"] == "General Category"
    print(f"[PASS] General Category: Subsidy={gen['applicable_subsidy']}, Tier={gen['category_tier']}")

    # Women / SC / ST Category
    women = scheme_agent.evaluate_eligibility("PMMSY-MECH-01", beneficiary_category="Women")
    assert "60%" in women["applicable_subsidy"]
    assert "Priority" in women["category_tier"]
    print(f"[PASS] Women / SC / ST Priority Category: Subsidy={women['applicable_subsidy']}, Tier={women['category_tier']}")

def test_application_dossier_tool():
    print("\n--- 3. Testing Application Dossier & Palghar Office Routing ---")
    dossier = scheme_agent.get_application_dossier("PMMSY-MECH-01")
    assert len(dossier["required_documents"]) >= 4
    assert any("Biometric" in d for d in dossier["required_documents"])
    assert any("Form 2" in d for d in dossier["required_documents"])
    assert "palghar_nodal_office" in dossier
    assert len(dossier["submission_steps"]) >= 3
    print(f"[PASS] Application Dossier: Checked {len(dossier['required_documents'])} documents. Nodal Authority='{dossier['palghar_nodal_office']}'")

def test_schemes_rag_retrieval():
    print("\n--- 4. Testing Scheme Advisory RAG Retrieval ---")
    rag_pmmsy = scheme_agent.retrieve_schemes_rag("What are the PMMSY subsidy rates for boat motors?")
    assert any("pmmsy" in doc["id"].lower() for doc in rag_pmmsy)
    print(f"[PASS] RAG retrieved: '{rag_pmmsy[0]['title']}'")

    rag_diesel = scheme_agent.retrieve_schemes_rag("How can I get diesel tax refund passbook in Palghar?")
    assert any("diesel" in doc["id"].lower() for doc in rag_diesel)
    print(f"[PASS] RAG retrieved: '{rag_diesel[0]['title']}'")

def test_output_schema_conformance():
    print("\n--- 5. Testing Exact JSON Output Schema Conformance ---")
    query = "Tell me about government fisheries schemes."
    location = {"name": "Satpati", "district": "Palghar", "state": "Maharashtra"}

    result = scheme_agent.run_as_dict(query, location)

    # Check all required keys
    missing_keys = EXPECTED_OUTPUT_KEYS - set(result.keys())
    assert not missing_keys, f"Result is missing required keys: {missing_keys}"

    # Check key types and constraints
    assert result["agent_name"] == "Government Scheme Agent"
    assert result["status"] in ("success", "partial", "error")
    assert isinstance(result["answer"], str) and len(result["answer"]) > 20
    assert isinstance(result["data"], dict)
    assert isinstance(result["sources"], list) and len(result["sources"]) > 0
    assert isinstance(result["warnings"], list)
    assert result["confidence"] is not None and 0.0 <= result["confidence"] <= 1.0

    print("[PASS] Output strictly conforms to requested schema:")
    print(json.dumps(result, indent=2))

def run_all_scheme_tests():
    test_scheme_search_tool()
    test_beneficiary_eligibility_tool()
    test_application_dossier_tool()
    test_schemes_rag_retrieval()
    test_output_schema_conformance()
    print("\n================================================================")
    print("ALL GOVERNMENT SCHEME AGENT PRODUCTION UNIT TESTS PASSED! (100%)")
    print("================================================================")

if __name__ == "__main__":
    run_all_scheme_tests()

