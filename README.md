# Qdrant Search API v3 - Enhanced Semantic Search Engine

> Production-ready FastAPI semantic search with **array filters**, **range queries**, **dual environment support**, and **100% backward compatibility** with v2.

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Tests](https://img.shields.io/badge/Tests-34%2F35%20Passed-success)

---

## 🚀 What's New in v3

### Major Enhancements Over v2

| Feature | v2 | v3 | Benefit |
|---------|----|----|---------|
| **Array Filters** | ❌ Single value | ✅ Multiple values (OR) | Search multiple files/pages at once |
| **Range Filters** | ❌ Not supported | ✅ gte/lte support | Filter by page ranges |
| **Complex Filtering** | ⚠️ Basic AND | ✅ Advanced AND + OR | Flexible condition combinations |
| **Environment Support** | ❌ Single config | ✅ DEV/PROD dual | Separate dev and prod settings |
| **HTTPS/SSL** | ❌ HTTP only | ✅ Full HTTPS | Secure production deployments |
| **API Authentication** | ❌ No auth | ✅ API key support | Secure endpoints |
| **Context Window** | ⚠️ Hardcoded (5) | ✅ Configurable | Flexible context retrieval |

---

## ⚡ Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/Crypto-Gi/qdrant_search_api_v3.git
cd qdrant_search_api_v3
cp tamplate.env .env

# 2. Run with Docker
docker-compose up -d

# 3. Test
curl http://localhost:8000/health

# 4. Run tests
chmod +x test_confluence_style.sh
./test_confluence_style.sh
```

---

## 📚 API Reference

### POST /search

**Basic Search:**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "filenames",
  "search_queries": ["BGP configuration"],
  "embedding_model": "granite-embedding:30m",
  "limit": 5
}'
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `collection_name` | string | ✅ | - | Qdrant collection name |
| `search_queries` | array | ✅ | - | Search queries (min 1) |
| `filter` | object | ❌ | null | Filter conditions |
| `embedding_model` | string | ❌ | mxbai-embed-large | Ollama model |
| `limit` | integer | ❌ | 5 | Results per query |
| `context_window_size` | integer | ❌ | 5 | Pages before/after |
| `use_production` | boolean | ❌ | false | Use PROD config |

---

## 🔍 Filter Examples

### 1. Single Value (v2 Compatible)

```json
{
  "filter": {
    "metadata.filename": {
      "match_text": "ECOS_9.2.4.0_Release_Notes_RevB.pdf"
    }
  }
}
```

### 2. Multiple Values - Array (NEW in v3)

```json
{
  "filter": {
    "metadata.filename": {
      "match_text": [
        "ECOS_9.2.4.0_Release_Notes_RevB.pdf",
        "ECOS_9.1.4.2_Release_Notes_RevC.pdf"
      ]
    }
  }
}
```
**Logic**: File1 OR File2

### 3. Page Range (NEW in v3)

```json
{
  "filter": {
    "metadata.page_number": {
      "gte": 10,
      "lte": 20
    }
  }
}
```
**Logic**: Pages 10 through 20

### 4. Multiple Pages - Array (NEW in v3)

```json
{
  "filter": {
    "metadata.page_number": {
      "match_value": [1, 2, 3, 4, 5]
    }
  }
}
```
**Logic**: Page 1 OR 2 OR 3 OR 4 OR 5

### 5. Complex Multi-Field (NEW in v3)

```json
{
  "filter": {
    "metadata.filename": {
      "match_text": ["file1.pdf", "file2.pdf"]
    },
    "metadata.element_type": {
      "match_text": "Table"
    },
    "metadata.page_number": {
      "match_value": [1, 2, 3, 4, 5]
    }
  }
}
```
**Logic**: (File1 OR File2) AND Table AND (Page1 OR 2 OR 3 OR 4 OR 5)

---

## 📖 Complete Examples

### Example 1: Search Multiple Files

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "filenames",
  "search_queries": ["VPN tunnel configuration"],
  "filter": {
    "metadata.filename": {
      "match_text": [
        "ECOS_9.2.4.0_Release_Notes_RevB.pdf",
        "ECOS_9.1.4.2_Release_Notes_RevC.pdf"
      ]
    }
  },
  "embedding_model": "granite-embedding:30m",
  "use_production": true,
  "limit": 10
}'
```

### Example 2: Search Page Range

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "content",
  "search_queries": ["installation guide"],
  "filter": {
    "metadata.page_number": {
      "gte": 1,
      "lte": 10
    }
  },
  "embedding_model": "bge-m3",
  "limit": 5
}'
```

### Example 3: Complex Filter

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "releasenotes-bge-m3",
  "search_queries": ["BGP OSPF routing"],
  "filter": {
    "metadata.filename": {
      "match_text": [
        "ECOS_9.3.2.3_Release_Notes_RevC.pdf",
        "ECOS_9.4.2.6_Release_Notes_RevA.pdf"
      ]
    },
    "metadata.element_type": {
      "match_text": "Table"
    },
    "metadata.page_number": {
      "match_value": [40, 41, 42, 43, 44, 45]
    }
  },
  "embedding_model": "bge-m3",
  "limit": 10,
  "context_window_size": 2
}'
```

