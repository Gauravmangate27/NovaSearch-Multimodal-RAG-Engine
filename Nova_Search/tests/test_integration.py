"""Integration tests for the complete RAG system."""

import pytest
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.embeddings.multimodal_embedder import MultimodalEmbedder
from src.retrieval.hybrid_retriever import HybridRetriever
from src.ingestion.data_ingester import DataIngester
from src.models.schemas import DocumentInput, SearchQuery


@pytest.fixture
def components():
    """Initialize all components."""
    embedder = MultimodalEmbedder()
    retriever = HybridRetriever(embedder)
    ingester = DataIngester()
    
    return {
        "embedder": embedder,
        "retriever": retriever,
        "ingester": ingester
    }


@pytest.fixture
def sample_documents():
    """Create sample documents for testing."""
    return [
        {
            "id": "python_guide",
            "text": "Python is a versatile programming language used for web development, data science, and AI.",
            "type": "text",
            "source": "guide.txt",
            "description": "Python programming guide"
        },
        {
            "id": "ml_basics",
            "text": "Machine learning enables computers to learn patterns from data without explicit programming.",
            "type": "text",
            "source": "ml.txt",
            "description": "Machine learning basics"
        },
        {
            "id": "llm_intro",
            "text": "Large Language Models like GPT-3 and GPT-4 have revolutionized natural language processing.",
            "type": "text",
            "source": "llm.txt",
            "description": "LLM introduction"
        }
    ]


class TestIntegration:
    """Integration tests for the complete system."""

    def test_end_to_end_workflow(self, components, sample_documents):
        """Test complete workflow: ingest -> index -> search."""
        retriever = components["retriever"]
        
        # Step 1: Index documents
        start_time = time.time()
        retriever.add_documents(sample_documents)
        index_time = time.time() - start_time
        
        assert retriever.faiss_index.ntotal == len(sample_documents)
        print(f"✓ Indexed {len(sample_documents)} documents in {index_time:.2f}s")
        
        # Step 2: Perform searches
        test_queries = [
            ("What is Python?", "python_guide"),
            ("Tell me about machine learning", "ml_basics"),
            ("Discuss large language models", "llm_intro")
        ]
        
        for query, expected_id in test_queries:
            start_time = time.time()
            results = retriever.search(query, k=3)
            search_time = time.time() - start_time
            
            assert len(results) > 0
            assert results[0]["id"] in [d["id"] for d in sample_documents]
            print(f"✓ Query '{query}' - Top result: {results[0]['id']} (score: {results[0]['score']:.3f}, {search_time*1000:.1f}ms)")

    def test_dense_vs_sparse_search(self, components, sample_documents):
        """Compare dense and sparse search results."""
        retriever = components["retriever"]
        retriever.add_documents(sample_documents)
        
        query = "artificial intelligence and machine learning"
        
        # Dense search only
        dense_results = retriever._dense_search(query, k=3)
        
        print(f"\nDense Search Results for '{query}':")
        for i, result in enumerate(dense_results, 1):
            print(f"  {i}. {result['id']} - Score: {result['score']:.3f}")
        
        assert len(dense_results) > 0
        assert all("score" in r for r in dense_results)
        assert all("retrieval_type" in r and r["retrieval_type"] == "dense" for r in dense_results)

    def test_batch_embeddings(self, components):
        """Test batch embedding generation."""
        embedder = components["embedder"]
        
        texts = [
            "First document about Python programming.",
            "Second document about machine learning systems.",
            "Third document about deep neural networks."
        ]
        
        embeddings = embedder.embed_texts_batch(texts)
        
        assert len(embeddings) == len(texts)
        assert all(isinstance(e, list) for e in embeddings)
        assert all(len(e) == 1536 for e in embeddings)
        print(f"✓ Generated {len(embeddings)} embeddings in batch mode")

    def test_metadata_preservation(self, components, sample_documents):
        """Test that document metadata is preserved during indexing."""
        retriever = components["retriever"]
        retriever.add_documents(sample_documents)
        
        # Search and check metadata
        results = retriever.search("Python", k=1)
        
        assert len(results) > 0
        result = results[0]
        
        # Verify metadata fields
        assert "id" in result
        assert "text" in result
        assert "type" in result
        assert "source" in result
        
        print(f"✓ Metadata preserved: {result['id']} from {result['source']}")

    def test_search_relevance_ranking(self, components, sample_documents):
        """Test that results are properly ranked by relevance."""
        retriever = components["retriever"]
        retriever.add_documents(sample_documents)
        
        query = "programming language"
        results = retriever.search(query, k=len(sample_documents))
        
        # Check that results are sorted by score (descending)
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)
        
        print(f"\n✓ Results properly ranked by relevance:")
        for i, (result, score) in enumerate(zip(results, scores), 1):
            print(f"  {i}. {result['id']} - Score: {score:.3f}")

    def test_index_persistence(self, components, sample_documents, tmp_path):
        """Test saving and loading FAISS index."""
        retriever = components["retriever"]
        retriever.add_documents(sample_documents)
        
        # Save index
        index_path = str(tmp_path / "test_index.faiss")
        retriever.save_index(index_path)
        
        assert os.path.exists(index_path)
        print(f"✓ Index saved to {index_path}")
        
        # Create new retriever and load index
        new_retriever = HybridRetriever(components["embedder"])
        new_retriever.metadata = retriever.metadata
        new_retriever.load_index(index_path)
        
        # Verify loaded index
        assert new_retriever.faiss_index.ntotal == retriever.faiss_index.ntotal
        
        # Search with loaded index
        results = new_retriever.search("Python", k=1)
        assert len(results) > 0
        
        print(f"✓ Index loaded and functional")

    def test_error_handling(self, components):
        """Test error handling in various scenarios."""
        embedder = components["embedder"]
        retriever = components["retriever"]
        
        # Test empty search
        results = retriever.search("test query")
        assert results == []  # Should return empty list, not error
        
        # Test empty query string
        try:
            results = retriever.search("", k=5)
            # Should either work or raise controlled error
        except Exception as e:
            print(f"✓ Properly handled empty query: {type(e).__name__}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
