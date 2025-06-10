from .vector_store import VectorStore
from typing import List, Dict, Optional

def search_documents(
    query: str, 
    content_types: Optional[List[str]] = None,
    limit: int = 5
) -> List[Dict]:
    """
    Search for similar content across all stored document data
    
    Args:
        query: Search query text
        content_types: Optional list of content types to search ('text', 'table', 'ocr', 'caption')
        limit: Maximum number of results to return
    """
    vector_store = VectorStore()
    
    # Prepare search filters
    search_filter = None
    if content_types:
        search_filter = {
            "must": [
                {
                    "key": "content_type",
                    "match": {
                        "any": content_types
                    }
                }
            ]
        }
    
    # Search in Qdrant
    results = vector_store.search(
        query=query,
        filter=search_filter,
        limit=limit
    )
    
    # Format results
    formatted_results = []
    for result in results:
        formatted_results.append({
            'score': result.score,
            'content_type': result.payload['content_type'],
            'source': result.payload['source_info'],
            'content': result.payload['content'],
            'metadata': {k: v for k, v in result.payload.items() 
                        if k not in ['content_type', 'source_info', 'content']}
        })
    
    return formatted_results