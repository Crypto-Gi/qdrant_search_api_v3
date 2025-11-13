# MCP Server IDE Setup Guide

## 🎯 Overview
This guide shows how to configure the Docsplorer MCP server in your IDE (Windsurf, Claude Desktop, etc.) with API key authentication.

## 📋 Prerequisites
- FastAPI server running with API key authentication enabled
- Generated API key (use: `openssl rand -hex 32`)
- MCP server files in your project

## 🔧 Setup Methods

### Method 1: Environment Variables in IDE Config (Recommended)

Add the API key directly to your IDE's MCP configuration file.

#### Windsurf Configuration
**File:** `~/.codeium/windsurf/mcp_config.json`

```json
{
  "mcpServers": {
    "docsplorer": {
      "command": "fastmcp",
      "args": [
        "run",
        "/home/mir/projects/qdrant-semantic-search-api/mcp-server/server.py"
      ],
      "disabled": false,
      "env": {
        "API_URL": "http://localhost:8001",
        "API_KEY": "c0649c550e8f7f1068a185bdc80c4fcb1a7884ceb3d787045cc0003a5f572eab",
        "QDRANT_COLLECTION": "content",
        "EMBEDDING_MODEL": "bge-m3",
        "USE_PRODUCTION": "true",
        "DEFAULT_CONTEXT_WINDOW": "5",
        "DEFAULT_LIMIT": "1"
      }
    }
  }
}
```

#### Claude Desktop Configuration
**File:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
**File:** `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

```json
{
  "mcpServers": {
    "docsplorer": {
      "command": "fastmcp",
      "args": ["run", "/path/to/server.py"],
      "env": {
        "API_URL": "http://localhost:8001",
        "API_KEY": "your-api-key-here",
        "QDRANT_COLLECTION": "content",
        "USE_PRODUCTION": "true"
      }
    }
  }
}
```

### Method 2: .env File (Local Development)

Create a `.env` file in the `mcp-server/` directory:

```env
# mcp-server/.env
API_URL=http://localhost:8001
API_KEY=c0649c550e8f7f1068a185bdc80c4fcb1a7884ceb3d787045cc0003a5f572eab
QDRANT_COLLECTION=content
EMBEDDING_MODEL=bge-m3
USE_PRODUCTION=true
DEFAULT_CONTEXT_WINDOW=5
DEFAULT_LIMIT=2
```

**IDE Config (minimal):**
```json
{
  "mcpServers": {
    "docsplorer": {
      "command": "fastmcp",
      "args": ["run", "/path/to/server.py"],
      "disabled": false
    }
  }
}
```

**Note:** The `.env` file is automatically loaded by `config.py` using `python-dotenv`.

### Method 3: System Environment Variables

Set environment variables at the system level:

```bash
# Linux/macOS
export API_URL="http://localhost:8001"
export API_KEY="your-api-key-here"
export QDRANT_COLLECTION="content"
export USE_PRODUCTION="true"

# Windows (PowerShell)
$env:API_URL="http://localhost:8001"
$env:API_KEY="your-api-key-here"
$env:QDRANT_COLLECTION="content"
$env:USE_PRODUCTION="true"
```

**IDE Config (minimal):**
```json
{
  "mcpServers": {
    "docsplorer": {
      "command": "fastmcp",
      "args": ["run", "/path/to/server.py"],
      "disabled": false
    }
  }
}
```

## 🌐 Remote Host Setup

### Scenario: API Server on Remote Host

If your FastAPI server is running on a remote host (e.g., `https://api.example.com`):

#### Option 1: Direct Connection
```json
{
  "mcpServers": {
    "docsplorer": {
      "command": "fastmcp",
      "args": ["run", "/path/to/server.py"],
      "env": {
        "API_URL": "https://api.example.com:8001",
        "API_KEY": "your-api-key-here",
        "QDRANT_COLLECTION": "content",
        "USE_PRODUCTION": "true"
      }
    }
  }
}
```

#### Option 2: SSH Tunnel
```bash
# Create SSH tunnel to remote host
ssh -L 8001:localhost:8001 user@remote-host

# Use localhost in config
"API_URL": "http://localhost:8001"
```

#### Option 3: HTTPS Proxy (Recommended for Production)
```bash
# Remote host with HTTPS proxy (nginx, caddy, etc.)
"API_URL": "https://api.example.com"
```

**Benefits:**
- ✅ API key encrypted in transit
- ✅ SSL/TLS termination
- ✅ Load balancing
- ✅ Rate limiting

