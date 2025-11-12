# API Testing Guide for MCP Tool Development

**Purpose**: Test and document actual API behavior before implementing MCP tools

**Principle**: No guesswork - observe real API responses, then design tools

---

## 🧪 Testing Workflow

For each tool, follow this process:

1. **Test API endpoint with curl**
2. **Save actual response**
3. **Analyze response structure**
4. **Document findings**
5. **Design tool based on reality**

---

## Tool 1: search_filenames_fuzzy

### API Endpoint
`POST /search/filenames`

### Test Commands

#### Test 1: Basic filename search
```bash
curl -X POST "http://localhost:8001/search/filenames" \
  -H "Content-Type: application/json" \
  -d '{
  "query": "ecos 9.3",
  "collection_name": "content",
  "limit": 5,
  "use_production": true
}' | jq '.' > test_results/tool1_test1.json
```

#### Test 2: Orchestrator search
```bash
curl -X POST "http://localhost:8001/search/filenames" \
  -H "Content-Type: application/json" \
  -d '{
  "query": "orchestrator",
  "collection_name": "content",
  "limit": 10,
  "use_production": true
}' | jq '.' > test_results/tool1_test2.json
```

#### Test 3: Limit parameter
```bash
curl -X POST "http://localhost:8001/search/filenames" \
  -H "Content-Type: application/json" \
  -d '{
  "query": "release notes",
  "collection_name": "content",
  "limit": 3,
  "use_production": true
}' | jq '.' > test_results/tool1_test3.json
```

### Response Analysis

**Fields to document:**
- [ ] Response structure (nested objects, arrays?)
- [ ] Field names (exact spelling, case)
- [ ] Data types (string, number, boolean, null?)
- [ ] Optional vs required fields
- [ ] Redundant data to remove
- [ ] Error response format

**Questions to answer:**
- What does the response look like with 0 results?
- What happens with invalid collection name?
- Are scores included? If so, what range?
- Is metadata included? What fields?

---

## Tool 2: search_with_filename_filter

### API Endpoint
`POST /search`

### Test Commands

#### Test 1: Single query with exact filename
```bash
curl -X POST "http://localhost:8001/search" \
  -H "Content-Type: application/json" \
  -d '{
  "search_queries": ["security vulnerabilities"],
  "collection_name": "content",
  "limit": 3,
  "embedding_model": "bge-m3",
  "context_window_size": 5,
  "filter": {
    "metadata.filename": {
      "match_value": "ECOS_9.3.7.0_Release_Notes_RevB"
    }
  },
  "use_production": true
}' | jq '.' > test_results/tool2_test1.json
```

#### Test 2: Different context window
```bash
curl -X POST "http://localhost:8001/search" \
  -H "Content-Type: application/json" \
  -d '{
  "search_queries": ["DHCP configuration"],
  "collection_name": "content",
  "limit": 2,
  "embedding_model": "bge-m3",
  "context_window_size": 2,
  "filter": {
    "metadata.filename": {
      "match_value": "ECOS_9.3.7.0_Release_Notes_RevB"
    }
  },
  "use_production": true
}' | jq '.' > test_results/tool2_test2.json
```

#### Test 3: Zero context window
```bash
curl -X POST "http://localhost:8001/search" \
  -H "Content-Type: application/json" \
  -d '{
  "search_queries": ["bug fixes"],
  "collection_name": "content",
  "limit": 1,
  "embedding_model": "bge-m3",
  "context_window_size": 0,
  "filter": {
    "metadata.filename": {
      "match_value": "ECOS_9.3.7.0_Release_Notes_RevB"
    }
  },
  "use_production": true
}' | jq '.' > test_results/tool2_test3.json
```

### Response Analysis

**Fields to document:**
- [ ] How are results structured? (nested arrays?)
- [ ] What fields are in each result?
- [ ] How is `combined_page` formatted?
- [ ] What's in `page_numbers` array?
- [ ] How is `center_page` indicated?
- [ ] Score range and meaning
- [ ] Filename duplication (in result vs filter?)

