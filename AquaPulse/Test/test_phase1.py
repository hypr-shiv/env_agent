import sys
import os

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Build", "backend"))
sys.path.insert(0, backend_path)

from app.core.database import get_session
from app.db.models import CoastalLocation, MarineWeatherRecord, FishMarketPriceRecord, GovtFisheryScheme
from app.schemas.agent_contract import AgentInput, AgentOutput, AgentStatus, LocationInfo
from app.main import root, health_check, system_info

def run_coro(coro):
    """Executes coroutine synchronously without OS socket dependency."""
    while True:
        try:
            coro.send(None)
        except StopIteration as e:
            return e.value

def test_database_and_models():
    print("--- 1. Testing Database & Models ---")
    with get_session() as session:
        locs = session.query(CoastalLocation).all()
        assert len(locs) >= 5, f"Expected at least 5 locations, found {len(locs)}"
        print(f"[PASS] Found {len(locs)} Palghar landing centers: {[l.name for l in locs]}")

        weather = session.query(MarineWeatherRecord).all()
        assert len(weather) > 0, "Weather records missing"
        print(f"[PASS] Found {len(weather)} Marine weather records (Sample: {weather[0].location_name} - {weather[0].sea_condition})")

        rates = session.query(FishMarketPriceRecord).all()
        assert len(rates) > 0, "Market price records missing"
        print(f"[PASS] Found {len(rates)} Market price records (Sample: {rates[0].species_local} - Rs {rates[0].modal_price_per_kg}/kg)")

        schemes = session.query(GovtFisheryScheme).all()
        assert len(schemes) > 0, "Govt schemes missing"
        print(f"[PASS] Found {len(schemes)} Govt schemes (Sample: {schemes[0].scheme_code})")

def test_agent_contract_schemas():
    print("\n--- 2. Testing Standard Agent Contract Schemas ---")
    inp = AgentInput(
        query="Can I sail today from Satpati?",
        location=LocationInfo(name="Satpati", district="Palghar", state="Maharashtra")
    )
    assert inp.location.name == "Satpati"
    print(f"[PASS] AgentInput validated: Query='{inp.query}' at Location='{inp.location.name}'")

    out = AgentOutput(
        agent_name="Weather Agent",
        status=AgentStatus.SUCCESS,
        summary="Sea condition is moderate, wind 12 knots. Safe to sail with standard precautions.",
        location=inp.location,
        warnings=[]
    )
    assert out.status == AgentStatus.SUCCESS
    print(f"[PASS] AgentOutput validated: Agent='{out.agent_name}', Status='{out.status.value}'")

def test_api_endpoints():
    print("\n--- 3. Testing FastAPI Endpoints ---")
    res_root = run_coro(root())
    assert res_root["status"] == "operational"
    print(f"[PASS] root() -> Status: {res_root['status']}, Region: {res_root['region']}")

    res_health = run_coro(health_check())
    assert res_health["status"] == "healthy"
    print(f"[PASS] health_check() -> Status: {res_health['status']}, Database: {res_health['database']}, Ollama: {res_health['ollama']['status']}")

    res_info = run_coro(system_info())
    assert res_info["project"] == "AquaPulse"
    tracked = res_info['geography']['landing_centers_tracked']
    agents_count = len(res_info['agents'])
    print(f"[PASS] system_info() -> Tracked {tracked} landing centers across {agents_count} specialist agents")

if __name__ == "__main__":
    test_database_and_models()
    test_agent_contract_schemas()
    test_api_endpoints()
    print("\n==========================================")
    print("ALL PHASE 1 FOUNDATION TESTS PASSED! (100%)")
    print("==========================================")
