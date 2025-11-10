# Qdrant Search API v2 - Advanced Semantic Search Engine

> A production-ready FastAPI-based semantic search engine with advanced filtering, context-aware retrieval, and intelligent deduplication. Powered by Qdrant vector database and Ollama embeddings.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Advanced Usage](#advanced-usage)
- [Code Architecture](#code-architecture)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**Qdrant Search API v2** is an advanced semantic search engine that bridges the gap between modern vector databases and language models. It provides a sophisticated REST API for performing semantic searches across document collections with intelligent context retrieval and advanced filtering capabilities.

### What Makes v2 Different?

v2 introduces significant improvements over v1:

- **Dynamic Context Windows**: Configure context retrieval per-request or globally via environment variables
- **Intelligent Deduplication**: Prevents duplicate pages from appearing across multiple search results
- **Advanced Filtering**: Support for array-based filters, enabling complex metadata queries
- **Dual Search Endpoints**: Both context-aware and lightweight search options
- **Per-Request Configuration**: Override default settings on a per-request basis
- **Production-Grade Logging**: Correlation IDs for request tracing across distributed systems
- **Connection Pooling**: Efficient resource management with connection reuse

---

## Key Features

### 🔍 Semantic Search
- **Vector-Based Matching**: Uses embeddings to find semantically similar content, not just keyword matches
- **Multiple Embedding Models**: Support for any Ollama embedding model (mxbai-embed-large, bge-m3, nomic-embed-text, etc.)
- **Batch Query Processing**: Process multiple queries in a single request for efficiency

### 📄 Context-Aware Retrieval
- **Dynamic Context Windows**: Retrieve surrounding pages (configurable: ±1 to ±N pages)
- **Intelligent Aggregation**: Combines matched content with surrounding context for better understanding
- **Page-Level Deduplication**: Prevents the same page from appearing multiple times across results

### 🔒 Advanced Filtering
- **Text Matching**: Filter by text fields with single or multiple values
- **Value Matching**: Filter by numeric, boolean, or categorical fields
- **Array Support**: Use arrays for complex OR conditions within a single filter
- **Composite Filters**: Combine multiple filters with AND logic

### 🩺 Production Features
- **Health Checks**: Monitor service and dependency status
- **Correlation IDs**: Track requests across distributed systems
- **JSON Logging**: Structured logging for easy parsing and analysis
- **CORS Support**: Cross-origin resource sharing enabled by default
- **Error Handling**: Comprehensive error responses with meaningful messages
- **Connection Pooling**: Reuse connections to Qdrant and Ollama for performance

### 🐳 Deployment Ready
- **Docker Support**: Includes Dockerfile for containerized deployment
- **Docker Compose**: Pre-configured for local development
- **Environment Configuration**: All settings via .env file
- **Timeout Management**: Configurable request timeouts

---

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Application                        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Qdrant Search API v2 (FastAPI)                 │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Request Validation & Middleware                      │  │
│  │ - Correlation ID injection                           │  │
│  │ - CORS handling                                      │  │
│  │ - Request logging                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────▼──────────────────────────────┐  │
│  │ SearchSystem Class (Connection Pooling)             │  │
│  │ - Qdrant client pool                                │  │
│  │ - Ollama client pool                                │  │
│  │ - Collection management                             │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │                                    │
│         ┌───────────────┼───────────────┐                  │
│         ▼               ▼               ▼                  │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐        │
│  │ Embedding  │  │  Filtering │  │ Context      │        │
│  │ Generation │  │  Engine    │  │ Aggregation  │        │
│  │ (Ollama)   │  │ (Qdrant)   │  │ & Dedup      │        │
│  └────────────┘  └────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    ┌─────────┐          ┌─────────┐        ┌──────────┐
    │ Ollama  │          │ Qdrant  │        │ Qdrant   │
    │ Service │          │ Vector  │        │ Vector   │
    │         │          │ DB      │        │ DB       │
    └─────────┘          └─────────┘        └──────────┘
```

### Request Flow Diagram

```
1. Client sends search request
   ↓
2. FastAPI validates request with Pydantic models
   ↓
3. Correlation ID middleware adds tracking ID
   ↓
4. SearchSystem instantiated with collection name
   ↓
5. For each query:
   a. Generate embedding via Ollama
   b. Search Qdrant with embedding vector
   c. Retrieve context pages around matches
   d. Deduplicate pages across results
   ↓
6. Aggregate and format results
   ↓
7. Return JSON response with correlation ID
```

---

## Prerequisites

### System Requirements
- **Docker**: 20.10+ and Docker Compose v2+
- **RAM**: Minimum 4GB (8GB+ recommended)
- **Disk Space**: 2GB+ for models and data
- **Network**: Access to external Qdrant and Ollama services

### External Services (Required)

This application is designed to run as a **containerized microservice** that connects to external Qdrant and Ollama services. You must have these services running and accessible:

#### **Qdrant Vector Database**
- **Purpose**: Stores and searches vector embeddings
- **Default Ports**: 6333 (REST API) / 6334 (gRPC)
- **Setup Options**:
  - Self-hosted: `docker run -p 6333:6333 qdrant/qdrant`
  - Cloud: Qdrant Cloud service
  - Local: Download from https://qdrant.tech/
- **Requirements**: At least one collection must exist

#### **Ollama Embedding Service**
- **Purpose**: Generates vector embeddings from text
- **Default Port**: 11434
- **Setup**: 
  ```bash
  # Install Ollama
  curl -fsSL https://ollama.ai/install.sh | sh
  
  # Pull embedding models
  ollama pull mxbai-embed-large
  ollama pull bge-m3
  ```
- **Requirements**: At least one embedding model installed

---

## Quick Start with Docker (Recommended)

### Step 1: Clone and Configure
```bash
# Clone the repository
git clone https://github.com/Crypto-Gi/qdrant_search_api_v2.git
cd qdrant_search_api_v2

# Create environment configuration
cp tamplate.env .env
```

### Step 2: Configure External Services
Edit `.env` file with your service endpoints:
```bash
# External Services Configuration
QDRANT_HOST=192.168.1.100    # Your Qdrant server IP
OLLAMA_HOST=192.168.1.101     # Your Ollama server IP

# Application Settings
DEBUG=false
REQUEST_TIMEOUT=30
CONTEXT_WINDOW_SIZE=5
```

### Step 3: Start the API Container
```bash
# Using Docker Compose (Recommended)
docker-compose up -d

# Or using Docker directly
docker build -t qdrant-search-api-v2 ./app
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name qdrant-search-api-v2 \
  qdrant-search-api-v2
```

### Step 4: Verify Installation
```bash
# Check container status
docker-compose ps

# Test health endpoint
curl http://localhost:8000/health

# View logs
docker-compose logs -f search_api
```

---

## Installation Methods

### Method 1: Docker Compose (Production Recommended)

**Best for**: Production deployments, development environments

```bash
# 1. Clone and configure
git clone https://github.com/Crypto-Gi/qdrant_search_api_v2.git
cd qdrant_search_api_v2
cp tamplate.env .env

# 2. Edit .env with your service IPs
nano .env

# 3. Start the service
docker-compose up -d

# 4. Verify
curl http://localhost:8000/health
```

### Method 2: Docker Build (Custom Deployments)

**Best for**: Custom container orchestration, Kubernetes

```bash
# 1. Clone repository
git clone https://github.com/Crypto-Gi/qdrant_search_api_v2.git
cd qdrant_search_api_v2

# 2. Build container
docker build -t qdrant-search-api-v2 ./app

# 3. Run with environment variables
docker run -d \
  -p 8000:8000 \
  -e QDRANT_HOST=your-qdrant-host \
  -e OLLAMA_HOST=your-ollama-host \
  -e DEBUG=false \
  --name qdrant-search-api-v2 \
  qdrant-search-api-v2
```

### Method 3: Manual Installation (Development Only)

**Best for**: Local development, debugging

```bash
# 1. Prerequisites
python --version  # Requires 3.9+
pip --version

# 2. Clone and setup
git clone https://github.com/Crypto-Gi/qdrant_search_api_v2.git
cd qdrant_search_api_v2

# 3. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r app/requirements.txt

# 5. Configure environment
cp tamplate.env .env
# Edit .env with your service IPs

# 6. Start development server
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# ===== Global Settings =====
ENVIRONMENT=development              # "development" or "production"
DEBUG=false                          # Enable debug logging
REQUEST_TIMEOUT=30                   # Request timeout in seconds

# ===== Development Environment Configuration =====
# Used when use_production=false (default) or when PROD_* variables are not set
DEV_QDRANT_URL=http://localhost:6333
DEV_QDRANT_API_KEY=
DEV_QDRANT_VERIFY_SSL=false

# ===== Production Environment Configuration =====
# Used when use_production=true in API requests
PROD_QDRANT_URL=https://qdrant.example.com:6333
PROD_QDRANT_API_KEY=your-production-api-key-here
PROD_QDRANT_VERIFY_SSL=true

# ===== Fallback Configuration (Backward Compatibility) =====
# Used if environment-specific (DEV_*/PROD_*) variables are not set
QDRANT_URL=
QDRANT_API_KEY=
QDRANT_VERIFY_SSL=true
QDRANT_HOST=192.168.153.47           # Legacy fallback

# ===== SSL Configuration =====
QDRANT_FORCE_IGNORE_SSL=false        # Force ignore SSL (dev only!)

# ===== Other Services =====
OLLAMA_HOST=192.168.153.46
```

### Configuration Details

#### Core Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ENVIRONMENT` | string | `development` | Environment mode: "development" or "production" |
| `DEBUG` | bool | `false` | Enable verbose logging for development/debugging |
| `REQUEST_TIMEOUT` | int | `30` | Maximum seconds to wait for external service responses |
| `OLLAMA_HOST` | string | `192.168.153.46` | Hostname or IP address of Ollama service |

#### Development Environment (DEV_*)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DEV_QDRANT_URL` | string | `""` | Development Qdrant URL (e.g., http://localhost:6333) |
| `DEV_QDRANT_API_KEY` | string | `""` | Development Qdrant API key (optional) |
| `DEV_QDRANT_VERIFY_SSL` | bool | `false` | Verify SSL certificates in development |

#### Production Environment (PROD_*)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PROD_QDRANT_URL` | string | `""` | Production Qdrant URL (must use https://) |
| `PROD_QDRANT_API_KEY` | string | `""` | Production Qdrant API key (required in production) |
| `PROD_QDRANT_VERIFY_SSL` | bool | `true` | Verify SSL certificates in production |

#### Fallback Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `QDRANT_URL` | string | `""` | Generic Qdrant URL (used if DEV_*/PROD_* not set) |
| `QDRANT_API_KEY` | string | `""` | Generic Qdrant API key |
| `QDRANT_VERIFY_SSL` | bool | `true` | Generic SSL verification setting |
| `QDRANT_HOST` | string | `192.168.153.47` | Legacy hostname (used if no URL provided) |
| `QDRANT_FORCE_IGNORE_SSL` | bool | `false` | Force ignore SSL verification (overrides all other SSL settings) |

### Configuration Priority

The system uses the following priority order for each setting:

1. **Request Parameters** (highest priority) - `qdrant_url`, `qdrant_api_key`, `qdrant_verify_ssl` in API request
2. **Environment-Specific Variables** - `DEV_*` or `PROD_*` based on `use_production` flag
3. **Generic Environment Variables** - `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_VERIFY_SSL`
4. **Legacy Fallback** - `QDRANT_HOST` with `http://` prefix
5. **Hardcoded Defaults** (lowest priority)

### Dual Environment Setup

Configure both development and production environments in the same `.env` file:

```bash
# Development (local testing)
DEV_QDRANT_URL=http://localhost:6333
DEV_QDRANT_API_KEY=
DEV_QDRANT_VERIFY_SSL=false

# Production (secure deployment)
PROD_QDRANT_URL=https://qdrant.prod.example.com:6333
PROD_QDRANT_API_KEY=prod-secret-key-12345
PROD_QDRANT_VERIFY_SSL=true
```

Switch between environments using the `use_production` flag in API requests (see examples below).

### Connection Pooling

The API uses dual connection pooling for efficiency:
- **Development Pool**: Reused across requests with `use_production=false`
- **Production Pool**: Reused across requests with `use_production=true`
- **Custom Clients**: Created per-request when using custom Qdrant parameters
- **Ollama Client**: Single pool reused across all requests
- **gRPC Protocol**: Used for Qdrant (faster than REST)
- **Connection Timeout**: 10 seconds per connection

### Security Best Practices

1. **Production Mode**: Always use HTTPS with API key authentication
2. **API Keys**: Store in environment variables, never commit to version control
3. **SSL Verification**: Keep enabled in production (`PROD_QDRANT_VERIFY_SSL=true`)
4. **Force Ignore SSL**: Only use `QDRANT_FORCE_IGNORE_SSL=true` for development with self-signed certificates
5. **Secrets Management**: Consider using AWS Secrets Manager or HashiCorp Vault for production

### Migration from v1

Existing deployments continue to work without changes:

```bash
# v1 Configuration (still works)
QDRANT_HOST=192.168.153.47
OLLAMA_HOST=192.168.153.46

# Migrate to v2 with HTTPS and API key
QDRANT_URL=https://192.168.153.47:6333
QDRANT_API_KEY=your-api-key
QDRANT_VERIFY_SSL=true

# Or use dual environment setup
DEV_QDRANT_URL=http://192.168.153.47:6333
PROD_QDRANT_URL=https://qdrant.prod.com:6333
PROD_QDRANT_API_KEY=prod-key
```

---

## API Reference

### Base URL
```
http://localhost:8000
```

### Endpoints Overview

| Method | Endpoint | Purpose | Context |
|--------|----------|---------|---------|
| `GET` | `/health` | Check service status | N/A |
| `POST` | `/search` | Semantic search with context | ✅ Yes |
| `POST` | `/simple-search` | Lightweight semantic search | ❌ No |

---

### 1. Health Check Endpoint

**Purpose**: Verify that the API and its dependencies are operational.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "ok",
  "services": {
    "qdrant": "ok",
    "ollama": "ok"
  }
}
```

**Status Values**:
- `"ok"`: Service is connected and operational
- `"offline"`: Service has not been initialized yet

---

### 2. Standard Search Endpoint (with Context)

**Purpose**: Perform semantic search with intelligent context retrieval and deduplication.

**Endpoint**: `POST /search`

**Request Body**:
```json
{
  "collection_name": "my_documents",
  "search_queries": ["query1", "query2"],
  "filter": {
    "metadata.field_name": {
      "match_text": "value"
    }
  },
  "embedding_model": "mxbai-embed-large",
  "limit": 5,
  "context_window_size": 3
}
```

**Request Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `collection_name` | string | ✅ Yes | - | Name of the Qdrant collection to search |
| `search_queries` | array[string] | ✅ Yes | - | List of search queries (1 or more) |
| `filter` | object | ❌ No | null | Metadata filters to narrow results |
| `embedding_model` | string | ❌ No | `mxbai-embed-large` | Ollama embedding model name |
| `limit` | integer | ❌ No | `5` | Maximum results per query (≥1) |
| `use_production` | boolean | ❌ No | `false` | Use production environment configuration (PROD_* variables) |
| `qdrant_url` | string | ❌ No | null | Override Qdrant URL for this request |
| `qdrant_api_key` | string | ❌ No | null | Override Qdrant API key for this request |
| `qdrant_verify_ssl` | boolean | ❌ No | null | Override SSL verification for this request |

**Filter Operators Reference**:

| Operator | Type | Value Type | Logic | Description |
|----------|------|------------|-------|-------------|
| `match_text` | Text | string or array[string] | OR within field | Match text fields (single value or array for OR logic) |
| `match_value` | Exact | any or array[any] | OR within field | Match exact values (numbers, booleans, strings, or arrays) |
| `gte` | Range | number | - | Greater than or equal to (numeric fields only) |
| `lte` | Range | number | - | Less than or equal to (numeric fields only) |

**Filter Logic Rules**:
- Multiple values in an array use **OR logic** (match ANY value)
- Multiple fields use **AND logic** (ALL conditions must match)
- Range operators (`gte`/`lte`) can be combined on the same field
- All filter types can be combined in a single request

**Response**:
```json
{
  "results": [
    [
      {
        "filename": "document.pdf",
        "score": 0.89,
        "center_page": 12,
        "combined_page": "Full text from pages 9-15...",
        "page_numbers": [9, 10, 11, 12, 13, 14, 15]
      }
    ]
  ]
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `results` | array[array[object]] | Nested array: outer array per query, inner array per result |
| `filename` | string | Source document filename |
| `score` | float | Semantic similarity score (0-1, higher is better) |
| `center_page` | integer | Page number of the matched content |
| `combined_page` | string | Concatenated text from all context pages |
| `page_numbers` | array[integer] | List of page numbers included in context |

**Example Request (Basic)**:
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "research_papers",
    "search_queries": ["machine learning applications"],
    "filter": {
      "metadata.year": {"match_value": 2023}
    },
    "limit": 3,
    "embedding_model": "mxbai-embed-large"
  }'
```

**Example Request (Using Development Environment - Default)**:
```bash
# Uses DEV_QDRANT_URL, DEV_QDRANT_API_KEY from .env
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "test_docs",
    "search_queries": ["API authentication"],
    "use_production": false,
    "limit": 5
  }'