### Example 4: Multi-Query Batch

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "filenames",
  "search_queries": [
    "BGP configuration",
    "OSPF routing",
    "IPSec tunnels"
  ],
  "filter": {
    "metadata.filename": {
      "match_text": [
        "ECOS_9.2.4.0_Release_Notes_RevB.pdf",
        "ECOS_9.1.4.2_Release_Notes_RevC.pdf"
      ]
    }
  },
  "embedding_model": "granite-embedding:30m",
  "limit": 3
}'
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Global Settings
ENVIRONMENT=development
DEBUG=false
REQUEST_TIMEOUT=30

# Development Environment
DEV_QDRANT_URL=http://192.168.254.22:6333
DEV_QDRANT_API_KEY=
DEV_QDRANT_VERIFY_SSL=false

# Production Environment
PROD_QDRANT_URL=https://your-qdrant-cloud.io:6333
PROD_QDRANT_API_KEY=your-api-key-here
PROD_QDRANT_VERIFY_SSL=true

# Ollama Service
OLLAMA_HOST=192.168.254.22

# Context Window
CONTEXT_WINDOW_SIZE=5

# Embedding Models
DEV_FILENAMES_EMBEDDING_MODEL=granite-embedding:30m
DEV_CONTENT_EMBEDDING_MODEL=bge-m3
PROD_FILENAMES_EMBEDDING_MODEL=granite-embedding:30m
PROD_CONTENT_EMBEDDING_MODEL=bge-m3
```

---

## 🔄 Migration from v2

### 100% Backward Compatible!

All v2 code works without changes. New features are optional.

**v2 Code (Still Works):**
```json
{
  "collection_name": "filenames",
  "search_queries": ["BGP"],
  "filter": {
    "metadata.filename": {
      "match_text": "file.pdf"
    }
  }
}
```

**v3 Enhanced (Optional):**
```json
{
  "collection_name": "filenames",
  "search_queries": ["BGP"],
  "filter": {
    "metadata.filename": {
      "match_text": ["file1.pdf", "file2.pdf", "file3.pdf"]
    }
  },
  "use_production": true,
  "context_window_size": 3
}
```

---

## 📊 Collections

### 1. Filenames Collection
- **Model**: granite-embedding:30m (384 dims)
- **Fields**: filename, page_number, element_type, pagecontent

### 2. Content Collection
- **Model**: bge-m3 (1024 dims)
- **Fields**: filename, page_number, pagecontent

### 3. Release Notes Collection
- **Model**: bge-m3 (1024 dims)
- **Fields**: filename, page_number, element_type, md5_hash, pagecontent

---

## 🧪 Testing

### Run All Tests
```bash
chmod +x test_confluence_style.sh
./test_confluence_style.sh
```

### Test Results
- **Total**: 35 tests
- **Passed**: 34
- **Failed**: 1
- **Success Rate**: 97%

### Test Coverage
- ✅ Filenames collection (5 tests)
- ✅ Content collection (3 tests)
- ✅ Release notes collection (10 tests)
- ✅ Production environment (2/3 tests)
- ✅ Multi-query batch (3 tests)
- ✅ Edge cases (3 tests)
- ✅ Backward compatibility (2 tests)
- ✅ Performance tests (4 tests)

---

## 🎯 Use Cases

### 1. Search Across Multiple Files
```bash
# Search all release notes for security info
"filter": {
  "metadata.filename": {
    "match_text": [
      "ECOS_9.2.4.0_Release_Notes_RevB.pdf",
      "ECOS_9.1.4.2_Release_Notes_RevC.pdf",
      "ECOS_9.1.0.0_Release_Notes_RevA.pdf"
    ]
  }
}
```

### 2. Search Only in Tables
```bash
# Find info specifically in table format
"filter": {
  "metadata.element_type": {
    "match_text": "Table"
  }
}
```

### 3. Search First 10 Pages
```bash
# Quick search in introduction sections
"filter": {
  "metadata.page_number": {
    "gte": 1,
    "lte": 10
  }
}
```

### 4. Complex Search
```bash
# Specific files + tables + page range
"filter": {
  "metadata.filename": {
    "match_text": ["file1.pdf", "file2.pdf"]
  },
  "metadata.element_type": {
    "match_text": "Table"
  },
  "metadata.page_number": {
    "gte": 40,
    "lte": 50
  }
}
```

---

## 🔐 Security

### HTTPS/SSL
```bash
# Development (HTTP)
DEV_QDRANT_URL=http://192.168.254.22:6333
DEV_QDRANT_VERIFY_SSL=false

