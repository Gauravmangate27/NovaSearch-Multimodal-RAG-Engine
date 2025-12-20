"""Configuration and utilities for NovaSearch."""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
    OPENAI_LLM_MODEL = "gpt-3.5-turbo"

    # Elasticsearch
    ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
    ELASTICSEARCH_PORT = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
    
    # FAISS
    FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
    FAISS_EMBEDDING_DIM = 1536
    
    # Application
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Search
    DEFAULT_K = 5
    ENABLE_HYBRID_SEARCH = True
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in environment")
        return True

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "openai_api_key": "***" if cls.OPENAI_API_KEY else None,
            "openai_embedding_model": cls.OPENAI_EMBEDDING_MODEL,
            "openai_llm_model": cls.OPENAI_LLM_MODEL,
            "elasticsearch_host": cls.ELASTICSEARCH_HOST,
            "elasticsearch_port": cls.ELASTICSEARCH_PORT,
            "faiss_index_path": cls.FAISS_INDEX_PATH,
            "log_level": cls.LOG_LEVEL,
            "api_host": cls.API_HOST,
            "api_port": cls.API_PORT,
        }


if __name__ == "__main__":
    Config.validate()
    import json
    print(json.dumps(Config.to_dict(), indent=2))
