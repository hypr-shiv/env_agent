import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Build", "backend")))
from app.orchestrator.graph import invoke_orchestrator

queries = [
    ("Wind", "What is the wind speed in Satpati?"),
    ("Wave", "What is the wave height in Dahanu?"),
    ("Tide", "When is the high tide?"),
    ("SafeToSail", "Is it safe to sail today?"),
    ("MonsoonBan", "When is the monsoon fishing ban in Maharashtra?"),
    ("Pomfret", "What is the price of Pomfret?"),
    ("Bombil", "What is the rate of Bombay duck?"),
    ("Diesel", "How to get diesel refund subsidy?"),
    ("KCC", "Tell me about Kisan Credit Card loan."),
    ("Mesh", "What is the minimum legal mesh size?"),
    ("Banned", "Is LED light fishing allowed?"),
    ("Greeting", "Hello, who are you?"),
    ("MarathiWeather", "आज हवामान कसे आहे?")
]

print("=== QUESTION SPECIFICITY VERIFICATION ===")
for tag, q in queries:
    res = invoke_orchestrator(q)
    ans = res.get("final_answer", "")
    targets = res.get("target_agents", [])
    print(f"\n--- [{tag}] ---")
    print(f"Query:   {q}")
    print(f"Targets: {targets}")
    print(f"Answer:\n{ans}")

