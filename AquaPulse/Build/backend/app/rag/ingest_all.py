import os
import sys
import glob
import logging
from typing import Dict, Any, List

# Ensure app is in path when executed directly
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.rag.vector_store import aquapulse_vector_store

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("aquapulse.rag.ingestion")

# Document Manifest with Domain Metadata
DOCUMENT_MANIFEST: Dict[str, Dict[str, Any]] = {
    "pmmsy_guidelines_palghar.txt": {
        "agent_name": "scheme",
        "document_name": "PMMSY Palghar Guidelines 2026",
        "location": "Palghar",
        "district": "Palghar",
        "source": "Department of Fisheries, Ministry of Fisheries, Animal Husbandry & Dairying",
        "publication_date": "2026-01-15"
    },
    "palghar_fish_landing_rates.csv": {
        "agent_name": "market",
        "document_name": "Palghar Fish Landing Market Rates",
        "location": "Satpati",
        "district": "Palghar",
        "source": "Palghar Fishermen Cooperative Societies Federation",
        "publication_date": "2026-03-01"
    },
    "mpcb_coastal_water_quality.csv": {
        "agent_name": "environment",
        "document_name": "MPCB Coastal Water Quality Index Bulletin",
        "location": "Dahanu",
        "district": "Palghar",
        "source": "Maharashtra Pollution Control Board (MPCB)",
        "publication_date": "2026-03-01"
    },
    "incois_disaster_cyclone_protocols.txt": {
        "agent_name": "disaster",
        "document_name": "INCOIS Coastal Cyclone & Tsunami Safety Standard Operating Procedures",
        "location": "Palghar",
        "district": "Palghar",
        "source": "Indian National Centre for Ocean Information Services (INCOIS)",
        "publication_date": "2025-11-20"
    },
    "coastal_illegal_trawling_complaint_rules.txt": {
        "agent_name": "complaint",
        "document_name": "Maharashtra Marine Fishing Complaint Redressal Procedures",
        "location": "Palghar",
        "district": "Palghar",
        "source": "Maharashtra Department of Fisheries Enforcement Wing",
        "publication_date": "2025-08-10"
    },
    "maharashtra_marine_safety_regulations.pdf": {
        "agent_name": "fisheries",
        "document_name": "Maharashtra Marine Fishing Regulation & Safety Act",
        "location": "Palghar",
        "district": "Palghar",
        "source": "Maharashtra Maritime Board & Department of Fisheries",
        "publication_date": "2025-06-01"
    },
    "imd_palghar_coastal_monsoon_bulletin.txt": {
        "agent_name": "weather",
        "document_name": "IMD Regional Specialised Meteorological Bulletin - Palghar",
        "location": "Palghar",
        "district": "Palghar",
        "source": "India Meteorological Department (IMD Mumbai)",
        "publication_date": "2026-03-01"
    }
}

def ingest_all_documents(docs_dir: str = None) -> List[Dict[str, Any]]:
    """
    Scans document directory and indexes all domain documents into ChromaDB
    collections according to metadata specifications.
    """
    if docs_dir is None:
        docs_dir = os.path.join(os.path.dirname(__file__), "documents")

    if not os.path.exists(docs_dir):
        logger.error(f"Documents directory not found at: {docs_dir}")
        return []

    logger.info(f"Starting ingestion from: {docs_dir}")
    files = glob.glob(os.path.join(docs_dir, "*.*"))
    results = []

    for file_path in files:
        base_name = os.path.basename(file_path)
        meta = DOCUMENT_MANIFEST.get(base_name, {
            "agent_name": "fisheries",
            "document_name": base_name,
            "location": "Palghar",
            "district": "Palghar",
            "source": "AquaPulse Knowledge Base",
            "publication_date": "2026-01-01"
        })

        try:
            res = aquapulse_vector_store.ingest_document(
                file_path=file_path,
                agent_name=meta["agent_name"],
                document_name=meta["document_name"],
                location=meta["location"],
                district=meta["district"],
                source=meta["source"],
                publication_date=meta["publication_date"]
            )
            results.append(res)
            logger.info(
                f"Ingested '{base_name}' -> Agent: {res.get('agent_name')} | "
                f"Type: {res.get('document_type')} | Chunks: {res.get('chunks_indexed')}"
            )
        except Exception as e:
            logger.error(f"Failed to ingest {base_name}: {e}", exc_info=True)
            results.append({"status": "failed", "document_name": base_name, "error": str(e)})

    return results

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("==================================================")
    print("      AquaPulse ChromaDB Knowledge Ingestion      ")
    print("==================================================")
    ingested = ingest_all_documents()
    print("\nIngestion Summary:")
    print("-" * 75)
    print(f"{'Document Name':<40} | {'Agent':<12} | {'Chunks':<6} | {'Status'}")
    print("-" * 75)
    for r in ingested:
        doc = r.get("document_name", "Unknown")[:38]
        agent = r.get("agent_name", "Unknown")
        chunks = r.get("chunks_indexed", 0)
        status = r.get("status", "Unknown")
        print(f"{doc:<40} | {agent:<12} | {chunks:<6} | {status}")
    print("-" * 75)
    print("Ingestion complete.\n")

