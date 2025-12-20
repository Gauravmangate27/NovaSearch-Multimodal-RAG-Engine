"""Pydantic models for API requests and responses."""

from typing import List, Optional
from pydantic import BaseModel, Field


class SearchQuery(BaseModel):
    """Search query model."""
    query: str = Field(..., description="Search query text")
    k: int = Field(default=5, description="Number of results to return")
    hybrid: bool = Field(default=True, description="Use hybrid retrieval")


class DocumentInput(BaseModel):
    """Document input model."""
    id: str
    text: str
    type: str = Field(..., description="Document type: 'text' or 'image'")
    source: Optional[str] = None
    description: Optional[str] = None


class SearchResult(BaseModel):
    """Single search result."""
    id: str
    text: str
    type: str
    source: Optional[str] = None
    score: float
    retrieval_type: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response model."""
    query: str
    results: List[SearchResult]
    total_results: int
    execution_time_ms: float


class IndexRequest(BaseModel):
    """Request to index documents."""
    documents: List[DocumentInput]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    indexed_documents: int