```

**Example Request (Using Production Environment)**:
```bash
# Uses PROD_QDRANT_URL, PROD_QDRANT_API_KEY from .env
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "production_docs",
    "search_queries": ["deployment strategies"],
    "use_production": true,
    "limit": 5
  }'
```

**Example Request (Custom Qdrant Parameters)**:
```bash
# Override Qdrant connection for this request only
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "staging_docs",
    "search_queries": ["testing procedures"],
    "qdrant_url": "https://staging.qdrant.com:6333",
    "qdrant_api_key": "staging-api-key",
    "qdrant_verify_ssl": true,
    "limit": 5
  }'
```

**Example Request (Invalid - Conflicting Parameters)**:
```bash
# This will return HTTP 400 Bad Request
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "docs",
    "search_queries": ["query"],
    "use_production": true,
    "qdrant_url": "https://custom.qdrant.com:6333"
  }'

# Error response:
# {
#   "detail": "Cannot use both use_production flag and custom Qdrant parameters"
# }
```

---

### 3. Simple Search Endpoint (Lightweight)

**Purpose**: Perform fast semantic search without context retrieval, ideal for quick lookups.

**Endpoint**: `POST /simple-search`

**Request Body**:
```json
{
  "collection_name": "my_documents",
  "queries": ["query1", "query2"],
  "embedding_model": "mxbai-embed-large",
  "limit": 5
}
```

**Request Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `collection_name` | string | ✅ Yes | - | Name of the Qdrant collection to search |
| `queries` | array[string] | ✅ Yes | - | List of search queries (1 or more) |
| `embedding_model` | string | ❌ No | `mxbai-embed-large` | Ollama embedding model name |
| `limit` | integer | ❌ No | `5` | Maximum results per query (≥1) |

**Response**:
```json
{
  "status": "success",
  "queries": ["query1", "query2"],
  "total_results": 5,
  "hits": [
    {
      "id": "point_id_123",
      "score": 0.88,
      "payload": {
        "pagecontent": "Relevant text content...",
        "metadata": {
          "filename": "document.pdf",
          "page_number": 15
        }
      },
      "matching_query": "query1"
    }
  ]
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Operation status: `"success"` or `"error"` |
| `queries` | array[string] | Original search queries |
| `total_results` | integer | Total number of unique results |
| `hits` | array[object] | Array of matching documents |
| `id` | string | Unique point ID in Qdrant |
| `score` | float | Semantic similarity score (0-1) |
| `payload` | object | Full document payload from Qdrant |
| `matching_query` | string | Which query this result matched |

**Example Request**:
```bash
curl -X POST http://localhost:8000/simple-search \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "knowledge_base",
    "queries": ["kubernetes deployment"],
    "limit": 5,
    "embedding_model": "bge-m3"
  }'
```

---

## Comprehensive Examples

### 1. Health Check Endpoint

The health check endpoint verifies that the API and all its dependencies are operational.

#### Example 1.1: Basic Health Check

**Request:**
```bash
curl -X GET "http://localhost:8000/health"
```

**Response (All Services OK):**
```json
{
  "status": "ok",
  "services": {
    "qdrant": "ok",
    "ollama": "ok"
  }
}
```

**Response (Service Offline):**
```json
{
  "status": "ok",
  "services": {
    "qdrant": "offline",
    "ollama": "ok"
  }
}
```

**Use Case**: Call this endpoint before making search requests to ensure all services are available. Useful for monitoring and health checks in production.

---

### 2. Standard Search Endpoint (with Context)

The `/search` endpoint performs semantic search with intelligent context retrieval and deduplication.

#### Example 2.1: Simple Search with Single Query

**Request:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "research_papers",
    "search_queries": ["machine learning applications in healthcare"],
    "limit": 3,
    "embedding_model": "mxbai-embed-large"
  }'