**Questions to answer:**
- How does context_window_size affect page_numbers?
- Is combined_page a single string or array?
- Are pages in chronological order?
- What happens with invalid filename?
- What's the structure with 0 results?

---

## Tool 3: search_multi_query_with_filter

### API Endpoint
`POST /search` (with array of queries)

### Test Commands

#### Test 1: Three queries on same file
```bash
curl -X POST "http://localhost:8001/search" \
  -H "Content-Type: application/json" \
  -d '{
  "search_queries": [
    "security vulnerabilities",
    "performance improvements",
    "bug fixes"
  ],
  "collection_name": "content",
  "limit": 2,
  "embedding_model": "bge-m3",
  "context_window_size": 3,
  "filter": {
    "metadata.filename": {
      "match_value": "ECOS_9.3.7.0_Release_Notes_RevB"
    }
  },
  "use_production": true
}' | jq '.' > test_results/tool3_test1.json
```

#### Test 2: Five queries
```bash
curl -X POST "http://localhost:8001/search" \
  -H "Content-Type: application/json" \
  -d '{
  "search_queries": [
    "DHCP",
    "routing",
    "VLAN",
    "security",
    "performance"
  ],
  "collection_name": "content",
  "limit": 1,
  "embedding_model": "bge-m3",
  "context_window_size": 2,
  "filter": {
    "metadata.filename": {
      "match_value": "ECOS_9.3.7.0_Release_Notes_RevB"
    }
  },
  "use_production": true
}' | jq '.' > test_results/tool3_test2.json
```

### Response Analysis

**Fields to document:**
- [ ] How are multiple query results structured?
- [ ] Is it an array of arrays?
- [ ] How to map results back to queries?
- [ ] Are results in same order as queries?
- [ ] What if one query has 0 results?

**Questions to answer:**
- How to identify which result belongs to which query?
- Are empty result arrays included?
- Is there a query identifier in results?
- What's the maximum number of queries supported?

---

## Tool 4: search_across_multiple_files

### API Endpoint
Multiple calls to `POST /search`

### Test Commands

#### Test 1: Same query, three files
```bash
# File 1
curl -X POST "http://localhost:8001/search" \
  -H "Content-Type: application/json" \
  -d '{
  "search_queries": ["DHCP security"],
  "collection_name": "content",
  "limit": 2,
  "embedding_model": "bge-m3",
  "context_window_size": 3,
  "filter": {
    "metadata.filename": {
      "match_value": "ECOS_9.3.7.0_Release_Notes_RevB"
    }
  },
  "use_production": true
}' | jq '.' > test_results/tool4_file1.json

# File 2
curl -X POST "http://localhost:8001/search" \
  -H "Content-Type: application/json" \
  -d '{
  "search_queries": ["DHCP security"],
  "collection_name": "content",
  "limit": 2,
  "embedding_model": "bge-m3",
  "context_window_size": 3,
  "filter": {
    "metadata.filename": {
      "match_value": "ECOS_9.3.6.0_Release_Notes_RevB"
    }
  },
  "use_production": true
}' | jq '.' > test_results/tool4_file2.json

# File 3
curl -X POST "http://localhost:8001/search" \
  -H "Content-Type: application/json" \
  -d '{
  "search_queries": ["DHCP security"],
  "collection_name": "content",
  "limit": 2,
  "embedding_model": "bge-m3",
  "context_window_size": 3,
  "filter": {
    "metadata.filename": {
      "match_value": "ECOS_9.3.5.0_Release_Notes_RevA"
    }
  },
  "use_production": true
}' | jq '.' > test_results/tool4_file3.json
```

### Response Analysis

**Design decisions:**
- [ ] How to aggregate results from multiple calls?
- [ ] Should we preserve score ordering across files?
- [ ] How to handle files with 0 results?
- [ ] Should we include filename in each result?
- [ ] How to indicate which file each result came from?

