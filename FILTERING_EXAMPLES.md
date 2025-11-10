# Qdrant Search API - Filtering Examples

Complete guide showing **OLD** (backward compatible) and **NEW** (enhanced) filtering capabilities.

## Collections in Production

1. **filenames** - 384 dimensions (granite-embedding:30m)
   - Fields: `metadata.filename`, `metadata.page_number`, `metadata.element_type`, `pagecontent`

2. **content** - 1024 dimensions (bge-m3)
   - Fields: `metadata.filename`, `metadata.page_number`, `pagecontent`

3. **releasenotes-bge-m3** - 1024 dimensions (bge-m3)
   - Fields: `metadata.filename`, `metadata.page_number`, `metadata.element_type`, `metadata.md5_hash`, `pagecontent`

---

## 1. FILENAMES Collection Examples

### 1.1 Basic Search (OLD & NEW - Same)

**Description**: Simple search without filters

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "filenames",
  "search_queries": ["BGP routing configuration"],
  "embedding_model": "granite-embedding:30m",
  "use_production": true,
  "limit": 5
}'
```

---

### 1.2 Single Filename Filter (OLD Way - Still Works)

**Description**: Filter by one specific filename

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "filenames",
  "search_queries": ["OSPF configuration"],
  "filter": {
    "metadata.filename": {
      "match_text": "ECOS_9.2.4.0_Release_Notes_RevB.pdf"
    }
  },
  "embedding_model": "granite-embedding:30m",
  "use_production": true,
  "limit": 5
}'
```

---

### 1.3 Multiple Filenames Filter (NEW - Array Support)

**Description**: Search across multiple files using OR logic

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
        "ECOS_9.1.4.2_Release_Notes_RevC.pdf",
        "ECOS_9.1.0.0_Release_Notes_RevA.pdf"
      ]
    }
  },
  "embedding_model": "granite-embedding:30m",
  "use_production": true,
  "limit": 10
}'
```

**Logic**: Returns results from ANY of the three files (OR logic)

---

### 1.4 Single Element Type Filter (OLD Way - Still Works)

**Description**: Filter by element type (Table, Image, etc.)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "filenames",
  "search_queries": ["resolved issues"],
  "filter": {
    "metadata.element_type": {
      "match_text": "Table"
    }
  },
  "embedding_model": "granite-embedding:30m",
  "use_production": true,
  "limit": 10
}'
```

---

### 1.5 Multiple Element Types Filter (NEW - Array Support)

**Description**: Search in both Tables and Images

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "filenames",
  "search_queries": ["security features"],
  "filter": {
    "metadata.element_type": {
      "match_text": ["Table", "Image"]
    }
  },
  "embedding_model": "granite-embedding:30m",
  "use_production": true,
  "limit": 10
}'
```

**Logic**: Returns results from Tables OR Images

---

### 1.6 Single Page Number Filter (OLD Way - Still Works)

**Description**: Filter by specific page number

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "filenames",
  "search_queries": ["introduction"],
  "filter": {
    "metadata.page_number": {
      "match_value": 1
    }
  },
  "embedding_model": "granite-embedding:30m",
  "use_production": true,
  "limit": 5
}'
```

---

### 1.7 Multiple Page Numbers Filter (NEW - Array Support)

**Description**: Search across specific pages (e.g., first 5 pages)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "filenames",
  "search_queries": ["overview summary"],
  "filter": {
    "metadata.page_number": {
      "match_value": [1, 2, 3, 4, 5]
    }
  },
  "embedding_model": "granite-embedding:30m",
  "use_production": true,
  "limit": 10
}'
```

**Logic**: Returns results from pages 1, 2, 3, 4, OR 5

---

### 1.8 Page Range Filter (NEW - Range Support)

**Description**: Search within a page range

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "filenames",
  "search_queries": ["troubleshooting guide"],
  "filter": {
    "metadata.page_number": {
      "gte": 10,
      "lte": 20
    }
  },
  "embedding_model": "granite-embedding:30m",
  "use_production": true,
  "limit": 10
}'
```

**Logic**: Returns results from pages 10 through 20 (inclusive)

---

### 1.9 Complex Multi-Field Filter (OLD Way - AND Logic)

**Description**: Combine filename AND element type

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "filenames",
  "search_queries": ["feature description"],
  "filter": {
    "metadata.filename": {
      "match_text": "ECOS_9.2.4.0_Release_Notes_RevB.pdf"
    },
    "metadata.element_type": {
      "match_text": "Table"
    }
  },
  "embedding_model": "granite-embedding:30m",
  "use_production": true,
  "limit": 5
}'
```

**Logic**: Results must be from the specific file AND be a Table

---

### 1.10 Advanced Multi-Field with Arrays (NEW - AND + OR Logic)

**Description**: Multiple files AND specific pages AND element type

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "filenames",
  "search_queries": ["security configuration"],
  "filter": {
    "metadata.filename": {
      "match_text": [
        "ECOS_9.2.4.0_Release_Notes_RevB.pdf",
        "ECOS_9.1.4.2_Release_Notes_RevC.pdf"
      ]
    },
    "metadata.element_type": {
      "match_text": "Table"
    },
    "metadata.page_number": {
      "match_value": [1, 2, 3, 4, 5, 10, 15, 20]
    }
  },
  "embedding_model": "granite-embedding:30m",
  "use_production": true,
  "limit": 10
}'
```