```

**Response:**
```json
{
  "results": [
    [
      {
        "filename": "healthcare_ml_2023.pdf",
        "score": 0.92,
        "center_page": 15,
        "combined_page": "Machine learning has revolutionized healthcare diagnostics... [full context from pages 13-17]",
        "page_numbers": [13, 14, 15, 16, 17]
      },
      {
        "filename": "ai_medical_review.pdf",
        "score": 0.87,
        "center_page": 8,
        "combined_page": "Clinical applications of AI and ML are expanding rapidly... [full context from pages 6-10]",
        "page_numbers": [6, 7, 8, 9, 10]
      }
    ]
  ]
}
```

**Key Points:**
- Single query in array format
- Returns context pages (default ±5 pages)
- Results sorted by relevance score
- Nested array structure: outer array per query, inner array per result

---

#### Example 2.2: Multiple Queries in Single Request

**Request:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "technical_docs",
    "search_queries": [
      "API authentication methods",
      "rate limiting strategies",
      "error handling best practices"
    ],
    "limit": 2,
    "embedding_model": "mxbai-embed-large",
    "context_window_size": 2
  }'
```

**Response:**
```json
{
  "results": [
    [
      {
        "filename": "api_security_guide.pdf",
        "score": 0.95,
        "center_page": 12,
        "combined_page": "OAuth 2.0 and JWT are the most common authentication methods... [context from pages 11-13]",
        "page_numbers": [11, 12, 13]
      }
    ],
    [
      {
        "filename": "api_design_patterns.pdf",
        "score": 0.89,
        "center_page": 25,
        "combined_page": "Rate limiting can be implemented using token bucket algorithm... [context from pages 24-26]",
        "page_numbers": [24, 25, 26]
      }
    ],
    [
      {
        "filename": "error_handling_guide.pdf",
        "score": 0.91,
        "center_page": 8,
        "combined_page": "Proper error handling includes validation, logging, and user-friendly messages... [context from pages 7-9]",
        "page_numbers": [7, 8, 9]
      }
    ]
  ]
}
```