---

## Tool 5: compare_versions

### API Endpoint
Two calls to `POST /search`

### Test Commands

#### Test 1: Compare DHCP security across versions
```bash
# Version 1 (9.3.6.0)
curl -X POST "http://localhost:8001/search" \
  -H "Content-Type: application/json" \
  -d '{
  "search_queries": ["DHCP security fixes"],
  "collection_name": "content",
  "limit": 3,
  "embedding_model": "bge-m3",
  "context_window_size": 3,
  "filter": {
    "metadata.filename": {
      "match_value": "ECOS_9.3.6.0_Release_Notes_RevB"
    }
  },
  "use_production": true
}' | jq '.' > test_results/tool5_version1.json

# Version 2 (9.3.7.0)
curl -X POST "http://localhost:8001/search" \
  -H "Content-Type: application/json" \
  -d '{
  "search_queries": ["DHCP security fixes"],
  "collection_name": "content",
  "limit": 3,
  "embedding_model": "bge-m3",
  "context_window_size": 3,
  "filter": {
    "metadata.filename": {
      "match_value": "ECOS_9.3.7.0_Release_Notes_RevB"
    }
  },
  "use_production": true
}' | jq '.' > test_results/tool5_version2.json
```

### Response Analysis

**Design decisions:**
- [ ] How to structure side-by-side comparison?
- [ ] Should we extract version numbers from filenames?
- [ ] How to highlight differences?
- [ ] Should results be interleaved or grouped?
- [ ] How to handle missing information in one version?

---

## 📊 Response Sanitization Strategy

After testing, document how to sanitize responses:

### Remove Redundant Data
- [ ] Duplicate filename fields
- [ ] Unnecessary metadata
- [ ] Internal IDs
- [ ] Debug information

### Flatten Structure
- [ ] Nested arrays that can be flattened
- [ ] Single-item arrays
- [ ] Wrapper objects

### Optimize for LLM
- [ ] Shorten field names where clear
- [ ] Remove null/empty fields
- [ ] Consolidate related fields
- [ ] Use arrays efficiently

### Example Transformation

**Before (API Response):**
```json
{
  "results": [[
    {
      "filename": "ECOS_9.3.7.0_Release_Notes_RevB",
      "score": 0.89,
      "center_page": 15,
      "combined_page": "Security fixes...",
      "page_numbers": [13, 14, 15, 16, 17],
      "metadata": {...}
    }
  ]]
}
```

**After (Sanitized for MCP):**
```json
{
  "query": "security fixes",
  "file": "ECOS_9.3.7.0_Release_Notes_RevB",
  "results": [
    {
      "score": 0.89,
      "page": 15,
      "pages": "13-17",
      "content": "Security fixes..."
    }
  ]
}
```

---

## 📝 Documentation Template

For each tool, document:

```markdown
## Tool X: [name]

### API Endpoint
[endpoint]

### Actual Response Structure
[paste actual JSON]

### Response Fields
| Field | Type | Always Present? | Purpose | Keep in MCP? |
|-------|------|-----------------|---------|--------------|
| ... | ... | ... | ... | ... |

### Sanitization Rules
1. Remove: [fields to remove]
2. Flatten: [structures to flatten]
3. Rename: [field renames]
4. Add: [computed fields]

### Final MCP Output Structure
[sanitized JSON structure]

### Edge Cases Observed
- [ ] Empty results: [behavior]
- [ ] Invalid input: [error format]
- [ ] Missing data: [how handled]

### Notes
[any important observations]
```

---

## ✅ Testing Checklist

Before implementing each tool:

- [ ] Run all test curl commands
- [ ] Save responses to `test_results/` directory
- [ ] Document actual response structure
- [ ] Identify redundant data
- [ ] Design sanitization strategy
- [ ] Create sanitized output example
- [ ] Document edge cases
- [ ] Review with team

---

**Remember**: The goal is to understand reality, not assumptions. Let the API tell you how it works!
