# NovaSearch - Multimodal RAG Engine

A powerful multimodal Retrieval-Augmented Generation (RAG) system that enables semantic search across text and image data using state-of-the-art embeddings and LLM orchestration.

## Features

- **Multimodal Processing**: Semantic search across both text and image data
- **Hybrid Retrieval**: Combines dense vector search (FAISS) with sparse keyword search (Elasticsearch)
- **OpenAI Integration**: Uses OpenAI embeddings and GPT models for intelligent processing
- **Real-time Ingestion**: Efficient document and image ingestion pipeline
- **FastAPI Interface**: RESTful API for easy integration
- **LangChain Orchestration**: LLM workflow management for answer generation and summarization

## Architecture

```
┌─────────────────────────────────────────────┐
│         Data Ingestion Layer                │
│  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Text Files   │  │  Image Files         │ │
│  └──────────────┘  └──────────────────────┘ │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│      Multimodal Embedding Layer             │
│  ┌──────────────────────────────────────┐   │
│  │  OpenAI Embeddings + CLIP Processing │   │
│  └──────────────────────────────────────┘   │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│      Hybrid Retrieval Layer                 │
│  ┌─────────────────┐  ┌─────────────────┐   │
│  │  FAISS Index    │  │  Elasticsearch  │   │
│  │ (Dense Search)  │  │ (Sparse Search) │   │
│  └─────────────────┘  └─────────────────┘   │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│      LLM Orchestration Layer                │
│  ┌──────────────────────────────────────┐   │
│  │  LangChain + GPT Models              │   │
│  │  Answer Generation & Summarization   │   │
│  └──────────────────────────────────────┘   │
└──────────────────────┬──────────────────────┘
                       │
┌──────────────────────▼──────────────────────┐
│      FastAPI REST Interface                 │
└─────────────────────────────────────────────┘
```

## Installation

### Prerequisites
- Python 3.8+
- OpenAI API Key
- Elasticsearch (optional, for hybrid search)

### Setup

1. Clone the repository:
```bash
cd Nova_Search
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Usage

### Starting the Server

```bash
python -m uvicorn src.api.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Index Documents
```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "id": "doc1",
        "text": "Your document content here",
        "type": "text",
        "source": "example.txt"
      }
    ]
  }'
```

#### Search
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "k": 5,
    "hybrid": true
  }'
```

#### Ingest Directory
```bash
curl -X POST "http://localhost:8000/ingest-directory?directory_path=/path/to/documents"
```

### Python Example

```python
from src.embeddings.multimodal_embedder import MultimodalEmbedder
from src.retrieval.hybrid_retriever import HybridRetriever

# Initialize components
embedder = MultimodalEmbedder()
retriever = HybridRetriever(embedder)

# Add documents
documents = [
    {
        "id": "doc1",
        "text": "Python is a programming language",
        "type": "text"
    }
]
retriever.add_documents(documents)

# Search
results = retriever.search("Tell me about Python", k=5)
for result in results:
    print(f"{result['id']}: {result['score']:.2f}")
```

## Components

### 1. Multimodal Embedder (`src/embeddings/multimodal_embedder.py`)
- Generates embeddings for text using OpenAI's embedding models
- Processes images using GPT-4 Vision and converts to embeddings
- Batch processing support for efficiency

### 2. Hybrid Retriever (`src/retrieval/hybrid_retriever.py`)
- Dense retrieval using FAISS for semantic similarity
- Sparse retrieval using Elasticsearch for keyword matching
- Merged ranking combining both approaches

### 3. Data Ingester (`src/ingestion/data_ingester.py`)
- Supports multiple file formats (txt, pdf, md, images)
- Recursive directory ingestion
- Document chunking with overlap

### 4. LLM Orchestrator (`src/api/llm_orchestrator.py`)
- LangChain integration for workflow management
- Answer generation from retrieved documents
- Summarization capabilities

### 5. FastAPI Application (`src/api/main.py`)
- RESTful API for all components
- CORS support for cross-origin requests
- Comprehensive error handling

## Testing

Run unit tests:
```bash
pytest tests/ -v
```

Run example:
```bash
python example_usage.py
```

## Configuration

Environment variables in `.env`:

```
OPENAI_API_KEY=your_api_key_here
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
FAISS_INDEX_PATH=./data/faiss_index
LOG_LEVEL=INFO
```

## Performance Considerations

- **FAISS**: Fast similarity search suitable for large-scale indexing
- **Elasticsearch**: Powerful for full-text search and filtering
- **Hybrid Approach**: Combines strengths of both methods for balanced retrieval
- **Batch Processing**: Efficient embedding generation for multiple documents

## Future Enhancements

- [ ] Kafka integration for real-time streaming
- [ ] Spark Streaming for large-scale processing
- [ ] Advanced caching mechanisms
- [ ] Multi-language support
- [ ] Custom embedding models
- [ ] Relevance feedback loop
- [ ] Document versioning
- [ ] Advanced analytics dashboard

## License

MIT License

## Contributing

Contributions are welcome! Please submit pull requests or issues.

## Support

For issues and questions, please open an issue on the repository.
