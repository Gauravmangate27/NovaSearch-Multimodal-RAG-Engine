"""Hybrid retrieval engine combining FAISS and Elasticsearch."""

import os
import logging
from typing import List, Dict, Any, Tuple
import numpy as np
import faiss
from elasticsearch import Elasticsearch
from src.embeddings.multimodal_embedder import MultimodalEmbedder

logger = logging.getLogger(__name__)


class HybridRetriever:
    """Hybrid retrieval system using FAISS for dense retrieval and Elasticsearch for sparse retrieval."""

    def __init__(self, embedder: MultimodalEmbedder, es_host: str = "localhost", es_port: int = 9200):
        """
        Initialize the hybrid retriever.
        
        Args:
            embedder: MultimodalEmbedder instance
            es_host: Elasticsearch host
            es_port: Elasticsearch port
        """
        self.embedder = embedder
        self.faiss_index = None
        self.metadata = []
        
        # Initialize Elasticsearch client
        try:
            self.es_client = Elasticsearch([{"host": es_host, "port": es_port}])
            self.es_client.info()
            logger.info(f"Connected to Elasticsearch at {es_host}:{es_port}")
        except Exception as e:
            logger.warning(f"Could not connect to Elasticsearch: {e}. Running without ES.")
            self.es_client = None

    def initialize_faiss_index(self, dimension: int = 1536):
        """
        Initialize FAISS index.
        
        Args:
            dimension: Embedding dimension
        """
        self.faiss_index = faiss.IndexFlatL2(dimension)
        logger.info(f"Initialized FAISS index with dimension {dimension}")

    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to both FAISS and Elasticsearch indexes.
        
        Args:
            documents: List of documents with 'id', 'text', 'type' (text/image), and optional 'content'
        """
        if self.faiss_index is None:
            self.initialize_faiss_index()

        for doc in documents:
            try:
                # Generate embedding
                if doc["type"] == "text":
                    embedding = self.embedder.embed_text(doc["text"])
                else:  # image
                    embedding = self.embedder.embed_image(doc["content"])

                # Add to FAISS
                embedding_array = np.array([embedding], dtype=np.float32)
                self.faiss_index.add(embedding_array)
                self.metadata.append(doc)

                # Add to Elasticsearch
                if self.es_client:
                    self._index_to_elasticsearch(doc, embedding)

                logger.info(f"Indexed document: {doc['id']}")

            except Exception as e:
                logger.error(f"Error indexing document {doc.get('id')}: {e}")

    def search(
        self, 
        query: str, 
        k: int = 5, 
        hybrid: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search across indexed documents.
        
        Args:
            query: Search query
            k: Number of results
            hybrid: Use hybrid retrieval (combine FAISS and ES)
            
        Returns:
            List of retrieved documents with scores
        """
        results = []

        if hybrid and self.es_client:
            # Hybrid search: combine dense and sparse retrieval
            dense_results = self._dense_search(query, k)
            sparse_results = self._sparse_search(query, k)
            results = self._merge_results(dense_results, sparse_results, k)
        else:
            # Dense search only
            results = self._dense_search(query, k)

        return results

    def _dense_search(self, query: str, k: int) -> List[Dict[str, Any]]:
        """
        Dense retrieval using FAISS.
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of retrieved documents
        """
        if self.faiss_index is None or self.faiss_index.ntotal == 0:
            logger.warning("FAISS index is empty")
            return []

        try:
            # Embed query
            query_embedding = self.embedder.embed_text(query)
            query_array = np.array([query_embedding], dtype=np.float32)

            # Search
            distances, indices = self.faiss_index.search(query_array, min(k, self.faiss_index.ntotal))

            results = []
            for idx, distance in zip(indices[0], distances[0]):
                if idx < len(self.metadata):
                    doc = self.metadata[idx].copy()
                    doc["score"] = float(1 / (1 + distance))  # Convert distance to similarity
                    doc["retrieval_type"] = "dense"
                    results.append(doc)

            return results

        except Exception as e:
            logger.error(f"Error in dense search: {e}")
            return []

    def _sparse_search(self, query: str, k: int) -> List[Dict[str, Any]]:
        """
        Sparse retrieval using Elasticsearch.
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of retrieved documents
        """
        if not self.es_client:
            return []

        try:
            response = self.es_client.search(
                index="novasearch_documents",
                query={
                    "multi_match": {
                        "query": query,
                        "fields": ["text", "description"]
                    }
                },
                size=k
            )

            results = []
            for hit in response["hits"]["hits"]:
                doc = hit["_source"].copy()
                doc["score"] = hit["_score"]
                doc["retrieval_type"] = "sparse"
                results.append(doc)

            return results

        except Exception as e:
            logger.error(f"Error in sparse search: {e}")
            return []

    def _merge_results(
        self, 
        dense_results: List[Dict], 
        sparse_results: List[Dict], 
        k: int
    ) -> List[Dict[str, Any]]:
        """
        Merge and rank results from dense and sparse retrieval.
        
        Args:
            dense_results: Results from FAISS
            sparse_results: Results from Elasticsearch
            k: Number of final results
            
        Returns:
            Merged and ranked results
        """
        # Combine results by ID, averaging scores
        merged = {}
        
        for doc in dense_results:
            doc_id = doc["id"]
            if doc_id not in merged:
                merged[doc_id] = doc.copy()
                merged[doc_id]["combined_score"] = doc["score"] * 0.6
            else:
                merged[doc_id]["combined_score"] += doc["score"] * 0.6

        for doc in sparse_results:
            doc_id = doc["id"]
            if doc_id not in merged:
                merged[doc_id] = doc.copy()
                merged[doc_id]["combined_score"] = doc["score"] * 0.4
            else:
                merged[doc_id]["combined_score"] += doc["score"] * 0.4

        # Sort by combined score
        sorted_results = sorted(merged.values(), key=lambda x: x["combined_score"], reverse=True)
        return sorted_results[:k]

    def _index_to_elasticsearch(self, doc: Dict[str, Any], embedding: List[float]) -> None:
        """
        Index document to Elasticsearch.
        
        Args:
            doc: Document to index
            embedding: Document embedding
        """
        try:
            doc_body = {
                "id": doc["id"],
                "text": doc.get("text", ""),
                "description": doc.get("description", ""),
                "type": doc["type"],
                "embedding": embedding
            }

            self.es_client.index(
                index="novasearch_documents",
                id=doc["id"],
                document=doc_body
            )
        except Exception as e:
            logger.error(f"Error indexing to Elasticsearch: {e}")

    def save_index(self, path: str) -> None:
        """Save FAISS index to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        faiss.write_index(self.faiss_index, path)
        logger.info(f"Saved FAISS index to {path}")

    def load_index(self, path: str) -> None:
        """Load FAISS index from disk."""
        self.faiss_index = faiss.read_index(path)
        logger.info(f"Loaded FAISS index from {path}")