## 🔒 Security Best Practices

### 1. Never Commit API Keys
```bash
# Add to .gitignore
echo "mcp-server/.env" >> .gitignore
echo "*.env" >> .gitignore
```

### 2. Use Different Keys for Different Environments
```env
# Development
API_KEY=dev-key-12345...

# Production
API_KEY=prod-key-67890...
```

### 3. Rotate Keys Regularly
```bash
# Generate new key
openssl rand -hex 32

# Update in:
# 1. FastAPI server .env
# 2. MCP server .env or IDE config
# 3. Restart both services
```

### 4. Use HTTPS for Remote Connections
```json
{
  "env": {
    "API_URL": "https://api.example.com",  // ✅ HTTPS
    "API_KEY": "your-key"  // Encrypted in transit
  }
}
```

## ✅ Verification

### Test MCP Server Connection
```bash
cd mcp-server
python test_mcp_tools.py
```

**Expected Output:**
```
🎉 All tests passed! MCP server API key authentication works!
```

### Test in IDE
1. Open your IDE (Windsurf/Claude Desktop)
2. Reload MCP servers
3. Try using a tool: `@docsplorer search_filenames_fuzzy("ecos", limit=5)`
4. Should return results without errors

## 🐛 Troubleshooting

### Issue: "Missing authentication credentials"
**Solution:** API key not configured
```bash
# Check if API_KEY is set
cd mcp-server
python -c "from config import MCPConfig; c = MCPConfig(); print(f'API Key: {\"✅\" if c.api_key else \"❌\"}')"
```

### Issue: "Invalid API key"
**Solution:** API key mismatch between FastAPI and MCP server
```bash
# Verify keys match
# FastAPI: cat ../.env | grep API_KEY
# MCP: cat .env | grep API_KEY
```

### Issue: Connection refused
**Solution:** FastAPI server not running
```bash
# Start FastAPI server
cd ..
docker compose up -d
# or
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Issue: Tools not working in IDE
**Solution:** Reload MCP servers
- **Windsurf:** Restart IDE or reload MCP servers
- **Claude Desktop:** Restart application

## 📚 Configuration Reference

### All Available Environment Variables

```env
# API Configuration
API_URL=http://localhost:8001              # FastAPI server URL
API_KEY=your-api-key-here                  # API authentication key

# Qdrant Configuration (Optional Overrides)
QDRANT_HOST=https://qdrant.example.com     # Override Qdrant host
QDRANT_API_KEY=qdrant-key                  # Override Qdrant API key
QDRANT_COLLECTION=content                  # Collection name

# Ollama Configuration (Optional Overrides)
OLLAMA_URL=http://localhost:11434          # Override Ollama URL
OLLAMA_API_KEY=ollama-key                  # Ollama Cloud API key

# Embedding Configuration
EMBEDDING_MODEL=bge-m3                     # Embedding model name
EMBEDDING_DIMENSIONS=1024                  # Vector dimensions

# Default Settings
USE_PRODUCTION=true                        # Use production Qdrant
DEFAULT_CONTEXT_WINDOW=5                   # Pages before/after match
DEFAULT_LIMIT=2                            # Max results per query
```

### Priority Order
1. **IDE env variables** (highest priority)
2. **`.env` file** in mcp-server directory
3. **System environment variables**
4. **Hardcoded defaults** (lowest priority)

## 🚀 Quick Start

### 1. Generate API Key
```bash
openssl rand -hex 32
```

### 2. Configure FastAPI Server
```bash
# Edit .env
API_KEY_ENABLED=true
API_KEY=your-generated-key

# Restart
docker compose restart
```

### 3. Configure MCP Server
**Option A: IDE Config**
```json
{
  "env": {
    "API_KEY": "your-generated-key"
  }
}
```

**Option B: .env File**
```bash
echo "API_KEY=your-generated-key" >> mcp-server/.env
```

### 4. Test
```bash
cd mcp-server
python test_mcp_tools.py
```

### 5. Use in IDE
```
@docsplorer search_filenames_fuzzy("ecos", limit=5)
```

---

## 🎉 You're Ready!

Your MCP server is now configured with secure API key authentication and ready to use in your IDE!

For more information, see:
- [INSTALL.md](INSTALL.md) - Installation guide
- [TOOL_USAGE.md](TOOL_USAGE.md) - Tool usage examples
- [PHASE2_COMPLETION.md](../PHASE2_COMPLETION.md) - API key implementation details
