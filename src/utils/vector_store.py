from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_qdrant import QdrantVectorStore  # Add this import
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
import uuid
import os
import dotenv
from datetime import datetime

# Load environment variables
dotenv.load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
EMBEDDING_MODEL_NAME = "nv-embed-v1"  # Update to match working example

def generate_chunk_id(base_id: str, chunk_index: int) -> str:
    """Generate a deterministic UUID for a document chunk based on base ID and chunk index"""
    # Create a namespace UUID from the base document ID
    namespace = uuid.UUID(base_id)
    # Generate a new UUID using the chunk index as name
    return str(uuid.uuid5(namespace, str(chunk_index)))

class VectorStore:
    def __init__(self, collection_name="document_store"):
        self.collection_name = collection_name
        
        try:
            # Initialize NVIDIA embeddings
            self.encoder = NVIDIAEmbeddings(
                model_name=EMBEDDING_MODEL_NAME,
                nvidia_api_key=os.getenv("NVIDIA_API_KEY")
            )
            
            # Initialize QdrantVectorStore instead of direct client
            self.vectorstore = QdrantVectorStore.from_existing_collection(
                collection_name=collection_name,
                embedding=self.encoder,
                url=QDRANT_URL,
                prefer_grpc=True
            )
            
        except Exception as e:
            # Try creating new collection if it doesn't exist
            self.vectorstore = QdrantVectorStore.from_documents(
                documents=[],  # Start with empty collection
                embedding=self.encoder,
                collection_name=collection_name,
                url=QDRANT_URL,
                prefer_grpc=True
            )
            
    def store_document_content(self, doc_id: str, content: str, content_type: str, 
                             source_info: str, metadata: dict):
        """Store document content in vector store with chunking"""
        chunks = self._split_content(content)
        
        for i, chunk in enumerate(chunks):
            try:
                # Use add_texts instead of direct client operations
                self.vectorstore.add_texts(
                    texts=[chunk],
                    metadatas=[{
                        "doc_id": doc_id,
                        "chunk_id": generate_chunk_id(doc_id, i),
                        "content_type": content_type,
                        "source": source_info,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        **metadata
                    }]
                )
            except Exception as e:
                print(f"❌ Error storing chunk {i+1}: {str(e)}")

    def similarity_search(self, query: str, k: int = 3):
        """Search for similar documents in the vector store"""
        try:
            # Use QdrantVectorStore's similarity_search
            results = self.vectorstore.similarity_search(
                query,
                k=k,
                include_metadata=True
            )
            return results
        except Exception as e:
            print(f"❌ Error during similarity search: {str(e)}")
            return []

    def chunk_text(self, text: str, max_chunk_size: int = 1000) -> list:
        """Split text into semantically meaningful chunks"""
        
        # Split into sections based on headers or semantic markers
        sections = self._split_into_sections(text)
        chunks = []
        
        for section in sections:
            # Split section into sentences
            sentences = section.split('.')
            current_chunk = []
            current_size = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                # Add sentence terminator back
                sentence = sentence + '.'
                
                # Start new chunk if:
                # 1. Current chunk would exceed max size
                # 2. Current sentence contains a header marker
                # 3. Natural break point is detected
                if (current_size + len(sentence) > max_chunk_size or
                    self._is_header(sentence) or
                    self._is_natural_break(current_chunk, sentence)):
                    
                    if current_chunk:
                        chunks.append(' '.join(current_chunk))
                    current_chunk = [sentence]
                    current_size = len(sentence)
                else:
                    current_chunk.append(sentence)
                    current_size += len(sentence) + 1
                    
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                
        return chunks

    def _split_into_sections(self, text: str) -> list:
        """Split text into logical sections based on markers"""
        # Common section markers from your documents
        markers = [
            '[PPTX Slide',
            '[PDF Page',
            '[DOCX',
            '# ',
            '## ',
            '\n\n'
        ]
        sections = []
        current_section = []
        
        for line in text.split('\n'):
            if any(marker in line for marker in markers):
                if current_section:
                    sections.append('\n'.join(current_section))
                    current_section = []
            current_section.append(line)
            
        if current_section:
            sections.append('\n'.join(current_section))
        
        return sections

    def _is_header(self, text: str) -> bool:
        """Check if text is a header"""
        header_patterns = [
            '[PPTX Slide',
            '[PDF Page',
            '[DOCX',
            '# ',
            '## ',
            'Chapter',
            'Section'
        ]
        return any(pattern in text for pattern in header_patterns)

    def _is_natural_break(self, current_chunk: list, next_sentence: str) -> bool:
        """Determine if there should be a natural break between chunks"""
        if not current_chunk:
            return False
            
        # Break on topic changes or logical transitions
        transition_words = [
            'However,',
            'Moreover,',
            'Furthermore,',
            'In conclusion,',
            'Therefore,',
            'Finally,'
        ]
        
        return any(word in next_sentence for word in transition_words)

    def _split_content(self, content: str) -> list:
        """Split content into chunks using the existing chunk_text method"""
        return self.chunk_text(content)

    def _get_embedding(self, text: str) -> list:
        """Get embedding vector for text using NVIDIA embeddings"""
        embeddings = self.encoder.embed_query(text)
        return embeddings