**Key Points:**
- Three separate queries processed in one request
- Each query gets its own result array
- Smaller context window (±2 pages)
- More efficient than three separate API calls

---

#### Example 2.3: Search with Text Filter (Single Value)

**Request:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "company_documents",
    "search_queries": ["quarterly revenue growth"],
    "filter": {
      "metadata.document_type": {
        "match_text": "financial_report"
      }
    },
    "limit": 5,
    "embedding_model": "mxbai-embed-large"
  }'
```

**Response:**
```json
{
  "results": [
    [
      {
        "filename": "Q3_2023_Financial_Report.pdf",
        "score": 0.93,
        "center_page": 18,
        "combined_page": "Q3 revenue reached $2.5B, representing 15% YoY growth... [context]",
        "page_numbers": [16, 17, 18, 19, 20]
      }
    ]
  ]
}
```

**Key Points:**
- Filters results to only financial_report documents
- Single text value filter
- Only matching documents returned

---

#### Example 2.4: Search with Text Filter (Multiple Values - OR Logic)

**Request:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "knowledge_base",
    "search_queries": ["deployment strategies"],
    "filter": {
      "metadata.category": {
        "match_text": ["devops", "infrastructure", "cloud"]
      }
    },
    "limit": 4,
    "embedding_model": "bge-m3"
  }'
```

**Response:**
```json
{
  "results": [
    [
      {
        "filename": "kubernetes_deployment.md",
        "score": 0.94,
        "center_page": 5,
        "combined_page": "Kubernetes provides orchestration for containerized deployments... [context]",
        "page_numbers": [3, 4, 5, 6, 7]
      },
      {
        "filename": "aws_deployment_guide.md",
        "score": 0.88,
        "center_page": 12,
        "combined_page": "AWS offers multiple deployment options including EC2, ECS, and Lambda... [context]",
        "page_numbers": [10, 11, 12, 13, 14]
      },
      {
        "filename": "docker_best_practices.md",
        "score": 0.85,
        "center_page": 8,
        "combined_page": "Docker containers enable consistent deployment across environments... [context]",
        "page_numbers": [6, 7, 8, 9, 10]
      }
    ]
  ]
}
```

**Key Points:**
- Array of text values acts as OR condition
- Returns documents matching ANY of the categories
- Useful for broad searches across multiple categories

---

#### Example 2.5: Search with Value Filter (Numeric)

**Request:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "research_papers",
    "search_queries": ["neural network optimization"],
    "filter": {
      "metadata.publication_year": {
        "match_value": 2023
      },
      "metadata.citation_count": {
        "match_value": [50, 100, 150]
      }
    },
    "limit": 3,
    "embedding_model": "bge-m3"
  }'
