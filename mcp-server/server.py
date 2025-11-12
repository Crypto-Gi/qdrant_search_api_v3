"""
Qdrant RAG MCP Server

Model Context Protocol server for semantic search with Qdrant vector database.
Provides 5 tools for document search, filtering, and version comparison.
"""

import httpx
from fastmcp import FastMCP
from config import MCPConfig

# Initialize MCP server and config
mcp = FastMCP("Qdrant RAG Search")
config = MCPConfig()


@mcp.tool()
async def search_filenames_fuzzy(
    query: str,
    limit: int = 5
) -> dict:
    """
    Fuzzy search for filenames in the document collection.
    
    Use this to discover available documents before searching their content.
    Returns unique filenames that match the query.
    
    Args:
        query: Filename search term (e.g., "ecos 9.3", "release notes")
        limit: Maximum number of filenames to return (default: 5)
        
    Returns:
        dict: {"query": str, "total_matches": int, "filenames": [{"filename": str, "score": float}]}
        
    Example:
        search_filenames_fuzzy("ecos 9.3", limit=5)
        → Returns list of ECOS 9.3.x release note filenames
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{config.api_url}/search/filenames",
            json={
                "query": query,
                "collection_name": config.qdrant_collection,
                "limit": limit,
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
    limit: int = 2,
    context_window: int = 5
) -> dict:
    """
    Search within a specific document with semantic matching.
    
    Finds relevant passages in a single document and returns surrounding context.
    Use after discovering filenames with search_filenames_fuzzy.
    
    Args:
        query: Search query (e.g., "security vulnerabilities", "DHCP configuration")
        filename_filter: Exact or partial filename to search within
        limit: Maximum results to return (default: 2)
        context_window: Pages before/after match to include (0-11, default: 5)
        
    Returns:
        dict: {
            "results": [[{
                "filename": str,
                "score": float,
                "center_page": int,
                "combined_page": str,  # Full page content
                "page_numbers": [int]  # Pages included
            }]]
        }
        
    Example:
        search_with_filename_filter(
            query="security fixes",
            filename_filter="ECOS_9.3.6.0_Release_Notes",
            limit=2,
            context_window=3
        )
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
    limit: int = 2,
    context_window: int = 5
) -> dict:
    """
    Search multiple queries within a single document simultaneously.
    
    Efficient for finding multiple related topics in one document.
    Each query returns independent results with deduplication across results.
    
    Args:
        queries: List of search queries (e.g., ["DHCP", "routing", "VLAN"])
        filename_filter: Exact or partial filename to search within
        limit: Maximum results per query (default: 2)
        context_window: Pages before/after match to include (0-11, default: 5)
        
    Returns:
        dict: {
            "results": [
                [result1_for_query1, result2_for_query1],  # Query 1 results
                [result1_for_query2, result2_for_query2],  # Query 2 results
                ...
            ]
        }
        
    Example:
        search_multi_query_with_filter(
            queries=["DHCP configuration", "routing protocol", "VLAN tagging"],
            filename_filter="ECOS_9.3.6.0",
            limit=2
        )
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
    limit: int = 2,
    context_window: int = 5
) -> dict:
    """
    Search the same query across multiple documents.
    
    Useful for comparing how different documents address the same topic.
    Returns results grouped by filename.
    
    Args:
        query: Single search query to run across all files
        filename_filters: List of filenames to search (e.g., ["ECOS_9.3.6.0", "ECOS_9.3.3.2"])
        limit: Maximum results per file (default: 2)
        context_window: Pages before/after match to include (0-11, default: 5)
        
    Returns:
        dict: {
            "query": str,
            "results_by_file": {
                "filename1": [results],
                "filename2": [results],
                ...
            }
        }
        
    Example:
        search_across_multiple_files(
            query="DHCP security",
            filename_filters=["ECOS_9.3.6.0", "ECOS_9.3.3.2", "ECOS_9.3.2.0"],
            limit=2
        )
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
    limit: int = 2,
    context_window: int = 5
) -> dict:
    """
    Compare how two document versions address the same topic.
    
    Specialized tool for version comparison (e.g., release notes across versions).
    Returns side-by-side results for easy comparison.
    
    Args:
        query: Search query (e.g., "security fixes", "new features")
        version1_filter: First version filename filter
        version2_filter: Second version filename filter
        limit: Maximum results per version (default: 2)
        context_window: Pages before/after match to include (0-11, default: 5)
        
    Returns:
        dict: {
            "query": str,
            "version1": {
                "filename": str,
                "results": [results]
            },
            "version2": {
                "filename": str,
                "results": [results]
            }
        }
        
    Example:
        compare_versions(
            query="security vulnerabilities",
            version1_filter="ECOS_9.3.3.2_Release_Notes",
            version2_filter="ECOS_9.3.6.0_Release_Notes",
            limit=2,
            context_window=3
        )
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