# Production (HTTPS)
PROD_QDRANT_URL=https://your-cloud.io:6333
PROD_QDRANT_API_KEY=your-secret-key
PROD_QDRANT_VERIFY_SSL=true
```

### API Key Authentication
```bash
# Set in environment
PROD_QDRANT_API_KEY=your-secret-key

# Or override per-request
{
  "qdrant_api_key": "request-specific-key"
}
```

---

## 🚨 Troubleshooting

### Connection Refused
```bash
# Check Qdrant is running
curl http://192.168.254.22:6333/collections

# Check .env configuration
cat .env | grep QDRANT
```

### Embedding Failed
```bash
# Check Ollama is running
curl http://192.168.254.22:11434/api/tags

# Pull required models
ollama pull granite-embedding:30m
ollama pull bge-m3
```

### Empty Results
- Check collection exists
- Verify filter conditions
- Try without filters first
- Check embedding model matches collection

### SSL Certificate Error
```bash
# For development only
QDRANT_FORCE_IGNORE_SSL=true
```

### Debug Mode
```bash
DEBUG=true
docker-compose logs -f search_api
```

---

## 📖 Additional Documentation

- **[FILTERING_EXAMPLES.md](FILTERING_EXAMPLES.md)** - 40+ real-world examples
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick lookup guide
- **[TESTING_PLAN.md](TESTING_PLAN.md)** - Test strategy
- **[TEST_RESULTS.md](TEST_RESULTS.md)** - Detailed results

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- **Qdrant** - Vector database
- **Ollama** - Embedding service
- **FastAPI** - Web framework
- **Pydantic** - Data validation

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Crypto-Gi/qdrant_search_api_v3/issues)
- **Docs**: See repository documentation
- **Examples**: Check FILTERING_EXAMPLES.md

---

## 🗺️ Roadmap

### v0.2 (Planned)
- [ ] GraphQL support
- [ ] Caching layer (Redis)
- [ ] Rate limiting
- [ ] Batch upload API

### v0.3 (Future)
- [ ] Web UI dashboard
- [ ] Monitoring and metrics
- [ ] Multi-tenancy support

---

## 📊 Performance

- **Single Query**: ~200-500ms
- **Batch Query (10)**: ~1-2s
- **Context Retrieval**: ~50-100ms per result
- **Throughput**: ~100-200 req/s

---

## 🔖 Version History

### v0.1 (Current - November 2025)
- ✅ Array filter support
- ✅ Range filter support
- ✅ Dual environment support
- ✅ Enhanced security
- ✅ Configurable context window
- ✅ 100% backward compatible
- ✅ 35 test cases (97% pass rate)

---

**Built with ❤️ for semantic search excellence**

**Repository**: https://github.com/Crypto-Gi/qdrant_search_api_v3

**Version**: 0.1 | **Status**: Production Ready | **License**: MIT