```

**Response:**
```json
{
  "results": [
    [
      {
        "filename": "deep_learning_2023_survey.pdf",
        "score": 0.96,
        "center_page": 22,
        "combined_page": "Recent advances in neural network optimization include adaptive learning rates... [context]",
        "page_numbers": [20, 21, 22, 23, 24]
      },
      {
        "filename": "transformer_optimization_2023.pdf",
        "score": 0.91,
        "center_page": 15,
        "combined_page": "Transformer models benefit from gradient accumulation and mixed precision training... [context]",
        "page_numbers": [13, 14, 15, 16, 17]
      }
    ]
  ]
}
```

**Key Points:**
- Filters by exact year (2023)
- Filters by citation count (50, 100, or 150)
- Combines multiple value filters with AND logic
- Useful for finding highly-cited recent papers

---

#### Example 2.6: Search with Custom Context Window

**Request:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "legal_documents",
    "search_queries": ["intellectual property rights"],
    "limit": 2,
    "context_window_size": 10,
    "embedding_model": "mxbai-embed-large"
  }'
```

**Response:**
```json
{
  "results": [
    [
      {
        "filename": "patent_law_guide.pdf",
        "score": 0.94,
        "center_page": 45,
        "combined_page": "Intellectual property includes patents, trademarks, and copyrights... [full context from pages 35-55, 21 pages total]",
        "page_numbers": [35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55]
      }
    ]
  ]
}
```

**Key Points:**
- context_window_size: 10 means ±10 pages (21 total pages)
- Larger context window for comprehensive understanding
- Useful for legal/technical documents needing full context
- Trade-off: slower response but more complete information

---

#### Example 2.7: Search with Minimal Context Window (Fast Response)

**Request:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "news_articles",
    "search_queries": ["technology trends"],
    "limit": 10,
    "context_window_size": 1,
    "embedding_model": "mxbai-embed-large"
  }'
```

**Response:**
```json
{
  "results": [
    [
      {
        "filename": "tech_news_2024.md",
        "score": 0.89,
        "center_page": 3,
        "combined_page": "AI and machine learning continue to dominate technology trends... [context from pages 2-4]",
        "page_numbers": [2, 3, 4]
      },
      {
        "filename": "innovation_report.md",
        "score": 0.85,
        "center_page": 7,
        "combined_page": "Cloud computing and edge computing are reshaping infrastructure... [context from pages 6-8]",
        "page_numbers": [6, 7, 8]
      }
    ]
  ]
}
```

**Key Points:**
- context_window_size: 1 means ±1 page (3 total pages)
- Minimal context for quick responses
- Useful for real-time applications
- Faster processing and smaller response payload

---

#### Example 2.8: Complex Multi-Filter Search

**Request:**
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "product_documentation",
    "search_queries": ["API rate limiting configuration"],
    "filter": {
      "metadata.product": {
        "match_text": ["API Gateway", "REST API"]
      },
      "metadata.version": {
        "match_value": [3, 4]
      },
      "metadata.status": {
        "match_text": "published"
      }
    },
    "limit": 5,
    "context_window_size": 3,
    "embedding_model": "bge-m3"
  }'
```

**Response:**
```json
{
  "results": [
    [
      {
        "filename": "api_gateway_v4_guide.pdf",
        "score": 0.96,
        "center_page": 28,
        "combined_page": "Rate limiting configuration in API Gateway v4 supports token bucket and sliding window algorithms... [context from pages 25-31]",
        "page_numbers": [25, 26, 27, 28, 29, 30, 31]
      },
      {
        "filename": "rest_api_v3_docs.pdf",
        "score": 0.91,
        "center_page": 15,
        "combined_page": "REST API v3 implements rate limiting through headers and quota management... [context from pages 12-18]",
        "page_numbers": [12, 13, 14, 15, 16, 17, 18]
      }
    ]
  ]
}
```

**Key Points:**
- Multiple filters combined with AND logic
- Text filters with arrays (OR within filter)
- Value filters with arrays (OR within filter)
- All filters must match for document to be included
- Most powerful search capability

---

### 3. Simple Search Endpoint (Lightweight)

The `/simple-search` endpoint performs fast semantic search without context retrieval, ideal for quick lookups.

#### Example 3.1: Basic Simple Search

**Request:**
```bash
curl -X POST "http://localhost:8000/simple-search" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "knowledge_base",
    "queries": ["containerization best practices"],
    "limit": 3,
    "embedding_model": "mxbai-embed-large"
  }'
```

**Response:**
```json
{
  "status": "success",
  "queries": ["containerization best practices"],
  "total_results": 3,
  "hits": [
    {
      "id": "doc_001",
      "score": 0.94,
      "payload": {
        "pagecontent": "Always use specific version tags for container images rather than 'latest' to ensure reproducibility and prevent unexpected changes.",
        "metadata": {
          "filename": "docker_guidelines.md",
          "page_number": 15,
          "category": "devops",
          "author": "DevOps Team"
        }
      },
      "matching_query": "containerization best practices"
    },
    {
      "id": "doc_002",
      "score": 0.88,
      "payload": {
        "pagecontent": "Multi-stage Docker builds reduce image size and improve security by minimizing attack surface.",
        "metadata": {
          "filename": "container_security.md",
          "page_number": 22,
          "category": "security"
        }
      },
      "matching_query": "containerization best practices"
    },
    {
      "id": "doc_003",
      "score": 0.82,
      "payload": {
        "pagecontent": "Container orchestration platforms like Kubernetes manage deployment, scaling, and networking.",
        "metadata": {
          "filename": "kubernetes_intro.md",
          "page_number": 8,
          "category": "orchestration"
        }
      },
      "matching_query": "containerization best practices"
    }
  ]
}
```

**Key Points:**
- No context retrieval (single page only)
- Faster response than standard search
- Results sorted by relevance score
- Includes matching_query field
- Ideal for quick lookups and real-time applications

---

#### Example 3.2: Multiple Queries with Simple Search

**Request:**
```bash
curl -X POST "http://localhost:8000/simple-search" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "support_documentation",
    "queries": [
      "kubernetes troubleshooting",
      "pod networking issues",
      "persistent volume setup"
    ],
    "limit": 2,
    "embedding_model": "bge-m3"
  }'
```

