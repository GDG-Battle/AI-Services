from src.utils.vector_store import VectorStore
import os
import hashlib
from PIL import Image
from src.utils.image_extractor import extract_images_by_format
from src.utils.table_extractor import extract_tables_by_format
from src.utils.text_extractor import extract_text_by_format
from src.utils.image_processor import process_images, process_image_and_save
import uuid
from datetime import datetime
import logging
import time

import warnings

DOCUMENT_EXTENSIONS = ('.pdf', '.docx', '.pptx')
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_document(filename: str) -> bool:
    """Check if file is a supported document type"""
    return filename.lower().endswith(DOCUMENT_EXTENSIONS)

def is_valid_image(filename: str) -> bool:
    """Check if file is a supported image type"""
    return filename.lower().endswith(IMAGE_EXTENSIONS)

def create_metadata(file_path: str, file_type: str = None) -> dict:
    """Create standard metadata for a file"""
    filename = os.path.basename(file_path)
    return {
        "filename": filename,
        "file_type": os.path.splitext(filename)[1],
        "file_path": file_path,
        "type": file_type,
        "added_date": datetime.now().isoformat()
    }

def get_document_id(file_path: str) -> str:
    """Generate unique document ID based on file path"""
    # Generate a UUID v5 using the file path as namespace
    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # UUID namespace for URLs
    return str(uuid.uuid5(namespace, file_path))

def process_documents(input_dir: str, output_dir: str) -> dict:
    """Process all documents in a directory"""
    vector_store = VectorStore()
    results = {"success": [], "failed": []}
    
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        try:
            if is_valid_document(filename):
                doc_metadata = create_metadata(file_path, "document")
                process_single_document(
                    file_path=file_path,
                    doc_output_dir=os.path.join(output_dir, os.path.splitext(filename)[0]),
                    doc_id=get_document_id(file_path),
                    doc_metadata=doc_metadata,
                    vector_store=vector_store
                )
                results["success"].append(filename)
            elif is_valid_image(filename):
                process_single_image(file_path, output_dir, vector_store)
                results["success"].append(filename)
                
        except Exception as e:
            results["failed"].append({"file": filename, "error": str(e)})
            logger.error(f"Error processing {filename}: {e}")
    
    return results

def process_single_image(file_path: str, output_dir: str, vector_store: VectorStore) -> None:
    """Process a single image file and store its analysis"""
    img_metadata = create_metadata(file_path, "standalone_image")
    output_file = os.path.join(output_dir, "standalone_images_analysis.txt")
    
    with Image.open(file_path).convert("RGB") as img:
        source_info = f"[Standalone Image: {img_metadata['filename']}]"
        process_image_and_save(img, output_file, source_info)
        
        with open(output_file, 'r', encoding='utf-8') as f:
            image_content = f.read()
            
        vector_store.store_document_content(
            doc_id=get_document_id(file_path),
            content=image_content,
            content_type="image",
            source_info=source_info,
            metadata=img_metadata
        )

def process_image_files(images_dir: str, output_dir: str) -> dict:
    """Process all images in a directory"""
    vector_store = VectorStore()
    os.makedirs(output_dir, exist_ok=True)
    
    results = {"success": [], "failed": []}
    
    for filename in os.listdir(images_dir):
        if is_valid_image(filename):
            try:
                img_path = os.path.join(images_dir, filename)
                process_single_image(img_path, output_dir, vector_store)
                results["success"].append(filename)
                logger.info(f"✓ Stored standalone image: {filename}")
            except Exception as e:
                results["failed"].append({"file": filename, "error": str(e)})
                logger.error(f"❌ Error processing image {filename}: {e}")
    
    return results

def store_document_content(vector_store, doc_id, content_path, content_type, doc_metadata):
    """Helper function to read and store document content"""
    if os.path.exists(content_path):
        with open(content_path, 'r', encoding='utf-8') as f:
            content = f.read()
            vector_store.store_document_content(
                doc_id=doc_id,
                content=content,
                content_type=content_type,
                source_info=f"{content_type.capitalize()} from {doc_metadata['filename']}",
                metadata=doc_metadata
            )

def process_single_document(file_path, doc_output_dir, doc_id, doc_metadata, vector_store):
    """Extract text, tables, and images from a document and store them in the vector store."""
    os.makedirs(doc_output_dir, exist_ok=True)
    
    # Process text content
    extract_text_by_format(file_path, doc_output_dir)
    store_document_content(
        vector_store,
        doc_id,
        os.path.join(doc_output_dir, "extracted_text.txt"),
        "text",
        doc_metadata
    )

    # Process tables
    extract_tables_by_format(file_path, doc_output_dir)
    store_document_content(
        vector_store,
        doc_id,
        os.path.join(doc_output_dir, "tables.txt"),
        "table",
        doc_metadata
    )

    # Process images
    extract_images_by_format(file_path, doc_output_dir)
    store_document_content(
        vector_store,
        doc_id,
        os.path.join(doc_output_dir, "image_analysis.txt"),
        "image",
        doc_metadata
    )

def add_new_documents(input_files: list, output_dir: str) -> dict:
    """Process a list of new documents"""
    vector_store = VectorStore()
    results = {
        "success": [], 
        "failed": [],
        "timing": []  # Add timing information
    }
    
    for file_path in input_files:
        filename = os.path.basename(file_path)
        start_time = time.time()
        
        try:
            if is_valid_document(filename):
                doc_metadata = create_metadata(file_path, "document")
                process_single_document(
                    file_path=file_path,
                    doc_output_dir=os.path.join(output_dir, os.path.splitext(filename)[0]),
                    doc_id=get_document_id(file_path),
                    doc_metadata=doc_metadata,
                    vector_store=vector_store
                )
                results["success"].append(filename)
            elif is_valid_image(filename):
                process_single_image(file_path, output_dir, vector_store)
                results["success"].append(filename)
            
            # Record processing time
            processing_time = time.time() - start_time
            results["timing"].append({
                "file": filename,
                "processing_time_seconds": round(processing_time, 2)
            })
                
        except Exception as e:
            processing_time = time.time() - start_time
            results["failed"].append({
                "file": filename, 
                "error": str(e),
                "processing_time_seconds": round(processing_time, 2)
            })
            logger.error(f"Error processing {filename} ({processing_time:.2f}s): {e}")
    
    return results

