"""
Docsplorer - Document Explorer MCP Server

Model Context Protocol server for semantic search through documentation and release notes.
Uses Qdrant vector database for intelligent document discovery and content retrieval.
Provides 5 specialized tools for exploring, searching, and comparing documentation.
"""

import httpx
from fastmcp import FastMCP
from config import MCPConfig
from typing import Optional

# Initialize MCP server and config
mcp = FastMCP("Docsplorer")
config = MCPConfig()


@mcp.tool()
async def search_filenames_fuzzy(
    query: str,
    limit: Optional[int] = None
) -> dict:
    """
    Discover available documents using fuzzy filename search.
    
    **When to use this tool:**
    - You don't know the exact filename
    - User asks "What files are available about X?"
    - Need to discover documentation before searching content
    - Finding release notes for a specific version or product
    
    **How it works:**
    - Performs fuzzy matching on filenames (handles typos and variations)
    - Returns ranked list of matching documents with relevance scores
    - Use the returned filenames in other search tools
    
    **Workflow:**
    1. Call this tool first to discover filenames
    2. Use returned filename in search_with_filename_filter or other tools
    3. Get actual content from discovered documents
    
    Args:
        query: Filename search term. Examples:
               - "ecos 9.3" → finds ECOS_9.3.x_Release_Notes
               - "release notes" → finds all release note files
               - "dhcp documentation" → finds DHCP-related docs
        limit: Maximum filenames to return. Defaults to .env DEFAULT_LIMIT (typically 1).
               Increase for broader discovery (e.g., 5-10).
        
    Returns:
        dict: {
            "query": str,              # Your search query
            "total_matches": int,      # Total files found
            "filenames": [             # Ranked list of matches
                {
                    "filename": str,   # Exact filename to use in other tools
                    "score": float     # Relevance score (0-1, higher is better)
                }
            ]
        }
        
    Example:
        # Discover ECOS 9.3 files
        search_filenames_fuzzy("ecos 9.3", limit=5)
        
        # Returns:
        # {
        #   "query": "ecos 9.3",
        #   "total_matches": 3,
        #   "filenames": [
        #     {"filename": "ECOS_9.3.6.0_Release_Notes_RevB", "score": 0.95},
        #     {"filename": "ECOS_9.3.7.0_Release_Notes_RevA", "score": 0.93}
        #   ]
        # }
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{config.api_url}/search/filenames",
            json={
                "query": query,
                "collection_name": config.qdrant_collection,
                "limit": limit or config.default_limit,
                "use_production": config.use_production
            },
            headers=config.get_headers()
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def search_with_filename_filter(
    query: str,
    filename_filter: str,
    limit: Optional[int] = None,
    context_window: Optional[int] = None
) -> dict:
    """
    Search for specific content within a single document using semantic matching.
    
    **When to use this tool:**
    - You know the filename (from search_filenames_fuzzy)
    - User asks "What does document X say about Y?"
    - Need specific information from one known document
    - Want context pages around matching content
    - Single topic in single document
    
    **How it works:**
    - Uses semantic search (understands meaning, not just keywords)
    - Finds most relevant passages in the document
    - Returns surrounding pages for context
    - Deduplicates pages across results
    
    **Don't use this tool if:**
    - You need to search multiple documents (use search_across_multiple_files)
    - You have multiple topics (use search_multi_query_with_filter)
    - You don't know the filename (use search_filenames_fuzzy first)
    
    Args:
        query: What to search for. Be specific. Examples:
               - "security vulnerabilities" → finds security issues
               - "DHCP configuration steps" → finds DHCP setup info
               - "performance improvements" → finds performance changes
        filename_filter: Which document to search. Can be:
                        - Exact: "ECOS_9.3.6.0_Release_Notes_RevB"
                        - Partial: "ECOS_9.3.6" (matches full filename)
        limit: Max results to return. Defaults to .env DEFAULT_LIMIT (typically 1).
               - Use 1-2 for focused answers
               - Use 3-5 for comprehensive coverage
        context_window: Pages before/after match. Defaults to .env DEFAULT_CONTEXT_WINDOW (typically 5).
                       - Range: 0-11 (total pages = window*2 + 1)
                       - Use 1-2 for just the match
                       - Use 5-7 for good context
                       - Use 10-11 for maximum context
        
    Returns:
        dict: {
            "results": [[                    # Nested array of results
                {
                    "filename": str,         # Document filename
                    "score": float,          # Relevance score (0-1)
                    "center_page": int,      # Page number of best match
                    "combined_page": str,    # Full text of all context pages
                    "page_numbers": [int]    # List of page numbers included
                }
            ]]
        }
        
    Example:
        # Find security info in ECOS 9.3.6
        search_with_filename_filter(
            query="security vulnerabilities",
            filename_filter="ECOS_9.3.6.0_Release_Notes_RevB",
            limit=2,
            context_window=5
        )
        
        # Returns passages about security with 5 pages before/after (11 total pages)
    """
    payload = config.build_search_payload(
        search_queries=[query],
        limit=limit,
        context_window_size=context_window,
        filter_dict={"metadata.filename": {"match_text": filename_filter}}
    )
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{config.api_url}/search",
            json=payload,
            headers=config.get_headers()
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def search_multi_query_with_filter(
    queries: list[str],
    filename_filter: str,
    limit: Optional[int] = None,
    context_window: Optional[int] = None
) -> dict:
    """
    Run multiple searches within ONE document efficiently (batch processing).
    
    **When to use this tool:**
    - User asks to analyze document for multiple topics
    - Example: "Analyze ECOS 9.3.6 for security, performance, and bugs"
    - Need comprehensive document analysis
    - Multiple topics, single document
    - Want to avoid calling search_with_filename_filter multiple times
    
    **How it works:**
    - Runs all queries in one efficient batch operation
    - Each query gets separate results
    - All queries search the same document
    - Faster than calling search_with_filename_filter multiple times
    
    **Don't use this tool if:**
    - Single topic (use search_with_filename_filter instead)
    - Multiple documents (use search_across_multiple_files instead)
    - Only 1 query (use search_with_filename_filter instead)
    
    **Best practices:**
    - Group 3-5 related queries for optimal performance
    - Keep queries thematically related
    - Use for comprehensive document analysis
    
    Args:
        queries: List of search queries. Each query is independent. Examples:
                - ["security", "performance", "bugs"] → 3 separate searches
                - ["DHCP", "DNS", "routing"] → network features
                - ["memory leak", "crash", "timeout"] → problem diagnosis
        filename_filter: Which document to search (exact or partial filename)
        limit: Max results per query. Defaults to .env DEFAULT_LIMIT.
               Each query gets this many results independently.
        context_window: Pages before/after match. Defaults to .env DEFAULT_CONTEXT_WINDOW.
                       Applied to all queries.
        
    Returns:
        dict: {
            "results": [
                [results_for_query_1],  # First query results
                [results_for_query_2],  # Second query results
                [results_for_query_3],  # Third query results
                ...
            ]
        }
        # Results array matches queries array order
        
    Example:
        # Comprehensive analysis of ECOS 9.3.6
        search_multi_query_with_filter(
            queries=["security fixes", "performance improvements", "bug fixes"],
            filename_filter="ECOS_9.3.6.0_Release_Notes",
            limit=2,
            context_window=5
        )
        
        # Returns 3 sets of results, one for each query
    """
    payload = config.build_search_payload(
        search_queries=queries,
        limit=limit,
        context_window_size=context_window,
        filter_dict={"metadata.filename": {"match_text": filename_filter}}
    )
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{config.api_url}/search",
            json=payload,
            headers=config.get_headers()
        )
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def search_across_multiple_files(
    query: str,
    filename_filters: list[str],
    limit: Optional[int] = None,
    context_window: Optional[int] = None
) -> dict:
    """
    Search for ONE topic across MULTIPLE documents (cross-file search).
    
    **When to use this tool:**
    - User asks "How is X covered in versions A, B, and C?"
    - Track feature evolution across versions
    - Compare documentation across products
    - Find all mentions of a topic in multiple files
    - Single topic, multiple documents
    
    **How it works:**
    - Same query runs against all specified documents
    - Results grouped by filename for easy comparison
    - Each file gets independent results
    - Perfect for version tracking and comparison
    
    **Don't use this tool if:**
    - Single document (use search_with_filename_filter instead)
    - Multiple topics (use search_multi_query_with_filter instead)
    - Comparing only 2 versions (use compare_versions instead)
    
    **Best practices:**
    - Use for 3+ documents
    - Keep documents related (e.g., different versions)
    - Use same query for all files for meaningful comparison
    
    Args:
        query: Single search query for all documents. Examples:
               - "DHCP security" → finds DHCP security in all files
               - "performance improvements" → tracks performance across versions
               - "CVE-2023-12345" → finds vulnerability mentions
        filename_filters: List of documents to search. Can be:
                         - Exact: ["ECOS_9.3.5.0_Release_Notes_RevB", ...]
                         - Partial: ["ECOS_9.3.5", "ECOS_9.3.6", "ECOS_9.3.7"]
        limit: Max results per file. Defaults to .env DEFAULT_LIMIT.
               Each file gets this many results independently.
        context_window: Pages before/after match. Defaults to .env DEFAULT_CONTEXT_WINDOW.
                       Applied to all files.
        
    Returns:
        dict: {
            "query": str,                    # Your search query
            "results_by_file": {            # Results grouped by filename
                "filename1": [results],      # Results from first file
                "filename2": [results],      # Results from second file
                "filename3": [results],      # Results from third file
                ...
            }
        }
        
    Example:
        # Track DHCP security across 3 ECOS versions
        search_across_multiple_files(
            query="DHCP security",
            filename_filters=[
                "ECOS_9.3.5.0_Release_Notes",
                "ECOS_9.3.6.0_Release_Notes",
                "ECOS_9.3.7.0_Release_Notes"
            ],
            limit=2,
            context_window=5
        )
        
        # Returns DHCP security info from all 3 versions, grouped by file
    """
    results_by_file = {}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for filename_filter in filename_filters:
            payload = config.build_search_payload(
                search_queries=[query],
                limit=limit,
                context_window_size=context_window,
                filter_dict={"metadata.filename": {"match_text": filename_filter}}
            )
            
            response = await client.post(
                f"{config.api_url}/search",
                json=payload,
                headers=config.get_headers()
            )
            response.raise_for_status()
            data = response.json()
            results_by_file[filename_filter] = data["results"][0] if data["results"] else []
    
    return {
        "query": query,
        "results_by_file": results_by_file
    }


@mcp.tool()
async def compare_versions(
    query: str,
    version1_filter: str,
    version2_filter: str,
    limit: Optional[int] = None,
    context_window: Optional[int] = None
) -> dict:
    """
    Compare how a topic appears in TWO versions side-by-side (before/after comparison).
    
    **When to use this tool:**
    - User asks "How did X change from version A to version B?"
    - Compare two specific versions
    - Track evolution between releases
    - Before/after analysis
    - Regression checking
    - Exactly 2 versions to compare
    
    **How it works:**
    - Searches same query in both versions
    - Returns structured side-by-side comparison
    - Perfect for "what changed" questions
    - Optimized for 2-version comparison
    
    **Don't use this tool if:**
    - More than 2 versions (use search_across_multiple_files instead)
    - Single version (use search_with_filename_filter instead)
    - Unrelated documents (use search_across_multiple_files instead)
    
    **Best practices:**
    - Use for adjacent versions (e.g., 9.3.6 → 9.3.7)
    - Same query for both versions
    - Compare related documents (same product/series)
    
    Args:
        query: Topic to compare across versions. Examples:
               - "DHCP security improvements" → see security changes
               - "memory leak fix" → track bug fix
               - "routing protocol" → feature evolution
        version1_filter: First version (older/baseline). Examples:
                        - "ECOS_9.3.6.0_Release_Notes"
                        - "Product_v1.0"
        version2_filter: Second version (newer/comparison). Examples:
                        - "ECOS_9.3.7.0_Release_Notes"
                        - "Product_v2.0"
        limit: Max results per version. Defaults to .env DEFAULT_LIMIT.
               Each version gets this many results.
        context_window: Pages before/after match. Defaults to .env DEFAULT_CONTEXT_WINDOW.
                       Applied to both versions.
        
    Returns:
        dict: {
            "query": str,                    # Your search query
            "version1": {                    # First version results
                "filename": str,             # Actual filename found
                "results": [results]         # Results from version 1
            },
            "version2": {                    # Second version results
                "filename": str,             # Actual filename found
                "results": [results]         # Results from version 2
            }
        }
        
    Example:
        # Compare DHCP security between ECOS 9.3.6 and 9.3.7
        compare_versions(
            query="DHCP security improvements",
            version1_filter="ECOS_9.3.6.0_Release_Notes",
            version2_filter="ECOS_9.3.7.0_Release_Notes",
            limit=2,
            context_window=5
        )
        
        # Returns side-by-side comparison of DHCP security in both versions
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get results for version 1
        payload_v1 = config.build_search_payload(
            search_queries=[query],
            limit=limit,
            context_window_size=context_window,
            filter_dict={"metadata.filename": {"match_text": version1_filter}}
        )
        response_v1 = await client.post(
            f"{config.api_url}/search",
            json=payload_v1,
            headers=config.get_headers()
        )
        response_v1.raise_for_status()
        data_v1 = response_v1.json()
        
        # Get results for version 2
        payload_v2 = config.build_search_payload(
            search_queries=[query],
            limit=limit,
            context_window_size=context_window,
            filter_dict={"metadata.filename": {"match_text": version2_filter}}
        )
        response_v2 = await client.post(
            f"{config.api_url}/search",
            json=payload_v2,
            headers=config.get_headers()
        )
        response_v2.raise_for_status()
        data_v2 = response_v2.json()
    
    return {
        "query": query,
        "version1": {
            "filename": version1_filter,
            "results": data_v1["results"][0] if data_v1["results"] else []
        },
        "version2": {
            "filename": version2_filter,
            "results": data_v2["results"][0] if data_v2["results"] else []
        }
    }


if __name__ == "__main__":
    # Run with stdio transport (default for MCP)
    print(f"Starting Qdrant RAG MCP Server with config: {config}")
    mcp.run()
