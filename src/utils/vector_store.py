from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import uuid

def generate_chunk_id(base_id: str, chunk_index: int) -> str:
    """Generate a deterministic UUID for a document chunk based on base ID and chunk index"""
    # Create a namespace UUID from the base document ID
    namespace = uuid.UUID(base_id)
    # Generate a new UUID using the chunk index as name
    return str(uuid.uuid5(namespace, str(chunk_index)))

class VectorStore:
    def __init__(self, collection_name="document_store"):
        self.collection_name = collection_name
        # Initialize Qdrant client (local instance)
        self.client = QdrantClient("localhost", port=6333)
        # Initialize sentence transformer model
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384,  # vector size for all-MiniLM-L6-v2
                    distance=models.Distance.COSINE
                )
            )

    def store_document_data(self, content_type: str, source_info: str, content: str, metadata: dict = None):
        """Store document data in vector database"""
        # Generate embedding for the content
        vector = self.encoder.encode(content).tolist()
        
        # Prepare payload
        payload = {
            "content_type": content_type,
            "source_info": source_info,
            "content": content,
            **(metadata or {})
        }

        # Store in Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload=payload
                )
            ]
        )

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
        """Get embedding vector for text using sentence transformer"""
        return self.encoder.encode(text).tolist()

    def store_document_content(self, doc_id: str, content: str, content_type: str, 
                             source_info: str, metadata: dict):
        """Store document content in vector store with chunking"""
        chunks = self._split_content(content)
        
        for i, chunk in enumerate(chunks):
            chunk_id = generate_chunk_id(doc_id, i)
            try:
                # Store chunk with valid UUID
                self.client.upsert(  # Changed from self.qdrant to self.client
                    collection_name=self.collection_name,
                    points=[
                        models.PointStruct(  # Added models. prefix
                            id=chunk_id,
                            vector=self._get_embedding(chunk),
                            payload={
                                "text": chunk,
                                "content_type": content_type,
                                "source": source_info,
                                "chunk_index": i,
                                "total_chunks": len(chunks),
                                **metadata
                            }
                        )
                    ]
                )
            except Exception as e:
                print(f"❌ Error storing chunk {i+1}: {str(e)}")