**Response:**
```json
{
  "status": "success",
  "queries": [
    "kubernetes troubleshooting",
    "pod networking issues",
    "persistent volume setup"
  ],
  "total_results": 5,
  "hits": [
    {
      "id": "k8s_001",
      "score": 0.96,
      "payload": {
        "pagecontent": "Use kubectl describe pod to diagnose pod issues. Check events, resource limits, and node status.",
        "metadata": {
          "filename": "k8s_troubleshooting.md",
          "page_number": 12,
          "section": "Pod Diagnostics"
        }
      },
      "matching_query": "kubernetes troubleshooting"
    },
    {
      "id": "k8s_002",
      "score": 0.93,
      "payload": {
        "pagecontent": "Network policies control traffic between pods. Use selectors to define ingress and egress rules.",
        "metadata": {
          "filename": "k8s_networking.md",
          "page_number": 35,
          "section": "Network Policies"
        }
      },
      "matching_query": "pod networking issues"
    },
    {
      "id": "k8s_003",
      "score": 0.91,
      "payload": {
        "pagecontent": "PersistentVolumes (PV) and PersistentVolumeClaims (PVC) manage storage. PVs are cluster resources, PVCs are namespace-scoped.",
        "metadata": {
          "filename": "k8s_storage.md",
          "page_number": 18,
          "section": "Storage Management"
        }
      },
      "matching_query": "persistent volume setup"
    },
    {
      "id": "k8s_004",
      "score": 0.87,
      "payload": {
        "pagecontent": "Service mesh tools like Istio provide advanced networking capabilities including traffic management and security policies.",
        "metadata": {
          "filename": "k8s_advanced.md",
          "page_number": 42,
          "section": "Service Mesh"
        }
      },
      "matching_query": "kubernetes troubleshooting"
    },
    {
      "id": "k8s_005",
      "score": 0.84,
      "payload": {
        "pagecontent": "StatefulSets maintain persistent identity for pods, useful for databases and stateful applications with persistent storage.",
        "metadata": {
          "filename": "k8s_stateful.md",
          "page_number": 25,
          "section": "Stateful Applications"
        }
      },
      "matching_query": "persistent volume setup"
    }
  ]
}
```

**Key Points:**
- Three queries processed in one request
- Results aggregated and deduplicated
- Sorted by score across all queries
- Shows which query matched each result
- Total count includes all unique results

---

#### Example 3.3: Simple Search with Different Embedding Model

**Request:**
```bash
curl -X POST "http://localhost:8000/simple-search" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "research_papers",
    "queries": ["quantum computing applications"],
    "limit": 4,
    "embedding_model": "bge-m3"
  }'
```

**Response:**
```json
{
  "status": "success",
  "queries": ["quantum computing applications"],
  "total_results": 4,
  "hits": [
    {
      "id": "quantum_001",
      "score": 0.97,
      "payload": {
        "pagecontent": "Quantum computers excel at optimization problems, drug discovery, and cryptography. Quantum annealing solves combinatorial optimization.",
        "metadata": {
          "filename": "quantum_applications_2024.pdf",
          "page_number": 45,
          "publication_year": 2024,
          "citations": 156
        }
      },
      "matching_query": "quantum computing applications"
    },
    {
      "id": "quantum_002",
      "score": 0.94,
      "payload": {
        "pagecontent": "Quantum machine learning leverages quantum circuits for classification and regression tasks with potential speedup.",
        "metadata": {
          "filename": "qml_survey.pdf",
          "page_number": 28,
          "publication_year": 2023,
          "citations": 89
        }
      },
      "matching_query": "quantum computing applications"
    },
    {
      "id": "quantum_003",
      "score": 0.91,
      "payload": {
        "pagecontent": "Quantum simulation enables studying quantum systems that are intractable for classical computers.",
        "metadata": {
          "filename": "quantum_simulation_guide.pdf",
          "page_number": 12,
          "publication_year": 2023,
          "citations": 67
        }
      },
      "matching_query": "quantum computing applications"
    },
    {
      "id": "quantum_004",
      "score": 0.88,
      "payload": {
        "pagecontent": "Quantum error correction is crucial for practical quantum computers. Surface codes and topological codes are promising approaches.",
        "metadata": {
          "filename": "quantum_error_correction.pdf",
          "page_number": 33,
          "publication_year": 2024,
          "citations": 45
        }
      },
      "matching_query": "quantum computing applications"
    }
  ]
}
```

**Key Points:**
- Uses bge-m3 embedding model (higher quality)
- Better semantic understanding
- Slightly slower than mxbai-embed-large
- Trade-off: accuracy vs speed
- Choose model based on requirements

---

## Advanced Usage

### Filtering Guide

#### 1. Text Matching (Single Value)
```json
{
  "metadata.category": {
    "match_text": "technology"
  }
}
```

#### 2. Text Matching (Multiple Values - OR Logic)
```json
{
  "metadata.category": {
    "match_text": ["technology", "science", "research"]
  }
}
```

#### 3. Value Matching (Numeric/Boolean)
```json
{
  "metadata.year": {
    "match_value": 2023
  },
  "metadata.published": {
    "match_value": true
  }
}
```

#### 4. Value Matching (Multiple Values - OR Logic)
```json
{
  "metadata.priority": {
    "match_value": [1, 2, 3]
  }
}
```

#### 5. Range Filters (Numeric Fields)
```json
{
  "metadata.year": {
    "gte": 2020,
    "lte": 2024
  },
  "metadata.score": {
    "gte": 0.8
  }
}
```

**Range Operators:**
- `gte`: Greater than or equal to
- `lte`: Less than or equal to
- Can be used together or separately
- Works with integer and float fields

#### 6. Complex Composite Filters
```json
{
  "metadata.document_type": {
    "match_text": ["report", "whitepaper"]
  },
  "metadata.year": {
    "gte": 2022,
    "lte": 2024
  },
  "metadata.published": {
    "match_value": true
  },
  "metadata.priority": {
    "match_value": [1, 2, 3]
  }
}
```

**Filter Logic:**
- Array values within a field use OR logic (match ANY value)
- Multiple fields use AND logic (ALL conditions must match)
- Range filters can be combined with other filter types

### Context Window Configuration

#### Global Configuration (via .env)
```bash
CONTEXT_WINDOW_SIZE=5
```
This sets the default context window for all requests.

#### Per-Request Override
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "docs",
    "search_queries": ["example"],
    "context_window_size": 10
  }'
```

#### Context Window Behavior
- **Window Size**: N pages before + N pages after the matched page
- **Example**: `context_window_size: 3` retrieves pages [center-3, center-2, center-1, center, center+1, center+2, center+3]
- **Total Pages**: `(context_window_size * 2) + 1`
- **Deduplication**: Pages are deduplicated across multiple search results

### Embedding Model Selection

#### Available Models (via Ollama)
```bash
# General purpose (default)
embedding_model: "mxbai-embed-large"

# High quality multilingual
embedding_model: "bge-m3"

# Optimized for text
embedding_model: "nomic-embed-text"

# Smaller, faster
embedding_model: "all-minilm"
```

#### Model Installation
```bash
# Pull model into Ollama
ollama pull mxbai-embed-large
ollama pull bge-m3

