# Deployment configuration for NovaSearch

## Docker Deployment

### Build Docker Image
```bash
docker build -t novasearch:latest .
```

### Run Docker Container
```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e ELASTICSEARCH_HOST=elasticsearch \
  novasearch:latest
```

## Kubernetes Deployment

Deploy to Kubernetes cluster:
```bash
kubectl apply -f k8s/
```

## Environment Variables

Required:
- `OPENAI_API_KEY`: Your OpenAI API key

Optional:
- `ELASTICSEARCH_HOST`: Default is "localhost"
- `ELASTICSEARCH_PORT`: Default is 9200
- `LOG_LEVEL`: Default is "INFO"
- `API_HOST`: Default is "0.0.0.0"
- `API_PORT`: Default is 8000

## Production Considerations

1. **API Keys**: Use secret management systems (AWS Secrets Manager, HashiCorp Vault)
2. **Scaling**: Use load balancers with multiple API instances
3. **Monitoring**: Integrate with logging and monitoring systems
4. **Caching**: Implement Redis for result caching
5. **Database**: Use persistent storage for FAISS indexes
6. **Security**: Use authentication and rate limiting

## Performance Optimization

- **Index Sharding**: Distribute FAISS indexes across servers
- **Batch Processing**: Use batch endpoints for large document sets
- **Caching**: Cache frequently accessed results
- **Async Processing**: Use message queues for async indexing
- **Load Balancing**: Distribute requests across multiple instances
