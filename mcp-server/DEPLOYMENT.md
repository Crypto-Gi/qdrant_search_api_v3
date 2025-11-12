# MCP Server Deployment Guide

Three deployment options for the Qdrant RAG MCP Server. Choose what works best for you!

---

## 📦 Option 1: uvx (Recommended - Like npx for Python)

**Best for**: Quick setup, auto-managed dependencies

### Prerequisites
```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup

1. **Clone the repository**:
```bash
git clone https://github.com/Crypto-Gi/qdrant-semantic-search-api.git
cd qdrant-semantic-search-api/mcp-server
```

2. **Copy environment template**:
```bash
cp .env.example .env
```

3. **Edit `.env`** with your settings:
```bash
API_URL=http://localhost:8001
QDRANT_COLLECTION=content
EMBEDDING_MODEL=bge-m3
```

### Windsurf/Claude Desktop Config

Add to `mcp_config.json` (replace `/path/to/` with your actual clone location):

```json
{
  "mcpServers": {
    "qdrant-rag": {
      "command": "uvx",
      "args": [
        "--from",
        "fastmcp",
        "fastmcp",
        "run",
        "/path/to/qdrant-semantic-search-api/mcp-server/server.py"
      ],
      "disabled": false,
      "env": {
        "API_URL": "http://localhost:8001",
        "QDRANT_COLLECTION": "content",
        "EMBEDDING_MODEL": "bge-m3",
        "USE_PRODUCTION": "true"
      }
    }
  }
}
```

**Example for common locations**:
- Linux/Mac: `/home/username/qdrant-semantic-search-api/mcp-server/server.py`
- Windows: `C:\Users\username\qdrant-semantic-search-api\mcp-server\server.py`
```

### Pros & Cons

✅ **Pros**:
- No manual dependency installation
- Auto-updates FastMCP
- Similar to `npx` pattern
- Clean, isolated environment

❌ **Cons**:
- Requires `uv` installation
- Slightly slower first run (downloads deps)

---

## 🐍 Option 2: FastMCP CLI

**Best for**: Direct Python execution, easy debugging

### Prerequisites
```bash
pip install fastmcp httpx python-dotenv
```

### Setup

1. **Clone the repository**:
```bash
git clone https://github.com/Crypto-Gi/qdrant-semantic-search-api.git
cd qdrant-semantic-search-api/mcp-server
```

2. **Copy environment template**:
```bash
cp .env.example .env
```

3. **Edit `.env`** with your settings

### Windsurf/Claude Desktop Config

Add to `mcp_config.json` (replace `/path/to/` with your actual clone location):

```json
{
  "mcpServers": {
    "qdrant-rag": {
      "command": "fastmcp",
      "args": [
        "run",
        "/path/to/qdrant-semantic-search-api/mcp-server/server.py"
      ],
      "disabled": false,
      "env": {
        "API_URL": "http://localhost:8001",
        "QDRANT_COLLECTION": "content",
        "EMBEDDING_MODEL": "bge-m3"
      }
    }
  }
}
```

### Pros & Cons

✅ **Pros**:
- Simple and direct
- Easy to debug
- Fast startup
- No extra tools needed

❌ **Cons**:
- Manual dependency management
- Uses global Python environment

---

## 🐳 Option 3: Docker

**Best for**: Isolated environment, production deployments

### Prerequisites
```bash
# Docker must be installed
docker --version
```

### Setup

1. **Clone the repository**:
```bash
git clone https://github.com/Crypto-Gi/qdrant-semantic-search-api.git
cd qdrant-semantic-search-api/mcp-server
```

2. **Copy environment template**:
```bash
cp .env.example .env
```

3. **Edit `.env`** with your settings

4. **Build Docker image**:
```bash
docker build -t qdrant-mcp-server .
```

### Windsurf/Claude Desktop Config

Add to `mcp_config.json` (replace `/path/to/` with your actual clone location):

```json
{
  "mcpServers": {
    "qdrant-rag": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--network",
        "host",
        "--env-file",
        "/path/to/qdrant-semantic-search-api/mcp-server/.env",
        "qdrant-mcp-server"
      ],
      "disabled": false
    }
  }
}
```

