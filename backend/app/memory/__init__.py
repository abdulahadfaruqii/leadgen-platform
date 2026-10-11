"""
Vector memory using ChromaDB for AI context retention.
"""
from typing import List, Dict, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class VectorMemory:
    """ChromaDB-based vector memory for agent context."""

    def __init__(self):
        self.client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
            settings=ChromaSettings(allow_reset=True),
        )
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION
        )

    def add(self, ids: List[str], documents: List[str], metadatas: List[Dict]):
        """Add documents to vector memory."""
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

    def query(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """Query similar documents from memory."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )
        return results

    def delete(self, ids: List[str]):
        """Delete documents from memory."""
        self.collection.delete(ids=ids)


# Singleton
_memory: Optional[VectorMemory] = None


def get_vector_memory() -> VectorMemory:
    global _memory
    if _memory is None:
        _memory = VectorMemory()
    return _memory
