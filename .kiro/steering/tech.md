---
inclusion: always
---

# Technology Stack

## Core Technologies

- **Python**: 3.9+
- **FastAPI**: 0.68+ (REST API framework)
- **Uvicorn**: 0.15+ (ASGI server)
- **Pydantic**: 1.8.2+ (data validation)

## External Services (Required)

- **Qdrant**: Vector database for storing and searching embeddings (gRPC on port 6334, REST on port 6333)
- **Ollama**: Embedding generation service (port 11434)

## Key Libraries

- `qdrant-client`: Qdrant Python client with gRPC support
- `ollama`: Ollama Python client for embedding generation
- `python-dotenv`: Environment variable management
- `python-json-logger`: Structured JSON logging

## Deployment

- **Docker**: Containerized deployment with Python 3.9-slim base image
- **Docker Compose**: Orchestration for local development and production

## Common Commands

### Development

```bash
# Local development (manual)
cd app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Operations

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f search_api

# Rebuild after changes
docker-compose up -d --build

# Stop services
docker-compose down

# Execute commands in container
docker-compose exec search_api bash
```

### Testing

```bash
# Health check
curl http://localhost:8000/health

# Simple search test
curl -X POST http://localhost:8000/simple-search \
  -H "Content-Type: application/json" \
  -d '{"collection_name": "test", "queries": ["test query"], "limit": 3}'

# Standard search with context
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"collection_name": "test", "search_queries": ["test query"], "limit": 3}'
```

## Configuration

Environment variables in `.env` file:
- `QDRANT_HOST`: Qdrant server hostname/IP
- `OLLAMA_HOST`: Ollama server hostname/IP
- `REQUEST_TIMEOUT`: Request timeout in seconds (default: 30)
- `CONTEXT_WINDOW_SIZE`: Default pages before/after match (default: 5)
- `DEBUG`: Enable debug logging (true/false)

## Embedding Models

Default: `mxbai-embed-large`

Available models (via Ollama):
- `mxbai-embed-large`: General purpose (default)
- `bge-m3`: High quality multilingual
- `nomic-embed-text`: Optimized for text
- `all-minilm`: Smaller, faster

Install models: `ollama pull <model-name>`
