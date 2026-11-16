import os
import io
import sys
import unittest
from datetime import datetime
from PIL import Image, ImageDraw

# Configure UTF-8 encoding for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Build", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.orchestrator.graph import invoke_orchestrator
from app.db.seed_data import seed_palghar_data_sync

def create_synthetic_fish_image() -> bytes:
    """Creates a synthetic fish specimen image in bytes."""
    img = Image.new("RGB", (300, 200), color=(200, 210, 220))
    draw = ImageDraw.Draw(img)
    # Draw silvery diamond shape (Silver Pomfret)
    draw.polygon([(50, 100), (150, 30), (250, 100), (150, 170)], fill=(225, 230, 240), outline=(180, 190, 200))
    draw.ellipse([(180, 80), (200, 95)], fill=(40, 40, 40))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

class TestAquaPulseOrchestratorIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Seed baseline PostgreSQL / SQLite database records."""
        seed_palghar_data_sync()

    def test_01_weather_only_query(self):
        """Scenario 1: Weather-only query routes strictly to Weather Agent."""
        res = invoke_orchestrator("What is today's weather in Palghar?")
        self.assertEqual(res["intent"], "marine_weather")
        self.assertEqual(res["target_agents"], ["weather"])
        self.assertIn("weather", res["agent_results"])
        self.assertEqual(res["agent_results"]["weather"]["status"], "success")
        self.assertTrue(res["validation_passed"])
        self.assertGreater(len(res["sources"]), 0)

    def test_02_fisheries_only_query(self):
        """Scenario 2: Fisheries-only query routes strictly to Fisheries Agent."""
        res = invoke_orchestrator("Which fish species are available in Palghar?")
        self.assertEqual(res["intent"], "fisheries_information")
        self.assertEqual(res["target_agents"], ["fisheries"])
        self.assertIn("fisheries", res["agent_results"])
        self.assertEqual(res["agent_results"]["fisheries"]["status"], "success")
        self.assertTrue(res["validation_passed"])

    def test_03_environment_only_query(self):
        """Scenario 3: Environment-only query routes strictly to Environment Agent."""
        res = invoke_orchestrator("What is the water quality in Palghar?")
        self.assertEqual(res["intent"], "coastal_environment")
        self.assertEqual(res["target_agents"], ["environment"])
        self.assertIn("environment", res["agent_results"])
        self.assertEqual(res["agent_results"]["environment"]["status"], "success")
        self.assertTrue(res["validation_passed"])

    def test_04_disaster_only_query(self):
        """Scenario 4: Disaster-only query routes strictly to Disaster Agent."""
        res = invoke_orchestrator("Is there a cyclone warning?")
        self.assertEqual(res["intent"], "disaster_warning")
        self.assertEqual(res["target_agents"], ["disaster"])
        self.assertIn("disaster", res["agent_results"])
        self.assertEqual(res["agent_results"]["disaster"]["status"], "success")
        self.assertTrue(res["validation_passed"])

    def test_05_market_only_query(self):
        """Scenario 5: Market-only query routes strictly to Market Agent."""
        res = invoke_orchestrator("What is today's Pomfret price?")
        self.assertEqual(res["intent"], "market_pricing")
        self.assertEqual(res["target_agents"], ["market"])
        self.assertIn("market", res["agent_results"])
        self.assertEqual(res["agent_results"]["market"]["status"], "success")
        self.assertTrue(res["validation_passed"])

    def test_06_government_scheme_query(self):
        """Scenario 6: Government scheme query routes strictly to Scheme Agent."""
        res = invoke_orchestrator("Tell me about government fisheries schemes.")
        self.assertEqual(res["intent"], "government_schemes")
        self.assertEqual(res["target_agents"], ["scheme"])
        self.assertIn("scheme", res["agent_results"])
        self.assertEqual(res["agent_results"]["scheme"]["status"], "success")
        self.assertTrue(res["validation_passed"])

    def test_07_complaint_registration(self):
        """Scenario 7: Complaint registration routes strictly to Complaint Agent."""
        res = invoke_orchestrator("Register a pollution complaint.")
        self.assertEqual(res["intent"], "public_complaint")
        self.assertEqual(res["target_agents"], ["complaint"])
        self.assertIn("complaint", res["agent_results"])
        self.assertEqual(res["agent_results"]["complaint"]["status"], "success")
        self.assertTrue(res["validation_passed"])

    def test_08_fish_image_identification(self):
        """Scenario 8: Fish image specimen upload invokes Fish Vision Module & Fisheries Agent."""
        img_bytes = create_synthetic_fish_image()
        attachments = [{"filename": "fish_specimen.jpg", "bytes": img_bytes, "content_type": "image/jpeg"}]

        res = invoke_orchestrator("Identify this fish", attachments=attachments)
        self.assertEqual(res["intent"], "fish_identification")
        self.assertEqual(res["target_agents"], ["fisheries"])
        self.assertIn("fisheries", res["agent_results"])

        fish_res = res["agent_results"]["fisheries"]
        self.assertEqual(fish_res["status"], "success")
        self.assertIn("Silver Pomfret", fish_res["answer"])
        self.assertTrue(res["validation_passed"])

    def test_09_fish_image_plus_price_query(self):
        """Scenario 9: Multi-agent fish image identification + market price lookup."""
        img_bytes = create_synthetic_fish_image()
        attachments = [{"filename": "fish_specimen.jpg", "bytes": img_bytes, "content_type": "image/jpeg"}]

        res = invoke_orchestrator("Identify this fish and tell me its market price.", attachments=attachments)
        self.assertEqual(res["intent"], "fish_identification_and_pricing")
        self.assertIn("fisheries", res["target_agents"])
        self.assertIn("market", res["target_agents"])
        self.assertIn("fisheries", res["agent_results"])
        self.assertIn("market", res["agent_results"])

        market_res = res["agent_results"]["market"]
        self.assertEqual(market_res["status"], "success")
        self.assertTrue(res["validation_passed"])
        self.assertIn("Silver Pomfret", res["final_answer"])

    def test_10_multi_agent_fishing_advisory(self):
        """Scenario 10: Multi-agent fishing advisory connects Weather, Disaster, and Fisheries."""
        res = invoke_orchestrator("Can I go fishing tomorrow?")
        self.assertEqual(res["intent"], "comprehensive_fishing_safety")
        self.assertEqual(res["target_agents"], ["weather", "disaster", "fisheries"])
        self.assertIn("weather", res["agent_results"])
        self.assertIn("disaster", res["agent_results"])
        self.assertIn("fisheries", res["agent_results"])
        self.assertTrue(res["validation_passed"])
        self.assertIn("Safety Advisory", res["final_answer"])

    def test_11_unknown_or_unsupported_question(self):
        """Scenario 11: Unknown or out-of-scope question is rejected gracefully without hallucination."""
        res = invoke_orchestrator("What is the capital of France?")
        self.assertEqual(res["intent"], "unsupported_question")
        self.assertEqual(res["target_agents"], ["unknown"])
        self.assertIn("outside the operational scope", res["final_answer"])
        self.assertEqual(res["agent_results"]["unknown"]["status"], "unsupported")

    def test_12_missing_and_outdated_data(self):
        """Scenario 12: Missing/unrecorded species is handled honestly with warnings."""
        res = invoke_orchestrator("What is the market price of Martian Coral Shark in Satpati?")
        self.assertEqual(res["intent"], "market_pricing")
        self.assertIn("market", res["agent_results"])
        market_res = res["agent_results"]["market"]
        # System should not invent prices for non-existent fish
        self.assertIn("warnings", market_res)

if __name__ == "__main__":
    unittest.main()

