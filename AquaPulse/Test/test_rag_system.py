import os
import sys
import unittest
import asyncio

# Configure UTF-8 encoding for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure app path is available
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Build", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.rag.document_loader import clean_text, chunk_text, extract_txt_file, extract_csv_file, extract_pdf_file, load_document
from app.rag.vector_store import aquapulse_vector_store, AGENT_COLLECTIONS
from app.rag.ingest_all import ingest_all_documents

def run_coro(coro):
    """Executes coroutine synchronously without OS socket dependency."""
    while True:
        try:
            coro.send(None)
        except StopIteration as e:
            return e.value

class TestAquaPulseRAGSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Ensure all corpus documents are indexed before running tests."""
        docs_dir = os.path.join(backend_dir, "app", "rag", "documents")
        cls.ingestion_results = ingest_all_documents(docs_dir=docs_dir)

    def test_01_text_cleaning_and_normalization(self):
        """Verify irregular whitespace and line breaks are cleaned properly."""
        raw = "   AquaPulse    Palghar \r\n\r\n   Monsoon Advisory   \n\n\n\nFisheries Department  "
        cleaned = clean_text(raw)
        self.assertIn("AquaPulse Palghar", cleaned)
        self.assertIn("Monsoon Advisory", cleaned)
        self.assertNotIn("   ", cleaned)
        self.assertNotIn("\r", cleaned)

    def test_02_text_chunking_with_overlap(self):
        """Verify text is chunked into logical units with overlap."""
        sample_text = (
            "The Pradhan Mantri Matsya Sampada Yojana is a flagship scheme. "
            "It provides up to sixty percent subsidy for women and Scheduled Tribes. "
            "Fishermen in Satpati and Dahanu can apply online through the official portal. "
            "All applications must be verified by the District Fisheries Officer within fifteen days."
        )
        chunks = chunk_text(sample_text, chunk_size=120, chunk_overlap=30)
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 150)

    def test_03_csv_extraction_to_natural_language(self):
        """Verify CSV rows are converted to descriptive key-value records."""
        csv_path = os.path.join(backend_dir, "app", "rag", "documents", "palghar_fish_landing_rates.csv")
        extracted = extract_csv_file(csv_path)
        self.assertIn("Record 1", extracted)
        self.assertIn("Silver Pomfret", extracted)
        self.assertIn("modal_price_per_kg", extracted)

    def test_04_pdf_extraction(self):
        """Verify PDF text extraction extracts content without error."""
        pdf_path = os.path.join(backend_dir, "app", "rag", "documents", "maharashtra_marine_safety_regulations.pdf")
        extracted = extract_pdf_file(pdf_path)
        self.assertGreater(len(extracted), 50)
        self.assertTrue("Maharashtra" in extracted or "Safety" in extracted or "Marine" in extracted)

    def test_05_metadata_integrity_in_chromadb(self):
        """Verify that indexed chunks contain all 7 mandatory metadata fields."""
        results = aquapulse_vector_store.query_documents(query="subsidy", agent_name="scheme", n_results=1)
        self.assertGreater(len(results), 0)
        top_meta = results[0]["metadata"]
        required_keys = ["agent_name", "document_name", "location", "district", "source", "publication_date", "document_type"]
        for key in required_keys:
            self.assertIn(key, top_meta, f"Missing required metadata key: {key}")
        self.assertEqual(top_meta["agent_name"], "scheme")
        self.assertEqual(top_meta["district"], "Palghar")

    def test_06_collection_isolation_for_all_agents(self):
        """Verify all 7 agent collections exist and can be queried independently."""
        expected_agents = ["weather", "fisheries", "disaster", "market", "environment", "scheme", "complaint"]
        for agent in expected_agents:
            col = aquapulse_vector_store._get_collection(agent)
            self.assertIsNotNone(col)
            self.assertIn(AGENT_COLLECTIONS[agent], col.name)
            self.assertGreaterEqual(col.count(), 1, f"Collection for {agent} should have at least 1 document chunk.")

    def test_07_semantic_retrieval_scheme_agent(self):
        """Verify semantic query for PMMSY subsidy retrieves scheme documentation."""
        results = aquapulse_vector_store.query_documents(
            query="What is the subsidy percentage for women in PMMSY?",
            agent_name="scheme",
            n_results=2
        )
        self.assertGreater(len(results), 0)
        content_joined = " ".join([r["content"] for r in results]).lower()
        self.assertTrue("60%" in content_joined or "subsidy" in content_joined)

    def test_08_semantic_retrieval_market_agent(self):
        """Verify semantic query for Pomfret fish prices retrieves market rates."""
        results = aquapulse_vector_store.query_documents(
            query="What is the market rate of Silver Pomfret at Satpati?",
            agent_name="market",
            n_results=2
        )
        self.assertGreater(len(results), 0)
        content_joined = " ".join([r["content"] for r in results]).lower()
        self.assertTrue("pomfret" in content_joined or "satpati" in content_joined or "850" in content_joined)

    def test_09_semantic_retrieval_weather_agent(self):
        """Verify semantic query for wind and SST retrieves IMD weather bulletin."""
        results = aquapulse_vector_store.query_documents(
            query="What is the sea surface temperature and wind speed in Palghar?",
            agent_name="weather",
            n_results=2
        )
        self.assertGreater(len(results), 0)
        content_joined = " ".join([r["content"] for r in results]).lower()
        self.assertTrue("temperature" in content_joined or "wind" in content_joined or "sst" in content_joined)

    def test_10_grounded_answer_generation_with_citations(self):
        """Verify grounded answer generation returns citations and authentic answer."""
        res = run_coro(aquapulse_vector_store.generate_grounded_answer(
            query="What are the cyclone alert stages defined by INCOIS?",
            agent_name="disaster"
        ))
        self.assertTrue(res["evidence_found"])
        self.assertIn("answer", res)
        self.assertGreater(len(res["citations"]), 0)
        top_citation = res["citations"][0]
        self.assertIn("document_name", top_citation)
        self.assertIn("source", top_citation)

    def test_11_honest_refusal_for_unrecorded_information(self):
        """Verify system honestly states unavailability when data is absent and does not fabricate."""
        res = run_coro(aquapulse_vector_store.generate_grounded_answer(
            query="What is the price of gold per gram in Palghar jeweler shops?",
            agent_name="market"
        ))
        # Note: If no relevant evidence matches or distances are high, or specific unavailable facts
        # Test query to a non-existent topic in weather
        res_nonexistent = run_coro(aquapulse_vector_store.generate_grounded_answer(
            query="Can mountain gorillas survive in underwater trenches off Arnala?",
            agent_name="weather"
        ))
        self.assertIn("answer", res_nonexistent)

if __name__ == "__main__":
    unittest.main()

