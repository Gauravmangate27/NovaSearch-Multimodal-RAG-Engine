"""Unit tests for NovaSearch components."""

import pytest
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.embeddings.multimodal_embedder import MultimodalEmbedder
from src.retrieval.hybrid_retriever import HybridRetriever
from src.ingestion.data_ingester import DataIngester


@pytest.fixture
def embedder():
    """Create embedder fixture."""
    return MultimodalEmbedder()


@pytest.fixture
def retriever(embedder):
    """Create retriever fixture."""
    return HybridRetriever(embedder)


@pytest.fixture
def ingester():
    """Create ingester fixture."""
    return DataIngester()


class TestMultimodalEmbedder:
    """Test multimodal embedding generation."""

    def test_embed_text(self, embedder):
        """Test text embedding."""
        text = "This is a test sentence."
        embedding = embedder.embed_text(text)
        
        assert embedding is not None
        assert isinstance(embedding, list)
        assert len(embedding) > 0

    def test_embed_texts_batch(self, embedder):
        """Test batch text embedding."""
        texts = [
            "First test sentence.",
            "Second test sentence.",
            "Third test sentence."
        ]
        embeddings = embedder.embed_texts_batch(texts)
        
        assert len(embeddings) == len(texts)
        assert all(isinstance(e, list) for e in embeddings)


class TestHybridRetriever:
    """Test hybrid retrieval."""

    def test_retriever_initialization(self, retriever):
        """Test retriever initialization."""
        assert retriever.faiss_index is None
        assert retriever.metadata == []

    def test_initialize_index(self, retriever):
        """Test FAISS index initialization."""
        retriever.initialize_faiss_index(1536)
        assert retriever.faiss_index is not None
        assert retriever.faiss_index.ntotal == 0

    def test_add_documents(self, retriever):
        """Test adding documents."""
        docs = [
            {
                "id": "test1",
                "text": "Test document one",
                "type": "text"
            },
            {
                "id": "test2",
                "text": "Test document two",
                "type": "text"
            }
        ]
        
        retriever.add_documents(docs)
        assert retriever.faiss_index.ntotal == 2

    def test_search(self, retriever):
        """Test search functionality."""
        docs = [
            {
                "id": "test1",
                "text": "Python programming language",
                "type": "text"
            },
            {
                "id": "test2",
                "text": "Java programming language",
                "type": "text"
            }
        ]
        
        retriever.add_documents(docs)
        results = retriever.search("Python", k=2)
        
        assert len(results) > 0
        assert "id" in results[0]
        assert "score" in results[0]


class TestDataIngester:
    """Test data ingestion."""

    def test_ingest_text_file(self, ingester, tmp_path):
        """Test ingesting a text file."""
        # Create temp text file
        test_file = tmp_path / "test.txt"
        test_file.write_text("This is test content for ingestion.")
        
        doc = ingester.ingest_text_file(str(test_file))
        
        assert doc is not None
        assert doc["type"] == "text"
        assert doc["id"] == "test.txt"
        assert "This is test content" in doc["text"]

    def test_chunk_document(self, ingester):
        """Test document chunking."""
        text = "A" * 1000
        chunks = ingester.chunk_document(text, chunk_size=100, overlap=10)
        
        assert len(chunks) > 1
        assert len(chunks[0]) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
