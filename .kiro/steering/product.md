---
inclusion: always
---

# Product Overview

Qdrant Search API v2 is a production-ready semantic search engine that provides REST API access to vector-based document search with intelligent context retrieval.

## Core Functionality

- **Semantic Search**: Vector-based matching using embeddings to find semantically similar content beyond keyword matching
- **Context-Aware Retrieval**: Dynamically retrieves surrounding pages (configurable ±1 to ±N pages) around matched content
- **Intelligent Deduplication**: Prevents duplicate pages from appearing across multiple search results
- **Advanced Filtering**: Supports text and value matching with array-based OR conditions and composite AND logic

## Key Features

- Dual search endpoints: context-aware (`/search`) and lightweight (`/simple-search`)
- Per-request configuration overrides for context window size and embedding models
- Batch query processing for efficiency
- Production-grade logging with correlation IDs for distributed tracing
- Connection pooling for Qdrant and Ollama services

## Architecture

The API acts as a microservice bridge between:
- **Qdrant Vector Database**: Stores and searches vector embeddings
- **Ollama Embedding Service**: Generates vector embeddings from text queries
- **Client Applications**: Consume the REST API for semantic search capabilities

## Use Cases

- Document search across large collections
- Knowledge base retrieval with context
- Research paper discovery
- Technical documentation search
- Support ticket analysis
