# NovaSearch Quick Start Guide

## 1. Environment Setup

Copy the example env file and add your OpenAI API key:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```
OPENAI_API_KEY=sk-your-key-here
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
LOG_LEVEL=INFO
```

## 2. Install Dependencies

Dependencies are already installed via requirements.txt:
```bash
pip install -r requirements.txt
```

## 3. Run the API Server

Start the FastAPI server:
```bash
python -m uvicorn src.api.main:app --reload
```

The server will start at: `http://localhost:8000`

Access the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 4. Quick Test with Example Data

In another terminal, run the example:
```bash
python example_usage.py
```

## 5. Basic API Usage

### Index Documents
```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "id": "intro1",
        "text": "Python is a high-level, interpreted programming language.",
        "type": "text",
        "source": "docs.txt",
        "description": "Introduction to Python"
      }
    ]
  }'
```

### Search
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Python?",
    "k": 5,
    "hybrid": true
  }'
```

### Health Check
```bash
curl http://localhost:8000/health
```

## 6. Project Structure

```
Nova_Search/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI application
│   │   └── llm_orchestrator.py   # LangChain LLM workflows
│   ├── embeddings/
│   │   └── multimodal_embedder.py # Text & image embeddings
│   ├── retrieval/
│   │   └── hybrid_retriever.py    # FAISS + Elasticsearch
│   ├── ingestion/
│   │   └── data_ingester.py       # Document ingestion
│   ├── models/
│   │   └── schemas.py             # Pydantic models
│   └── __init__.py
├── tests/
│   └── test_components.py         # Unit tests
├── data/
│   ├── documents/                 # Text files
│   └── images/                    # Image files
├── .vscode/
│   ├── settings.json
│   ├── launch.json
│   └── tasks.json
├── .env.example                   # Environment template
├── requirements.txt               # Python dependencies
├── README.md                      # Full documentation
├── example_usage.py               # Example script
└── QUICKSTART.md                  # This file
```

## 7. Running Tests

Execute unit tests:
```bash
pytest tests/ -v
```

## 8. VS Code Debugging

Press `F5` or go to Run → Start Debugging to launch:
- **FastAPI Server**: Starts the API with hot reload
- **Run Example**: Executes the example script
- **Run Tests**: Runs the test suite

## 9. Key Features to Explore

1. **Multimodal Search**: Add both text and image documents
2. **Hybrid Retrieval**: Combines dense (FAISS) and sparse (Elasticsearch) search
3. **LLM Integration**: Uses OpenAI for embeddings and answer generation
4. **Batch Indexing**: Efficiently index multiple documents at once

## 10. Next Steps

1. Add your documents to `data/documents/` folder
2. Use `/ingest-directory` endpoint to index them
3. Start searching with the `/search` endpoint
4. Customize the LLM prompts in `llm_orchestrator.py`

## Troubleshooting

### Elasticsearch Connection Issues
If you see warnings about Elasticsearch connection, it's optional. The system works with FAISS only.

### OpenAI API Errors
- Ensure your API key is valid and has available credits
- Check that the key is properly set in `.env`

### Import Errors
Make sure you're running from the project root directory and all dependencies are installed.

## Performance Tips

- Use FAISS for large-scale indexing (millions of documents)
- Enable hybrid search for better relevance ranking
- Batch your embeddings for faster processing
- Consider document chunking for better retrieval

## Support

For issues:
1. Check the logs in the terminal output
2. Review the README.md for detailed documentation
3. Check test cases in `tests/test_components.py` for usage examples
