"""FastAPI application for NovaSearch."""

import os
import logging
import time
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.embeddings.multimodal_embedder import MultimodalEmbedder
from src.retrieval.hybrid_retriever import HybridRetriever
from src.ingestion.data_ingester import DataIngester
from src.models.schemas import (
    SearchQuery,
    SearchResponse,
    SearchResult,
    IndexRequest,
    HealthResponse,
    DocumentInput
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NovaSearch",
    description="Multimodal RAG Engine",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global components
embedder = None
retriever = None
ingester = None


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global embedder, retriever, ingester
    
    try:
        logger.info("Initializing NovaSearch components...")
        
        # Initialize embedder
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        
        embedder = MultimodalEmbedder(openai_api_key=openai_api_key)
        logger.info("✓ Embedder initialized")
        
        # Initialize retriever
        es_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        es_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        retriever = HybridRetriever(embedder, es_host=es_host, es_port=es_port)
        logger.info("✓ Retriever initialized")
        
        # Initialize ingester
        ingester = DataIngester()
        logger.info("✓ Ingester initialized")
        
        logger.info("NovaSearch startup complete!")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        indexed_count = retriever.faiss_index.ntotal if retriever and retriever.faiss_index else 0
        return HealthResponse(
            status="healthy",
            indexed_documents=indexed_count
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            indexed_documents=0
        )


@app.post("/search", response_model=SearchResponse)
async def search(query_request: SearchQuery):
    """
    Search across indexed documents.
    
    Args:
        query_request: Search query
        
    Returns:
        Search results with scores
    """
    if not retriever or not retriever.faiss_index:
        raise HTTPException(status_code=503, detail="Retriever not initialized")
    
    try:
        start_time = time.time()
        
        # Perform search
        results = retriever.search(
            query=query_request.query,
            k=query_request.k,
            hybrid=query_request.hybrid
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        # Format results
        formatted_results = [
            SearchResult(
                id=result["id"],
                text=result.get("text", "")[:200],  # Truncate for response
                type=result["type"],
                source=result.get("source"),
                score=result["score"],
                retrieval_type=result.get("retrieval_type")
            )
            for result in results
        ]
        
        return SearchResponse(
            query=query_request.query,
            results=formatted_results,
            total_results=len(formatted_results),
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Error during search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index")
async def index_documents(request: IndexRequest):
    """
    Index documents for retrieval.
    
    Args:
        request: Index request with documents
        
    Returns:
        Success message
    """
    if not retriever:
        raise HTTPException(status_code=503, detail="Retriever not initialized")
    
    try:
        # Convert Pydantic models to dicts
        documents = [doc.dict() for doc in request.documents]
        
        # Index documents
        retriever.add_documents(documents)
        
        return {
            "status": "success",
            "message": f"Indexed {len(documents)} documents",
            "total_indexed": retriever.faiss_index.ntotal if retriever.faiss_index else 0
        }
        
    except Exception as e:
        logger.error(f"Error during indexing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest-directory")
async def ingest_directory(directory_path: str):
    """
    Ingest all documents from a directory.
    
    Args:
        directory_path: Path to directory
        
    Returns:
        Ingestion status
    """
    if not ingester or not retriever:
        raise HTTPException(status_code=503, detail="Components not initialized")
    
    try:
        if not os.path.exists(directory_path):
            raise HTTPException(status_code=400, detail="Directory not found")
        
        # Ingest documents
        documents = ingester.ingest_directory(directory_path)
        
        if documents:
            retriever.add_documents(documents)
        
        return {
            "status": "success",
            "message": f"Ingested {len(documents)} documents from {directory_path}",
            "total_indexed": retriever.faiss_index.ntotal if retriever.faiss_index else 0
        }
        
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "NovaSearch",
        "description": "Multimodal RAG Engine",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "search": "/search",
            "index": "/index",
            "ingest": "/ingest-directory"
        }
    }
