"""Multimodal embedding generation using OpenAI and CLIP."""

import os
from typing import List, Union
import numpy as np
from openai import OpenAI
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class MultimodalEmbedder:
    """Generate embeddings for text and images using OpenAI and CLIP."""

    def __init__(self, openai_api_key: str = None, model: str = "text-embedding-3-small"):
        """
        Initialize the multimodal embedder.
        
        Args:
            openai_api_key: OpenAI API key
            model: Embedding model to use
        """
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.embedding_dim = 1536 if "3-small" in model else 1536

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error embedding text: {e}")
            raise

    def embed_texts_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            # Sort by index to maintain order
            embeddings = sorted(response.data, key=lambda x: x.index)
            return [e.embedding for e in embeddings]
        except Exception as e:
            logger.error(f"Error embedding texts batch: {e}")
            raise

    def embed_image(self, image_path: str) -> List[float]:
        """
        Generate embedding for image using CLIP description.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Embedding vector
        """
        try:
            # Load and process image
            image = Image.open(image_path)
            # For now, we'll use image description via OpenAI Vision
            # In production, you might want to use CLIP directly
            
            # Convert image to base64 for API
            import base64
            from io import BytesIO
            
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Get image description from GPT-4V
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_str}",
                                },
                            },
                            {
                                "type": "text",
                                "text": "Describe this image in detail for semantic search indexing."
                            }
                        ],
                    }
                ],
                max_tokens=300,
            )
            
            description = response.choices[0].message.content
            # Embed the description
            return self.embed_text(description)
            
        except Exception as e:
            logger.error(f"Error embedding image: {e}")
            raise

    def embed_images_batch(self, image_paths: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple images.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for path in image_paths:
            try:
                embedding = self.embed_image(path)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Error embedding image {path}: {e}")
                embeddings.append(None)
        
        return embeddings