**Logic**: 
- Must be from (File1 OR File2) 
- AND must be a Table
- AND must be on (page 1 OR 2 OR 3 OR 4 OR 5 OR 10 OR 15 OR 20)

---

### 1.11 Custom Context Window (NEW Feature)

**Description**: Override default context window size

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "filenames",
  "search_queries": ["IPSec tunnel"],
  "filter": {
    "metadata.filename": {
      "match_text": "ECOS_9.2.4.0_Release_Notes_RevB.pdf"
    }
  },
  "embedding_model": "granite-embedding:30m",
  "use_production": true,
  "limit": 5,
  "context_window_size": 2
}'
```

**Note**: Default is 5 pages (±5), this sets it to 2 pages (±2)

---

## 2. CONTENT Collection Examples

### 2.1 Basic Search (OLD & NEW - Same)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "content",
  "search_queries": ["ECOS features and capabilities"],
  "embedding_model": "bge-m3",
  "use_production": true,
  "limit": 5
}'
```

---

### 2.2 Single Filename Filter (OLD Way - Still Works)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "content",
  "search_queries": ["network configuration"],
  "filter": {
    "metadata.filename": {
      "match_text": "ECOS_9.2.4.0_Release_Notes_RevB.pdf"
    }
  },
  "embedding_model": "bge-m3",
  "use_production": true,
  "limit": 5
}'
```

---

### 2.3 Multiple Filenames Filter (NEW - Array Support)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "content",
  "search_queries": ["upgrade procedures"],
  "filter": {
    "metadata.filename": {
      "match_text": [
        "ECOS_9.2.4.0_Release_Notes_RevB.pdf",
        "ECOS_9.1.4.2_Release_Notes_RevC.pdf",
        "Orchestrator_Release_Notes_Version_9.3.3_RevA.pdf"
      ]
    }
  },
  "embedding_model": "bge-m3",
  "use_production": true,
  "limit": 10
}'
```

---

### 2.4 Page Range Filter (NEW - Range Support)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "content",
  "search_queries": ["installation steps"],
  "filter": {
    "metadata.page_number": {
      "gte": 1,
      "lte": 10
    }
  },
  "embedding_model": "bge-m3",
  "use_production": true,
  "limit": 10
}'
```

---

### 2.5 Filename + Page Range (NEW - Combined)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "content",
  "search_queries": ["getting started guide"],
  "filter": {
    "metadata.filename": {
      "match_text": "ECOS_9.2.4.0_Release_Notes_RevB.pdf"
    },
    "metadata.page_number": {
      "gte": 1,
      "lte": 5
    }
  },
  "embedding_model": "bge-m3",
  "use_production": true,
  "limit": 5
}'
```

---

### 2.6 Multiple Files + Specific Pages (NEW - Array + Array)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "content",
  "search_queries": ["release highlights"],
  "filter": {
    "metadata.filename": {
      "match_text": [
        "ECOS_9.2.4.0_Release_Notes_RevB.pdf",
        "ECOS_9.1.4.2_Release_Notes_RevC.pdf"
      ]
    },
    "metadata.page_number": {
      "match_value": [1, 2, 3]
    }
  },
  "embedding_model": "bge-m3",
  "use_production": true,
  "limit": 10
}'
```

---

### 2.7 Custom Context Window (NEW Feature)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "content",
  "search_queries": ["troubleshooting"],
  "embedding_model": "bge-m3",
  "use_production": true,
  "limit": 5,
  "context_window_size": 3
}'
```

---

## 3. RELEASENOTES-BGE-M3 Collection Examples

### 3.1 Basic Search (OLD & NEW - Same)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "releasenotes-bge-m3",
  "search_queries": ["BGP routing issues"],
  "embedding_model": "bge-m3",
  "use_production": false,
  "limit": 5
}'
```

---

### 3.2 Single Filename Filter (OLD Way - Still Works)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "releasenotes-bge-m3",
  "search_queries": ["security vulnerability"],
  "filter": {
    "metadata.filename": {
      "match_text": "ECOS_9.3.2.3_Release_Notes_RevC.pdf"
    }
  },
  "embedding_model": "bge-m3",
  "use_production": false,
  "limit": 5
}'
```

---

