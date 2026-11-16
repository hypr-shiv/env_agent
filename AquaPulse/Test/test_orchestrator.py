import sys
import os

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Build", "backend"))
sys.path.insert(0, backend_path)

from app.orchestrator.graph import invoke_orchestrator, aquapulse_graph
from app.orchestrator.router import rule_based_classification

REQUIRED_RESULT_KEYS = {
    "agent_name",
    "status",
    "answer",
    "source",
    "location",
    "timestamp",
    "confidence",
    "warnings"
}

def verify_structured_agent_result(agent_res: dict, expected_name: str):
    missing_keys = REQUIRED_RESULT_KEYS - set(agent_res.keys())
    assert not missing_keys, f"Agent result missing mandatory keys: {missing_keys}"
    assert agent_res["status"] in ("success", "partial", "error"), f"Invalid status: {agent_res['status']}"
    assert agent_res["confidence"] >= 0.0 and agent_res["confidence"] <= 1.0, f"Invalid confidence: {agent_res['confidence']}"
    assert isinstance(agent_res["warnings"], list), "warnings must be a list"
    assert isinstance(agent_res["location"], dict), "location must be a dict"
    assert "name" in agent_res["location"], "location must contain 'name'"

def test_routing_conditions():
    test_cases = [
        # 1. Weather Agent
        {
            "query": "What is today's weather in Palghar?",
            "expected_targets": ["weather"],
            "expected_agents": ["Weather Agent"]
        },
        # 2. Fisheries Agent
        {
            "query": "Which fish species are available in Palghar?",
            "expected_targets": ["fisheries"],
            "expected_agents": ["Fisheries Agent"]
        },
        # 3. Environment Agent
        {
            "query": "What is the water quality in Palghar?",
            "expected_targets": ["environment"],
            "expected_agents": ["Environment Agent"]
        },
        # 4. Market Agent
        {
            "query": "What is today's Pomfret price?",
            "expected_targets": ["market"],
            "expected_agents": ["Market Agent"]
        },
        # 5. Disaster Agent
        {
            "query": "Is there a cyclone warning?",
            "expected_targets": ["disaster"],
            "expected_agents": ["Disaster Agent"]
        },
        # 6. Government Scheme Agent
        {
            "query": "Tell me about government fisheries schemes.",
            "expected_targets": ["scheme"],
            "expected_agents": ["Government Scheme Agent"]
        },
        # 7. Complaint Agent
        {
            "query": "Register a pollution complaint.",
            "expected_targets": ["complaint"],
            "expected_agents": ["Complaint Agent"]
        },
        # 8. Complex Multi-Agent: Weather + Disaster + Fisheries
        {
            "query": "Can I go fishing tomorrow?",
            "expected_targets": ["weather", "disaster", "fisheries"],
            "expected_agents": ["Weather Agent", "Disaster Agent", "Fisheries Agent"]
        },
        # 9. Complex Multi-Agent: Fisheries + Market
        {
            "query": "Identify this fish and tell me its market price.",
            "expected_targets": ["fisheries", "market"],
            "expected_agents": ["Fisheries Agent", "Market Agent"]
        }
    ]

    print("\n==================================================================")
    print("AQUAPULSE MULTI-AGENT ORCHESTRATOR ROUTING & EXECUTION TEST SUITE")
    print("==================================================================\n")

    passed_count = 0

    for idx, tc in enumerate(test_cases, 1):
        query = tc["query"]
        expected_targets = tc["expected_targets"]
        print(f"[{idx}/9] Query: '{query}'")

        # 1. Verify router classification
        intent, targets, reasoning = rule_based_classification(query)
        assert targets == expected_targets, f"Expected {expected_targets}, got {targets}"
        print(f"      -> Intent: {intent} | Targets: {targets}")

        # 2. Run full multi-agent orchestrator pipeline
        state = invoke_orchestrator(query)

        # 3. Verify target agents match
        assert state["target_agents"] == expected_targets, f"State target mismatch: {state['target_agents']}"

        # 4. Verify each agent produced a structured result with all mandatory keys
        for target in expected_targets:
            assert target in state["agent_results"], f"Missing result for {target}"
            agent_res = state["agent_results"][target]
            verify_structured_agent_result(agent_res, target)
            print(f"      -> {agent_res['agent_name']}: Status='{agent_res['status']}', Conf={agent_res['confidence']}")

        # 5. Verify validation node passed
        assert state["validation_passed"] is True, f"Validation failed: {state.get('validation_notes')}"

        # 6. Verify final synthesis exists
        assert len(state["final_answer"]) > 20, "Final answer too short"
        assert len(state["sources"]) >= len(expected_targets), "Sources count mismatch"

        print(f"      [PASS] Validation passed. Final answer length: {len(state['final_answer'])} chars\n")
        passed_count += 1

    print("==================================================================")
    print(f"ALL {passed_count}/{len(test_cases)} ROUTING & MULTI-AGENT ORCHESTRATOR TESTS PASSED! (100%)")
    print("==================================================================")

if __name__ == "__main__":
    test_routing_conditions()