### Alternative: docker-compose

```bash
# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Pros & Cons

✅ **Pros**:
- Complete isolation
- Reproducible environment
- Production-ready
- No Python version conflicts

❌ **Cons**:
- Requires Docker
- Larger resource footprint
- Slower startup

---

## 🔧 Configuration Reference

### Required Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_URL` | Your Qdrant Search API URL | `http://localhost:8001` | ✅ |
| `QDRANT_COLLECTION` | Collection name | `content` | ✅ |
| `EMBEDDING_MODEL` | Embedding model name | `bge-m3` | ✅ |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | API authentication key | None |
| `QDRANT_HOST` | Override Qdrant host | None (uses API default) |
| `QDRANT_API_KEY` | Override Qdrant API key | None (uses API default) |
| `OLLAMA_URL` | Override Ollama URL | None (uses API default) |
| `OLLAMA_API_KEY` | Ollama Cloud API key | None (for local Ollama) |
| `EMBEDDING_DIMENSIONS` | Embedding vector size | `1024` |
| `USE_PRODUCTION` | Use production Qdrant | `true` |
| `DEFAULT_CONTEXT_WINDOW` | Default pages before/after | `5` |
| `DEFAULT_LIMIT` | Default results per query | `2` |

---

## 🧪 Testing Your Installation

### 1. Check Server Status

After adding to Windsurf/Claude Desktop, restart the application.

### 2. Test with a Query

Ask your AI assistant:
```
Search for "security vulnerabilities" in ECOS 9.3.6.0 release notes
```

### 3. Verify Tools are Available

The assistant should have access to 5 tools:
- `search_filenames_fuzzy`
- `search_with_filename_filter`
- `search_multi_query_with_filter`
- `search_across_multiple_files`
- `compare_versions`

---

## 🔍 Troubleshooting

### Server Won't Start

**Check logs**:
```bash
# Option 1 (uvx): Check Windsurf logs
# Option 2 (fastmcp): Check Windsurf logs
# Option 3 (docker): 
docker logs qdrant-mcp-server
```

**Common issues**:
1. ❌ API not running → Start your Qdrant Search API first
2. ❌ Wrong API_URL → Check `.env` or config
3. ❌ Missing dependencies → Reinstall requirements

### Tools Not Appearing

1. Restart Windsurf/Claude Desktop
2. Check `mcp_config.json` syntax
3. Verify `disabled: false`
4. Check server logs for errors

### Connection Errors

**"Connection refused"**:
- ✅ Ensure API is running: `curl http://localhost:8001/health`
- ✅ Check firewall settings
- ✅ Verify `API_URL` in config

**"Unauthorized"**:
- ✅ Check `API_KEY` if authentication is enabled
- ✅ Verify API key format

---

## 🚀 Quick Start (Recommended Path)

### For First-Time Users:

1. **Clone repository**:
```bash
git clone https://github.com/Crypto-Gi/qdrant-semantic-search-api.git
cd qdrant-semantic-search-api/mcp-server
```

2. **Install uv**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **Configure**:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Add to Windsurf** (Option 1 config above, update path to your clone location)

5. **Restart Windsurf**

6. **Test**: Ask "What files are available about ECOS 9.3?"

---

## 📝 Summary

| Option | Setup Time | Maintenance | Best For |
|--------|------------|-------------|----------|
| **1. uvx** | 5 min | Low | Most users |
| **2. FastMCP CLI** | 2 min | Medium | Developers |
| **3. Docker** | 10 min | Low | Production |

**Recommendation**: Start with **Option 1 (uvx)** - it's the easiest and most reliable!

---

## 🆘 Need Help?

- Check API is running: `curl http://localhost:8001/health`
- View server logs in Windsurf console
- Verify `.env` configuration
- Test API directly with curl (see `test_results/CURL_COMMANDS.md`)

---

**Last Updated**: November 12, 2025  
**MCP Server Version**: 1.0.0  
**FastMCP Version**: >=0.5.0