### 3.3 Multiple Filenames Filter (NEW - Array Support)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "releasenotes-bge-m3",
  "search_queries": ["appliance reboot issues"],
  "filter": {
    "metadata.filename": {
      "match_text": [
        "ECOS_9.3.2.3_Release_Notes_RevC.pdf",
        "ECOS_9.4.2.6_Release_Notes_RevA.pdf",
        "ECOS_9.2.4.0_Release_Notes_RevB.pdf"
      ]
    }
  },
  "embedding_model": "bge-m3",
  "use_production": false,
  "limit": 10
}'
```

---

### 3.4 Single Element Type Filter (OLD Way - Still Works)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "releasenotes-bge-m3",
  "search_queries": ["resolved issues"],
  "filter": {
    "metadata.element_type": {
      "match_text": "Table"
    }
  },
  "embedding_model": "bge-m3",
  "use_production": false,
  "limit": 10
}'
```

---

### 3.5 Multiple Element Types Filter (NEW - Array Support)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "releasenotes-bge-m3",
  "search_queries": ["security patches"],
  "filter": {
    "metadata.element_type": {
      "match_text": ["Table", "Image"]
    }
  },
  "embedding_model": "bge-m3",
  "use_production": false,
  "limit": 10
}'
```

---

### 3.6 Page Range Filter (NEW - Range Support)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "releasenotes-bge-m3",
  "search_queries": ["issue resolution"],
  "filter": {
    "metadata.page_number": {
      "gte": 40,
      "lte": 50
    }
  },
  "embedding_model": "bge-m3",
  "use_production": false,
  "limit": 10
}'
```

---

### 3.7 Specific Pages Array (NEW - Array Support)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "releasenotes-bge-m3",
  "search_queries": ["known issues"],
  "filter": {
    "metadata.page_number": {
      "match_value": [40, 41, 42, 43, 44, 45]
    }
  },
  "embedding_model": "bge-m3",
  "use_production": false,
  "limit": 10
}'
```

---

### 3.8 Complex Multi-Field (OLD Way - AND Logic)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "releasenotes-bge-m3",
  "search_queries": ["VPN configuration"],
  "filter": {
    "metadata.filename": {
      "match_text": "ECOS_9.3.2.3_Release_Notes_RevC.pdf"
    },
    "metadata.element_type": {
      "match_text": "Table"
    }
  },
  "embedding_model": "bge-m3",
  "use_production": false,
  "limit": 5
}'
```

---

### 3.9 Advanced Multi-Field with Arrays (NEW - Complex AND + OR)

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
      "match_value": [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
    }
  },
  "embedding_model": "bge-m3",
  "use_production": false,
  "limit": 10
}'
```

**Logic**:
- Must be from (File1 OR File2)
- AND must be a Table
- AND must be on (page 40 OR 41 OR 42... OR 50)

---

### 3.10 Custom Context Window (NEW Feature)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "releasenotes-bge-m3",
  "search_queries": ["memory leak"],
  "filter": {
    "metadata.filename": {
      "match_text": "ECOS_9.3.2.3_Release_Notes_RevC.pdf"
    }
  },
  "embedding_model": "bge-m3",
  "use_production": false,
  "limit": 5,
  "context_window_size": 2
}'
```

---

## 4. Multi-Query Examples (Batch Processing)

### 4.1 Multiple Queries - Simple (OLD & NEW - Same)

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
  "embedding_model": "granite-embedding:30m",
  "use_production": true,
  "limit": 3
}'
```

---

### 4.2 Multiple Queries with Array Filters (NEW)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "filenames",
  "search_queries": [
    "new features",
    "resolved issues",
    "upgrade considerations"
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
  "use_production": true,
  "limit": 5
}'
```

---

### 4.3 Large Batch Query (Performance Test)

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
  "collection_name": "releasenotes-bge-m3",
  "search_queries": [
    "BGP issues",
    "OSPF problems",
    "VPN tunnel",
    "firewall rules",
    "security patches",
    "upgrade issues",
    "memory leak",
    "appliance reboot"
  ],
  "embedding_model": "bge-m3",
  "use_production": false,
  "limit": 2
}'
```

---

## Summary of Capabilities

### OLD Code (GitHub Repo) - Backward Compatible ✅
- ✅ Single value filters (`match_text`, `match_value`)
- ✅ Multi-field AND logic
- ✅ Basic search
- ✅ Multi-query batch

### NEW Code (Your Enhanced Version) - All OLD + These ✅
- ✅ **Array filters** (OR logic within field)
- ✅ **Range filters** (`gte`, `lte`)
- ✅ **Complex AND + OR logic**
- ✅ **Configurable context window**
- ✅ **Dual environment** (DEV/PROD)
- ✅ **HTTPS/SSL support**
- ✅ **API key authentication**
- ✅ **Empty array validation**
- ✅ **Range validation**

### Filter Logic Summary

**Single Field**:
- OLD: `field = value`
- NEW: `field = value` OR `field IN [value1, value2, value3]`

**Multiple Fields**:
- OLD: `field1 = value1 AND field2 = value2`
- NEW: `(field1 IN [v1, v2]) AND (field2 IN [v3, v4]) AND (field3 >= min AND field3 <= max)`

**All OLD examples work in NEW code - 100% backward compatible!**
