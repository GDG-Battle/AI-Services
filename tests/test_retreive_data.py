import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.vector_store import VectorStore

def test_similarity_search():
    vector_store = VectorStore()
    
    test_queries = [
        "What is machine learning?",
        "How does dependency injection work?",
        "Explain REST API concepts"
    ]
    
    for query in test_queries:
        results = vector_store.similarity_search(
            query=query,
            k=3
        )
        
        print(f"\nResults for query: {query}")
        print("=" * 50)
        
        if not results:
            print("No results found")
            continue
            
        for i, doc in enumerate(results, 1):
            print(f"\nResult {i}:")
            content = doc.get('page_content', '')
            if content:
                print(f"Content: {content[:200]}...")
            else:
                print("No content available")
                
            print(f"Source: {doc['metadata'].get('source_info', 'No source')}")
            print(f"Score: {doc['metadata'].get('score', 0):.4f}")

if __name__ == "__main__":
    test_similarity_search()