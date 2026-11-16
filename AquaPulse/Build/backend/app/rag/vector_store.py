import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

import chromadb
from app.core.config import settings
from app.rag.document_loader import load_document, chunk_text
from app.core.ollama_client import ollama_client

logger = logging.getLogger("aquapulse.rag.vectorstore")

# The 7 Specialized Agent Collections
AGENT_COLLECTIONS = {
    "weather": "aquapulse_weather",
    "fisheries": "aquapulse_fisheries",
    "disaster": "aquapulse_disaster",
    "market": "aquapulse_market",
    "environment": "aquapulse_environment",
    "scheme": "aquapulse_scheme",
    "complaint": "aquapulse_complaint"
}

class AquaPulseVectorStore:
    """
    Production ChromaDB RAG Vector Store for AquaPulse.
    Supports 7 dedicated agent collections and consolidated metadata filtering.
    """

    def __init__(self, persist_directory: Optional[str] = None):
        self.persist_directory = persist_directory or settings.CHROMA_PERSIST_DIRECTORY
        os.makedirs(self.persist_directory, exist_ok=True)
        # Initialize persistent Chroma client
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.main_collection = self.client.get_or_create_collection(
            name="aquapulse_master_corpus",
            metadata={"description": "Master multi-agent knowledge base for Palghar coastal safety"}
        )

    def _get_collection(self, agent_name: Optional[str] = None):
        """Returns dedicated agent collection or master collection."""
        if agent_name:
            norm_agent = agent_name.lower().replace(" agent", "").strip()
            col_name = AGENT_COLLECTIONS.get(norm_agent, "aquapulse_master_corpus")
            return self.client.get_or_create_collection(name=col_name)
        return self.main_collection

    def ingest_document(
        self,
        file_path: str,
        agent_name: str,
        document_name: Optional[str] = None,
        location: str = "Palghar",
        district: str = "Palghar",
        source: Optional[str] = None,
        publication_date: Optional[str] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> Dict[str, Any]:
        """
        Loads, extracts, chunks, embeds and indexes a document (PDF, CSV, or TXT)
        with mandatory AquaPulse metadata.
        """
        doc_name = document_name or os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1].lower().replace(".", "")
        pub_date = publication_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        src = source or f"Official {agent_name} Registry"

        # 1. Extract and clean content
        raw_text = load_document(file_path)
        if not raw_text.strip():
            logger.warning(f"No extractable text found in {file_path}")
            return {"status": "empty", "chunks_indexed": 0, "document_name": doc_name}

        # 2. Chunk text
        chunks = chunk_text(raw_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        # 3. Prepare IDs, documents, and metadata
        ids = []
        documents = []
        metadatas = []

        norm_agent = agent_name.lower().replace(" agent", "").strip()

        for idx, chunk in enumerate(chunks):
            chunk_id = f"{doc_name}-chunk-{idx}-{str(uuid.uuid4())[:8]}"
            meta = {
                "agent_name": norm_agent,
                "document_name": doc_name,
                "location": location,
                "district": district,
                "source": src,
                "publication_date": pub_date,
                "document_type": ext,
                "chunk_index": idx,
                "total_chunks": len(chunks)
            }
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append(meta)

        # 4. Store in Dedicated Agent Collection AND Master Collection
        agent_col = self._get_collection(norm_agent)
        agent_col.add(ids=ids, documents=documents, metadatas=metadatas)
        self.main_collection.add(ids=ids, documents=documents, metadatas=metadatas)

        logger.info(f"Indexed {len(chunks)} chunks for '{doc_name}' into collection '{agent_col.name}'")

        return {
            "status": "success",
            "document_name": doc_name,
            "document_type": ext,
            "agent_name": norm_agent,
            "chunks_indexed": len(chunks),
            "source": src
        }

    def query_documents(
        self,
        query: str,
        agent_name: Optional[str] = None,
        location: Optional[str] = None,
        n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Executes semantic vector search with metadata filtering across
        agent collections or master collection.
        """
        collection = self._get_collection(agent_name)
        
        where_filter = {}
        if agent_name:
            norm_agent = agent_name.lower().replace(" agent", "").strip()
            where_filter["agent_name"] = norm_agent
        if location and location.lower() != "palghar":
            where_filter["location"] = location

        kwargs: Dict[str, Any] = {
            "query_texts": [query],
            "n_results": min(n_results, max(collection.count(), 1))
        }
        if where_filter and collection == self.main_collection:
            kwargs["where"] = where_filter

        try:
            results = collection.query(**kwargs)
        except Exception as e:
            logger.warning(f"ChromaDB query fallback: {e}")
            return []

        retrieved_docs = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            dists = results["distances"][0] if "distances" in results else [0.0] * len(docs)

            for d, m, dist in zip(docs, metas, dists):
                # Calculate normalized confidence (lower distance is higher confidence)
                conf = round(max(0.0, min(1.0, 1.0 - (dist / 2.0))), 3) if dist else 0.95
                retrieved_docs.append({
                    "content": d,
                    "metadata": m,
                    "confidence": conf
                })

        return retrieved_docs

    async def generate_grounded_answer(
        self,
        query: str,
        agent_name: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates answers ONLY from retrieved evidence.
        Returns full document references (citations) and handles missing data honestly.
        """
        retrieved = self.query_documents(query=query, agent_name=agent_name, location=location, n_results=3)

        # Handle missing information honestly
        if not retrieved:
            return {
                "answer": "The requested information is not available in verified AquaPulse official documents.",
                "evidence_found": False,
                "citations": [],
                "confidence": 0.0,
                "warnings": ["No matching domain documentation found in knowledge base"]
            }

        # Format retrieved evidence context
        context_blocks = []
        citations = []
        for idx, item in enumerate(retrieved, 1):
            m = item["metadata"]
            citation = {
                "document_name": m.get("document_name", "Official Record"),
                "source": m.get("source", "Government of Maharashtra / CMFRI / IMD"),
                "publication_date": m.get("publication_date", "Recent"),
                "chunk_index": m.get("chunk_index", 0),
                "confidence": item["confidence"]
            }
            citations.append(citation)
            context_blocks.append(f"[{idx}] {item['content']} (Source: {citation['source']}, Doc: {citation['document_name']})")

        context_str = "\n\n".join(context_blocks)

        prompt = (
            f"You are the AquaPulse Knowledge Engine for Palghar, Maharashtra.\n"
            f"Answer the user's question STRICTLY based on the retrieved evidence below.\n"
            f"Never invent or assume facts not present in the evidence.\n"
            f"If the evidence does not answer the question, state that the information is unavailable in official records.\n\n"
            f"Retrieved Evidence:\n{context_str}\n\n"
            f"Question: {query}\n\n"
            f"Grounded Answer:"
        )

        if ollama_client.is_reachable():
            try:
                answer = await ollama_client.generate(prompt=prompt, temperature=0.1)
                answer = answer.strip()
            except Exception:
                answer = self._synthesize_fallback(query, retrieved)
        else:
            answer = self._synthesize_fallback(query, retrieved)

        return {
            "answer": answer,
            "evidence_found": True,
            "citations": citations,
            "confidence": retrieved[0]["confidence"],
            "warnings": []
        }

    def _synthesize_fallback(self, query: str, retrieved: List[Dict[str, Any]]) -> str:
        """Deterministic grounded synthesis when Ollama is offline."""
        top = retrieved[0]
        doc_name = top["metadata"].get("document_name", "Official Record")
        src = top["metadata"].get("source", "Official Department")
        return f"According to {doc_name} ({src}): {top['content']}"

# Singleton vector store instance
aquapulse_vector_store = AquaPulseVectorStore()