# List available models
ollama list
```

---

## Code Architecture

### Class Hierarchy

#### SearchSystem Class
The core class managing all search operations:

```python
class SearchSystem:
    # Class-level connection pools (singleton pattern)
    _qdrant_pool: Optional[QdrantClient] = None
    _ollama_pool: Optional[ollama.Client] = None
    
    def __init__(self, collection_name: str, context_window_size: Optional[int] = None)
    
    # Connection Management
    @classmethod
    def _get_qdrant_client() -> QdrantClient
    @classmethod
    def _get_ollama_client() -> ollama.Client
    
    # Collection Management
    def _ensure_collection() -> None
    
    # Validation
    def _validate_payload(payload: Dict) -> bool
    def _validate_simple_payload(payload: Dict) -> bool
    
    # Core Operations
    def _generate_query_embedding(query: str, embedding_model: str) -> List[float]
    def _get_context_pages(filename: str, center_page_number: int) -> List[Dict]
    def batch_search(...) -> List[List[Dict]]
```

### Request Models (Pydantic)

#### SearchRequest
```python
class SearchRequest(BaseModel):
    collection_name: str  # Required
    search_queries: List[str]  # Required, min 1 item
    filter: Optional[Dict[str, Dict[str, Union[str, int, float, bool, List]]]]
    embedding_model: Optional[str] = "mxbai-embed-large"
    limit: Optional[int] = 5  # Must be >= 1
    context_window_size: Optional[int] = None
```

#### SimpleSearchRequest
```python
class SimpleSearchRequest(BaseModel):
    collection_name: str  # Required
    queries: List[str]  # Required, min 1 item
    embedding_model: Optional[str] = "mxbai-embed-large"
    limit: Optional[int] = 5  # Must be >= 1
```

### Exception Hierarchy

```python
SearchException (base)
├── EmbeddingError
└── QdrantConnectionError
```

### Middleware Components

#### Correlation ID Middleware
- Injects unique UUID for each request
- Tracks request through entire system
- Included in all log entries
- Returned in response headers as `X-Correlation-ID`

#### CORS Middleware
- Allows requests from any origin
- Supports all HTTP methods
- Allows all headers

### Logging System

#### JSON Logging Format
```json
{
  "asctime": "2024-03-20 14:35:22",
  "levelname": "INFO",
  "name": "__main__",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Search request received",
  "collection": "research_papers",
  "query_count": 2
}
```

#### Log Levels
- **DEBUG**: Detailed internal information (embedding generation, context retrieval)
- **INFO**: Request lifecycle events (request received, results generated)
- **ERROR**: Operational failures (connection errors, search failures)
- **CRITICAL**: System-level failures

---

## Performance Optimization

### 1. Connection Pooling
- Connections are reused via class-level pools
- First request initializes connections
- Subsequent requests reuse existing connections
- Reduces overhead for high-frequency requests

### 2. Context Window Tuning
```bash
# Faster responses (less context)
CONTEXT_WINDOW_SIZE=1

# Balanced (default)
CONTEXT_WINDOW_SIZE=5

# More context (slower)
CONTEXT_WINDOW_SIZE=10
```

### 3. Embedding Model Selection
```bash
# Fast but less accurate
embedding_model: "all-minilm"

# Balanced (default)
embedding_model: "mxbai-embed-large"

# Slow but most accurate
embedding_model: "bge-m3"
```

### 4. Result Limiting
```bash
# Fewer results = faster response
limit: 3

# More results = slower response
limit: 20
```

### 5. Batch Processing
```bash
# Process multiple queries in one request
# More efficient than multiple requests
POST /search
{
  "search_queries": ["query1", "query2", "query3"]
}
```

### 6. Filter Optimization
- Use specific filters to reduce search space
- Combine multiple filters for narrower results
- Reduces number of context pages to retrieve

### Benchmarks (Approximate)
- **Health Check**: <10ms
- **Simple Search (1 query)**: 100-500ms
- **Standard Search (1 query, context)**: 200-800ms
- **Batch Search (3 queries, context)**: 400-1500ms

---

## Troubleshooting

### Connection Issues

#### Qdrant Connection Failed
```
Error: Qdrant connection failed: Connection refused
```

**Solutions**:
1. Verify Qdrant is running: `telnet $QDRANT_HOST 6334`
2. Check `QDRANT_HOST` in `.env` file
3. Ensure network connectivity between services
4. Check Qdrant logs: `docker logs qdrant` (if using Docker)

#### Ollama Connection Failed
```
Error: Ollama connection failed: Connection refused
```

**Solutions**:
1. Verify Ollama is running: `curl http://$OLLAMA_HOST:11434/api/tags`
2. Check `OLLAMA_HOST` in `.env` file
3. Ensure network connectivity between services
4. Verify Ollama service is listening on correct port

### Embedding Issues

#### Embedding Model Not Found
```
Error: model not found
```

**Solutions**:
1. List available models: `ollama list`
2. Pull required model: `ollama pull mxbai-embed-large`
3. Verify model name spelling in request
4. Check Ollama logs for errors

#### Embedding Generation Timeout
```
Error: Request timeout
```

**Solutions**:
1. Increase `REQUEST_TIMEOUT` in `.env`
2. Use a smaller embedding model (all-minilm)
3. Reduce batch size (fewer queries per request)
4. Check Ollama service performance

### Search Issues

#### Empty Search Results
```
Response: "results": [[]]
```

**Solutions**:
1. Verify collection exists: `curl http://$QDRANT_HOST:6333/collections`
2. Verify collection has data: Check Qdrant dashboard
3. Try simpler search query
4. Remove or relax filters
5. Verify embedding model matches collection

#### Collection Not Found
```
Error: Collection 'my_collection' not found
```

**Solutions**:
1. Create collection in Qdrant first
2. Verify collection name spelling
3. Check Qdrant dashboard for available collections
4. Use API to list collections

### Performance Issues

#### Slow Response Times
**Causes & Solutions**:
- Large context windows → Reduce `CONTEXT_WINDOW_SIZE`
- Complex filters → Simplify or remove filters
- Large embedding models → Use smaller model
- High load → Increase timeouts, add load balancing
- Network latency → Check network connectivity

#### High Memory Usage
**Causes & Solutions**:
- Large context windows → Reduce `CONTEXT_WINDOW_SIZE`
- Large embedding models → Use smaller model
- Many concurrent requests → Add rate limiting
- Memory leaks → Restart service, check logs

### Docker Issues

#### Container Fails to Start
```bash
# Check container logs
docker-compose logs search_api
# OR
docker logs qdrant-search-api-v2

# Check container status
docker-compose ps
# OR
docker ps -a

# Verify image exists
docker images | grep qdrant

# Rebuild image
docker-compose build --no-cache
# OR
docker build -t qdrant-search-api-v2 ./app --no-cache
```

