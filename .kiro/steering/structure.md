---
inclusion: always
---

# Project Structure

## Directory Layout

```
qdrant_search_api_v2/
├── app/                      # Application code
│   ├── main.py              # FastAPI application and core logic
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Container build configuration
├── docker-compose.yml       # Service orchestration
├── .env                     # Environment configuration (not in repo)
├── tamplate.env            # Environment template
├── README.md               # Comprehensive documentation
├── LICENSE                 # MIT License
└── directory-structure.txt # Project structure reference
```

## Core Application (`app/main.py`)

### Class Structure

- **SearchSystem**: Main class managing search operations
  - Class-level connection pools (`_qdrant_pool`, `_ollama_pool`) for singleton pattern
  - Collection management and validation
  - Embedding generation via Ollama
  - Context page retrieval with deduplication
  - Batch search processing

### Request Models (Pydantic)

- **SearchRequest**: Standard search with context
  - `collection_name` (required)
  - `search_queries` (required, min 1)
  - `filter` (optional, dict of conditions)
  - `embedding_model` (optional, default: mxbai-embed-large)
  - `limit` (optional, default: 5)
  - `context_window_size` (optional, overrides env var)

- **SimpleSearchRequest**: Lightweight search without context
  - `collection_name` (required)
  - `queries` (required, min 1)
  - `embedding_model` (optional)
  - `limit` (optional)

### Exception Hierarchy

```
SearchException (base)
├── EmbeddingError
└── QdrantConnectionError
```

### API Endpoints

- `GET /health`: Service health check
- `POST /search`: Semantic search with context retrieval
- `POST /simple-search`: Lightweight semantic search

### Middleware

- **Correlation ID Middleware**: Injects UUID for request tracking
- **CORS Middleware**: Allows cross-origin requests

## Code Organization Patterns

### Connection Management
- Singleton pattern for Qdrant and Ollama clients
- Class-level pools initialized on first use
- Connections reused across requests

### Validation
- Pydantic models for request validation
- Payload validation methods for search results
- Type hints throughout codebase

### Logging
- JSON structured logging via `python-json-logger`
- Correlation IDs in all log entries
- Context variables for request tracking
- Log levels: DEBUG, INFO, ERROR, CRITICAL

### Error Handling
- Custom exception classes for different error types
- HTTPException responses with appropriate status codes
- Comprehensive error logging with context

## Configuration Files

- **docker-compose.yml**: Single service definition for search API
- **Dockerfile**: Multi-stage build with Python 3.9-slim base
- **.env**: Runtime configuration (created from tamplate.env)
- **requirements.txt**: Pinned Python dependencies

## Naming Conventions

- **Files**: lowercase with underscores (snake_case)
- **Classes**: PascalCase
- **Functions/Methods**: snake_case
- **Constants**: UPPER_SNAKE_CASE
- **Private methods**: Leading underscore (_method_name)
- **Class-level variables**: Leading underscore (_class_var)

## API Stability Guidelines

When making changes to the codebase:

- **DO NOT** modify existing endpoint paths (/health, /search, /simple-search)
- **DO NOT** change existing request parameter names or behavior (collection_name, search_queries, filter, embedding_model, limit, context_window_size)
- **DO NOT** modify response formats or structures
- **DO** maintain backward compatibility with existing deployments
- **DO** add new optional parameters rather than changing existing ones
- **DO** preserve the current collection_name behavior in all endpoints

Changes should focus on internal implementation (connection management, authentication) without affecting the external API contract.
