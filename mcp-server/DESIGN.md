# MCP Server for Docsplorer Application - Design Document

**Version:** 1.0  
**Date:** November 12, 2025  
**Status:** Design Phase

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Objectives](#objectives)
3. [Architecture](#architecture)
4. [Tool Specifications](#tool-specifications)
5. [Implementation Plan](#implementation-plan)
6. [Testing Strategy](#testing-strategy)
7. [Future Enhancements](#future-enhancements)

---

## 🎯 Project Overview

### What We're Building

An MCP (Model Context Protocol) server that enables Large Language Models (LLMs) to interact with our Qdrant-based RAG (Retrieval-Augmented Generation) system for searching and analyzing release note documentation.

### The Problem

Users need to query release notes across multiple versions and products efficiently. Manual searching is time-consuming and error-prone. LLMs can help, but they need structured access to our document database.

### The Solution

Create an MCP server that exposes specialized tools for:
1. **Discovery**: Find relevant release note files
2. **Retrieval**: Get specific content from documents with context
3. **Analysis**: Compare information across versions
4. **Efficiency**: Batch multiple queries to reduce API calls

---

## 🎯 Objectives

### Primary Goals

1. **Enable LLM-Driven RAG Workflow**
   - LLM can discover available documents
   - LLM can search within specific documents
   - LLM can compare information across versions

2. **Optimize for Production Use**
   - Minimize token usage in responses
   - Reduce API call overhead
   - Provide clean, structured outputs

3. **Maintain Flexibility**
   - Support both local (stdio) and remote (SSE) access
   - Allow configuration of Qdrant collections
   - Enable context window customization

### Success Criteria

- ✅ LLM can successfully complete 2-step RAG workflow (discover → retrieve)
- ✅ All tools work with existing FastAPI endpoints (no new endpoints required)
- ✅ Response format is optimized for LLM consumption (sanitized JSON)
- ✅ Tools are tested with real curl commands before implementation
- ✅ Documentation is clear and comprehensive

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         LLM Client                          │
│                    (Claude, GPT, Gemini)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ MCP Protocol (stdio/SSE)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                      MCP Server                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Tool 1: search_filenames_fuzzy                      │  │
│  │  Tool 2: search_with_filename_filter                 │  │
│  │  Tool 3: search_multi_query_with_filter              │  │
│  │  Tool 4: search_across_multiple_files                │  │
│  │  Tool 5: compare_versions                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
│                         │ HTTP/JSON                         │
│                         │                                   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   FastAPI Server                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  POST /search                                        │  │
│  │  POST /search/filenames                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Qdrant Vector DB                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Collection: content (1024d, bge-m3)                 │  │
│  │  Collection: filenames (384d, granite-embedding)     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **MCP Framework**: FastMCP (Python)
- **Transport**: stdio (Phase 1), SSE (Phase 2)
- **HTTP Client**: httpx
- **Output Format**: Sanitized JSON (Phase 1), TOON (Phase 2)
- **Deployment**: Docker container

### Data Flow

1. **LLM → MCP Server**: Tool call with parameters
2. **MCP Server → FastAPI**: HTTP POST with JSON payload
3. **FastAPI → Qdrant**: Vector search with filters
4. **Qdrant → FastAPI**: Search results with metadata
5. **FastAPI → MCP Server**: JSON response
6. **MCP Server → LLM**: Sanitized, optimized JSON

---

## 🛠️ Tool Specifications

### Design Principles

1. **Test-Driven Design**: Test API endpoints with curl before implementing tools
2. **Observe Reality**: Base tool schemas on actual API responses, not assumptions
3. **No Guesswork**: Verify every field, data type, and structure
4. **Sanitize Outputs**: Remove redundant data, flatten structures where possible
5. **LLM-Friendly**: Optimize for token efficiency and parsing ease

### Tool 1: `search_filenames_fuzzy`

**Purpose**: Find release note files using fuzzy text matching

**API Endpoint**: `POST /search/filenames`

**Input Parameters**:
```json
{
  "query": "string (required) - Search term",
  "collection_name": "string (optional, default: 'content')",
  "limit": "integer (optional, default: 10, range: 1-100)"
}
```

**Output Format** (to be determined after curl testing):
```json
{
  "query": "ecos 9.3",
  "total": 5,
  "files": [
    "ECOS_9.3.7.0_Release_Notes_RevB",
    "ECOS_9.3.6.0_Release_Notes_RevB"
  ]
}
```

**Use Case**: "Find all ECOS 9.3 release notes"

---

### Tool 2: `search_with_filename_filter`

**Purpose**: Search within a specific release note file with context

**API Endpoint**: `POST /search`

**Input Parameters**:
```json
{
  "query": "string (required) - What to search for",
  "filename": "string (required) - Exact filename from Tool 1",
  "collection_name": "string (optional, default: 'content')",
  "limit": "integer (optional, default: 3, range: 1-10)",
  "context_window_size": "integer (optional, default: 5, range: 0-10)"
}
```

**Output Format** (to be determined after curl testing):
```json
{
  "query": "security fixes",
  "filename": "ECOS_9.3.7.0_Release_Notes_RevB",
  "results": [
    {
      "score": 0.89,
      "page": 15,
      "page_range": "13-17",
      "content": "Security fixes include CVE-2024-1234..."
    }
  ]
}
```

**Use Case**: "What security fixes are in ECOS 9.3.7?"

---

### Tool 3: `search_multi_query_with_filter`

**Purpose**: Run multiple queries on the same file efficiently

**API Endpoint**: `POST /search` (with array of queries)

**Input Parameters**:
```json
{
  "queries": "array[string] (required) - Multiple search queries",
  "filename": "string (required) - Target file",
  "collection_name": "string (optional, default: 'content')",
  "limit": "integer (optional, default: 3)",
  "context_window_size": "integer (optional, default: 5)"
}
```

**Output Format** (to be determined after curl testing):
```json
{
  "filename": "ECOS_9.3.7.0_Release_Notes_RevB",
  "results": [
    {
      "query": "security fixes",
      "score": 0.89,
      "page": 15,
      "content": "..."
    },
    {
      "query": "performance improvements",
      "score": 0.85,
      "page": 22,
      "content": "..."
    }
  ]
}
```

**Use Case**: "Analyze ECOS 9.3.7 for security, performance, and bugs"

---

### Tool 4: `search_across_multiple_files`

**Purpose**: Search same query across multiple versions

**API Endpoint**: Multiple calls to `POST /search`

**Input Parameters**:
```json
{
  "query": "string (required) - Single search query",
  "filenames": "array[string] (required) - List of files to search",
  "collection_name": "string (optional, default: 'content')",
  "limit": "integer (optional, default: 3)",
  "context_window_size": "integer (optional, default: 5)"
}
```

**Output Format** (to be determined after curl testing):
```json
{
  "query": "DHCP security",
  "results": [
    {
      "filename": "ECOS_9.3.7.0_Release_Notes_RevB",
      "score": 0.91,
      "page": 15,
      "content": "..."
    },
    {
      "filename": "ECOS_9.3.6.0_Release_Notes_RevB",
      "score": 0.87,
      "page": 12,
      "content": "..."
    }
  ]
}
```

**Use Case**: "How has DHCP security evolved across versions?"

---

### Tool 5: `compare_versions`

**Purpose**: Side-by-side comparison of topic across two versions

**API Endpoint**: Two calls to `POST /search`

**Input Parameters**:
```json
{
  "query": "string (required) - Topic to compare",
  "version1_filename": "string (required) - First version",
  "version2_filename": "string (required) - Second version",
  "collection_name": "string (optional, default: 'content')",
  "limit": "integer (optional, default: 3)"
}
```

**Output Format** (to be determined after curl testing):
```json
{
  "query": "DHCP security",
  "comparison": [
    {
      "version": "9.3.6.0",
      "filename": "ECOS_9.3.6.0_Release_Notes_RevB",
      "score": 0.87,
      "content": "..."
    },
    {
      "version": "9.3.7.0",
      "filename": "ECOS_9.3.7.0_Release_Notes_RevB",
      "score": 0.91,
      "content": "..."
    }
  ]
}
```

**Use Case**: "What changed in DHCP security between 9.3.6 and 9.3.7?"

---

### Tool 6: `get_available_versions` (Phase 2)

**Purpose**: Discover all available release note versions in the system

**API Endpoint**: `POST /search/filenames` (with wildcard or broad query)

**Input Parameters**:
```json
{
  "product": "string (optional) - Filter by product name (e.g., 'ECOS', 'Orchestrator')",
  "collection_name": "string (optional, default: 'content')",
  "limit": "integer (optional, default: 100, range: 1-1000)"
}
```

**Output Format** (to be determined after curl testing):
```json
{
  "products": ["ECOS", "Orchestrator", "Controller"],
  "versions": {
    "ECOS": [
      {"version": "9.3.7.0", "filename": "ECOS_9.3.7.0_Release_Notes_RevB"},
      {"version": "9.3.6.0", "filename": "ECOS_9.3.6.0_Release_Notes_RevB"},
      {"version": "9.3.5.0", "filename": "ECOS_9.3.5.0_Release_Notes_RevA"}
    ],
    "Orchestrator": [
      {"version": "2.1.0", "filename": "Orchestrator_2.1.0_Release_Notes"}
    ]
  },
  "total_count": 25
}
```

**Implementation Notes**:
- Uses existing `/search/filenames` endpoint with broad query (e.g., "release notes" or "*")
- Parses `metadata.filename` field from responses
- Extracts product name and version from filename patterns
- Groups and organizes by product
- No new API endpoint required

**Use Case**: "What ECOS versions are available?" or "Show me all Orchestrator releases"

---

## 📅 Implementation Plan

### Phase 1: Foundation & Testing (Current Phase)

**Goal**: Establish solid foundation with test-driven design

**Tasks**:

1. **API Testing & Documentation** (Week 1)
   - [ ] Test `POST /search/filenames` with various queries
   - [ ] Test `POST /search` with single query + filter
   - [ ] Test `POST /search` with multiple queries + filter
   - [ ] Test `POST /search` with different context_window_size values
   - [ ] Document actual API response structures
   - [ ] Create curl command reference

2. **MCP Server Setup** (Week 1)
   - [ ] Create `mcp-server/` directory structure
   - [ ] Set up FastMCP framework
   - [ ] Configure stdio transport
   - [ ] Create configuration management
   - [ ] Set up logging

3. **Tool Implementation** (Week 2)
   - [ ] Implement Tool 1: `search_filenames_fuzzy`
   - [ ] Test Tool 1 with Claude Desktop
   - [ ] Implement Tool 2: `search_with_filename_filter`
   - [ ] Test Tool 2 with Claude Desktop
   - [ ] Implement Tool 3: `search_multi_query_with_filter`
   - [ ] Test Tool 3 with Claude Desktop
   - [ ] Implement Tool 4: `search_across_multiple_files`
   - [ ] Test Tool 4 with Claude Desktop
   - [ ] Implement Tool 5: `compare_versions`
   - [ ] Test Tool 5 with Claude Desktop

4. **Docker Integration** (Week 2)
   - [ ] Create Dockerfile for MCP server
   - [ ] Update docker-compose.yml
   - [ ] Test Docker deployment
   - [ ] Create setup documentation

5. **Documentation & Polish** (Week 3)
   - [ ] Write user guide
   - [ ] Create example LLM prompts
   - [ ] Add troubleshooting guide
   - [ ] Record demo video

**Deliverables**:
- ✅ Working MCP server with 5 tools
- ✅ Docker deployment
- ✅ Comprehensive documentation
- ✅ Test results and examples

---

### Phase 2: Standalone Deployment & Security (Current)

**Goal**: Make MCP server standalone and production-ready with authentication

**Tasks**:

1. **Separate GitHub Repository**
   - [ ] Create new repo: `docsplorer-mcp-server`
   - [ ] Move MCP server code to standalone repo
   - [ ] Add comprehensive README with setup instructions
   - [ ] Include Docker deployment options
   - [ ] Document API endpoint configuration

2. **API Key Authentication**
   - [ ] Add API key auth to `/search` endpoint
   - [ ] Add API key auth to `/search/filenames` endpoint
   - [ ] Add API key auth to `/health` endpoint
   - [ ] Implement Bearer token validation
   - [ ] Add API key generation script

3. **MCP Server API Key Support**
   - [ ] Add `API_KEY` environment variable support
   - [ ] Update config.py to handle API keys
   - [ ] Add API key to HTTP headers in all requests
   - [ ] Support IDE config environment variables
   - [ ] Document API key setup in INSTALL.md

4. **Version Discovery via Fuzzy Search**
   - [x] Use `search_filenames_fuzzy` with limit=1000
   - [x] No additional tool needed
   - [ ] Document discovery patterns in TOOL_USAGE.md

**Deliverables**:
- ✅ Standalone GitHub repository
- ✅ API key authentication on all endpoints
- ✅ Configurable API endpoint URL
- ✅ Downloadable and usable from anywhere
- ✅ Production-ready security

**Notes**:
- Version Discovery tool NOT needed - use `search_filenames_fuzzy("", limit=1000)` to get all files
- TOON Format, SSE Transport, Performance Optimization moved to Phase 3

---

### Phase 3: Advanced Optimization (Future)

**Goal**: Optimize for production scale and add advanced capabilities

**Tasks**:

1. **TOON Format Integration** (moved from Phase 2)
   - [ ] Implement TOON encoder
   - [ ] Convert tool outputs to TOON format
   - [ ] Benchmark token savings (target: 50%)
   - [ ] A/B test with LLMs

2. **SSE Transport** (moved from Phase 2)
   - [ ] Add SSE transport support
   - [ ] Implement authentication
   - [ ] Set up HTTPS/SSL
   - [ ] Test remote access

3. **Performance Optimization** (moved from Phase 2)
   - [ ] Add response caching
   - [ ] Implement request batching
   - [ ] Optimize HTTP connection pooling
   - [ ] Add rate limiting

4. **Monitoring & Analytics** (moved from Phase 2)
   - [ ] Add usage metrics
   - [ ] Track token consumption
   - [ ] Monitor API latency
   - [ ] Create dashboards

5. **Additional Tools**
   - [ ] `quick_check_exists` - Fast keyword validation
   - [ ] `get_document_structure` - Document metadata
   - [ ] `extract_table_of_contents` - Parse document structure

6. **Enhanced Search**
   - [ ] Semantic clustering of results
   - [ ] Automatic query expansion
   - [ ] Relevance feedback
   - [ ] Cross-reference detection

7. **Multi-Collection Support**
   - [ ] Support custom collections
   - [ ] Cross-collection search
   - [ ] Collection management tools
   - [ ] Dynamic collection discovery

**Deliverables**:
- ✅ 50% token reduction with TOON
- ✅ Remote access via HTTPS
- ✅ Production monitoring
- ✅ Advanced search features
- ✅ Multi-collection support

---

## 🧪 Testing Strategy

### Test-Driven Tool Design Process

**For Each Tool:**

1. **API Testing**
   ```bash
   # Test the underlying API endpoint
   curl -X POST "http://localhost:8001/search/filenames" \
     -H "Content-Type: application/json" \
     -d '{"query": "ecos 9.3", "limit": 5, "use_production": true}' \
     | jq '.'
   ```

2. **Response Analysis**
   - Document actual response structure
   - Note field names, types, nesting
   - Identify redundant or unnecessary data
   - Plan sanitization strategy

3. **Tool Implementation**
   - Create tool based on observed behavior
   - Implement response sanitization
   - Add error handling

4. **LLM Testing**
   - Test with Claude Desktop
   - Observe LLM interaction
   - Refine based on usage patterns

5. **Documentation**
   - Document tool behavior
   - Add example prompts
   - Note any limitations

### Test Cases

**Tool 1: search_filenames_fuzzy**
- [ ] Search for "ecos 9.3" returns relevant files
- [ ] Search for "orchestrator" returns orchestrator files
- [ ] Limit parameter works correctly
- [ ] Empty results handled gracefully
- [ ] Invalid collection name returns error

**Tool 2: search_with_filename_filter**
- [ ] Single query with exact filename works
- [ ] Context window includes correct pages
- [ ] Score threshold filtering works
- [ ] Invalid filename returns error
- [ ] Empty query returns error

**Tool 3: search_multi_query_with_filter**
- [ ] Multiple queries return separate results
- [ ] Results maintain query order
- [ ] Empty query array returns error
- [ ] Partial failures handled gracefully

**Tool 4: search_across_multiple_files**
- [ ] Same query across multiple files works
- [ ] Results grouped by filename
- [ ] Invalid filenames skipped gracefully
- [ ] Empty filename array returns error

**Tool 5: compare_versions**
- [ ] Two-version comparison works
- [ ] Results clearly labeled by version
- [ ] Identical filenames rejected
- [ ] Missing files handled gracefully

---

## 🔮 Future Enhancements

### Short-term (3-6 months)

1. **Streaming Responses**
   - Stream large results incrementally
   - Reduce perceived latency
   - Better UX for long queries

2. **Query History**
   - Track previous queries
   - Enable query refinement
   - Suggest related queries

3. **Result Caching**
   - Cache frequent queries
   - Reduce API load
   - Faster response times

### Long-term (6-12 months)

1. **Multi-Language Support**
   - Support non-English queries
   - Translate results
   - Cross-language search

2. **Advanced Analytics**
   - Query pattern analysis
   - Usage statistics
   - Cost optimization recommendations

3. **Custom Embeddings**
   - Fine-tune embeddings for domain
   - Improve search relevance
   - Reduce false positives

---

## 📚 References

### Internal Documentation
- FastAPI Server: `/app/main.py`
- API Endpoints: `/docs` (Swagger UI)
- Environment Config: `.env`

### External Resources
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [TOON Format Specification](https://github.com/toon-format/toon)
- [Qdrant Documentation](https://qdrant.tech/documentation/)

---

## 📝 Notes

### Key Decisions

1. **JSON First, TOON Later**: Start with sanitized JSON for simplicity, migrate to TOON in Phase 2
2. **No New Endpoints**: Use existing FastAPI endpoints to minimize changes
3. **Test-Driven Design**: Always test API with curl before implementing tools
4. **Stdio First**: Start with local stdio transport, add SSE in Phase 2

### Open Questions

- [ ] Should we add authentication for SSE transport?
- [ ] What's the optimal context_window_size default?
- [ ] Should we cache API responses in MCP server?
- [ ] How to handle API rate limiting?

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| API response structure changes | High | Version API responses, add schema validation |
| Token costs too high | Medium | Implement TOON format, add caching |
| LLM misuses tools | Medium | Add usage examples, improve descriptions |
| Docker networking issues | Low | Test thoroughly, document troubleshooting |

---

**Document Status**: ✅ Ready for Phase 1 Implementation

**Next Steps**: Begin API testing with curl commands
