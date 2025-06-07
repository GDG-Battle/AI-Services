import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.retriever.search_service import SearchService

if __name__ == "__main__":
    search_service = SearchService()
    while True:
        query = input("Enter a search query (or type 'exit'): ")
        if query.lower() == 'exit':
            break
        results = search_service.search(query)
        print("\nTop results:")
        for i, res in enumerate(results, 1):
            print(f"{i}. {res}\n")