#### Container Starts But Health Check Fails
```bash
# Check if container is running
docker-compose ps

# Test container network connectivity
docker-compose exec search_api ping qdrant-host
docker-compose exec search_api ping ollama-host

# Check environment variables
docker-compose exec search_api env | grep -E "(QDRANT|OLLAMA)"

# Test external services from container
docker-compose exec search_api curl http://$QDRANT_HOST:6333/collections
docker-compose exec search_api curl http://$OLLAMA_HOST:11434/api/tags
```

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# OR
netstat -tulpn | grep 8000

# Kill process
kill -9 <PID>

# Or use different port in docker-compose.yml
ports:
  - "8001:8000"  # Host:Container
```

#### External Service Connection Issues
```bash
# Test connectivity from host
ping $QDRANT_HOST
ping $OLLAMA_HOST

# Test service endpoints
curl http://$QDRANT_HOST:6333/collections
curl http://$OLLAMA_HOST:11434/api/tags

# Check firewall rules
sudo ufw status  # Ubuntu
sudo firewall-cmd --list-all  # CentOS/RHEL

# Verify Docker network
docker network ls
docker network inspect qdrant_search_api_v2_default
```

#### Environment Variable Issues
```bash
# Check .env file exists and is readable
ls -la .env
cat .env

# Verify environment variables in container
docker-compose exec search_api env

# Test with explicit environment variables
docker run -it --rm \
  -e QDRANT_HOST=192.168.1.100 \
  -e OLLAMA_HOST=192.168.1.101 \
  -e DEBUG=true \
  qdrant-search-api-v2 python -c "import os; print(f'Qdrant: {os.getenv(\"QDRANT_HOST\")}')"
```

#### Container Resource Issues
```bash
# Check container resource usage
docker stats qdrant-search-api-v2

# Check available system resources
free -h  # Memory
df -h    # Disk space

# Increase container resources (if using Docker Desktop)
# Go to Docker Desktop > Settings > Resources
```

---

## Container Management

### Docker Compose Commands

#### Basic Operations
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View status
docker-compose ps

# View logs
docker-compose logs -f search_api

# Rebuild and restart
docker-compose up -d --build
```

#### Development Operations
```bash
# Start with live logs
docker-compose up

# Start specific service
docker-compose up search_api

# Execute commands in container
docker-compose exec search_api bash
docker-compose exec search_api python -c "import sys; print(sys.version)"

# View environment variables
docker-compose exec search_api env

# Copy files to/from container
docker-compose cp local_file.txt search_api:/app/
docker-compose cp search_api:/app/logs/app.log ./
```

#### Maintenance Operations
```bash
# Update container image
docker-compose pull
docker-compose up -d

# Clean up unused resources
docker system prune -f

# View resource usage
docker-compose exec search_api top
docker stats $(docker-compose ps -q)

# Backup container data (if any volumes)
docker-compose exec search_api tar czf /tmp/backup.tar.gz /app/data
docker-compose cp search_api:/tmp/backup.tar.gz ./backup.tar.gz
```

### Direct Docker Commands

#### Container Lifecycle
```bash
# Build image
docker build -t qdrant-search-api-v2 ./app

# Run container
docker run -d \
  --name qdrant-search-api-v2 \
  -p 8000:8000 \
  --env-file .env \
  qdrant-search-api-v2

# Stop container
docker stop qdrant-search-api-v2

# Start existing container
docker start qdrant-search-api-v2

# Remove container
docker rm qdrant-search-api-v2

# Remove image
docker rmi qdrant-search-api-v2
```

#### Container Inspection
```bash
# View container logs
docker logs qdrant-search-api-v2 -f

# Execute commands in container
docker exec -it qdrant-search-api-v2 bash
docker exec qdrant-search-api-v2 curl http://localhost:8000/health

# Inspect container configuration
docker inspect qdrant-search-api-v2

# View container resource usage
docker stats qdrant-search-api-v2
```

---

## Development

### Development with Docker (Recommended)
```bash
# 1. Start development environment
docker-compose up -d

# 2. Make code changes in ./app/

# 3. Rebuild and restart
docker-compose up -d --build

# 4. View logs
docker-compose logs -f search_api

# 5. Test changes
curl http://localhost:8000/health
```

### Local Development (Manual)
```bash
# 1. Setup environment
cd app
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
cp ../tamplate.env ../.env
# Edit .env with service IPs

# 3. Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Debugging

#### Container Debugging
```bash
# Enable debug logging in container
docker-compose exec search_api \
  python -c "import os; os.environ['DEBUG']='true'; exec(open('main.py').read())"

# View detailed logs
docker-compose logs -f search_api

# Interactive debugging
docker-compose exec search_api python -i main.py
```

#### Local Debugging
```bash
# Enable debug logging
DEBUG=true uvicorn main:app --reload

# Python debugger
python -m pdb app/main.py

# View detailed logs
tail -f logs/app.log
```

### Testing

#### Health Check Tests
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test from inside container
docker-compose exec search_api curl http://localhost:8000/health

# Test external service connectivity
docker-compose exec search_api curl http://$QDRANT_HOST:6333/collections
docker-compose exec search_api curl http://$OLLAMA_HOST:11434/api/tags
```

#### API Tests
```bash
# Simple search test
curl -X POST http://localhost:8000/simple-search \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "test_collection",
    "queries": ["test query"],
    "limit": 3
  }'

# Standard search test
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "test_collection",
    "search_queries": ["test query"],
    "limit": 3,
    "context_window_size": 2
  }'
```

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```bash
git clone https://github.com/Crypto-Gi/qdrant_search_api_v2.git
cd qdrant_search_api_v2
python -m venv venv
source venv/bin/activate
pip install -r app/requirements.txt
```

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### MIT License Summary
- ✅ Commercial use
- ✅ Modification
- ✅ Distribution
- ✅ Private use
- ❌ Liability
- ❌ Warranty

---

## Support & Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Ollama Documentation](https://github.com/ollama/ollama)

### Community
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Start discussions on GitHub Discussions
- **Email**: Contact maintainers for support

### Related Projects
- [Qdrant Vector Database](https://github.com/qdrant/qdrant)
- [Ollama](https://github.com/ollama/ollama)
- [FastAPI](https://github.com/tiangolo/fastapi)

---

## Changelog

### v2.0.0 (Current)
- ✨ Dynamic context window configuration
- ✨ Intelligent page deduplication
- ✨ Advanced array-based filtering
- ✨ Per-request configuration override
- ✨ Comprehensive documentation
- 🐛 Improved error handling
- 📈 Performance optimizations

### v1.0.0
- Initial release
- Basic semantic search
- Context retrieval
- Health check endpoint

---

**Made with ❤️ by Crypto-Gi**

*Last Updated: 2024*
