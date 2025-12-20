"""Data ingestion pipeline for multimodal documents."""

import os
import logging
from typing import List, Dict, Any
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)


class DataIngester:
    """Ingest and process text documents and images."""

    SUPPORTED_TEXT_FORMATS = {".txt", ".pdf", ".md", ".doc", ".docx"}
    SUPPORTED_IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

    def __init__(self):
        """Initialize the data ingester."""
        pass

    def ingest_directory(self, directory: str) -> List[Dict[str, Any]]:
        """
        Recursively ingest all documents and images from a directory.
        
        Args:
            directory: Path to directory
            
        Returns:
            List of ingested documents
        """
        documents = []
        path = Path(directory)

        for file_path in path.rglob("*"):
            if file_path.is_file():
                suffix = file_path.suffix.lower()
                
                if suffix in self.SUPPORTED_TEXT_FORMATS:
                    doc = self.ingest_text_file(str(file_path))
                    if doc:
                        documents.append(doc)
                        
                elif suffix in self.SUPPORTED_IMAGE_FORMATS:
                    doc = self.ingest_image_file(str(file_path))
                    if doc:
                        documents.append(doc)

        logger.info(f"Ingested {len(documents)} documents from {directory}")
        return documents

    def ingest_text_file(self, file_path: str) -> Dict[str, Any]:
        """
        Ingest a text file.
        
        Args:
            file_path: Path to text file
            
        Returns:
            Document dict or None if error
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return {
                "id": os.path.basename(file_path),
                "text": content,
                "type": "text",
                "source": file_path,
                "description": content[:500]  # First 500 chars as description
            }
        except Exception as e:
            logger.error(f"Error ingesting text file {file_path}: {e}")
            return None

    def ingest_image_file(self, file_path: str) -> Dict[str, Any]:
        """
        Ingest an image file.
        
        Args:
            file_path: Path to image file
            
        Returns:
            Document dict or None if error
        """
        try:
            return {
                "id": os.path.basename(file_path),
                "text": f"Image: {os.path.basename(file_path)}",
                "type": "image",
                "source": file_path,
                "content": file_path,
                "description": f"Image from {os.path.basename(file_path)}"
            }
        except Exception as e:
            logger.error(f"Error ingesting image file {file_path}: {e}")
            return None

    def chunk_document(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Input text
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap

        return chunks
