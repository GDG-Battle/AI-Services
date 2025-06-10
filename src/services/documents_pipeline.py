from src.utils.vector_store import VectorStore
import os
import hashlib
from PIL import Image
from src.utils.image_extractor import extract_images_by_format
from src.utils.table_extractor import extract_tables_by_format
from src.utils.text_extractor import extract_text_by_format
from src.utils.image_processor import process_images, process_image_and_save
import uuid

import warnings

def get_document_id(file_path: str) -> str:
    """Generate unique document ID based on file path"""
    # Generate a UUID v5 using the file path as namespace
    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # UUID namespace for URLs
    return str(uuid.uuid5(namespace, file_path))

def process_documents(input_dir: str, output_dir: str):
    vector_store = VectorStore()
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.pdf', '.docx', '.pptx')):
            file_path = os.path.join(input_dir, filename)
            base_name = os.path.splitext(filename)[0]
            doc_output_dir = os.path.join(output_dir, base_name)
            doc_id = get_document_id(file_path)
            
            # Document metadata
            doc_metadata = {
                "filename": filename,
                "file_type": os.path.splitext(filename)[1],
                "file_path": file_path
            }
            
            try:
                # Process text content
                os.makedirs(doc_output_dir, exist_ok=True)
                extract_text_by_format(file_path, doc_output_dir)
                text_path = os.path.join(doc_output_dir, "extracted_text.txt")
                if os.path.exists(text_path):
                    with open(text_path, 'r', encoding='utf-8') as f:
                        text_content = f.read()
                        vector_store.store_document_content(
                            doc_id=doc_id,
                            content=text_content,
                            content_type="text",
                            source_info=f"Document: {filename}",
                            metadata=doc_metadata
                        )
                
                # Process tables
                extract_tables_by_format(file_path, doc_output_dir)
                tables_path = os.path.join(doc_output_dir, "tables.txt")
                if os.path.exists(tables_path):
                    with open(tables_path, 'r', encoding='utf-8') as f:
                        tables_content = f.read()
                        vector_store.store_document_content(
                            doc_id=doc_id,
                            content=tables_content,
                            content_type="table",
                            source_info=f"Tables from {filename}",
                            metadata=doc_metadata
                        )
                
                # Process images
                extract_images_by_format(file_path, doc_output_dir)
                images_path = os.path.join(doc_output_dir, "image_analysis.txt")
                if os.path.exists(images_path):
                    with open(images_path, 'r', encoding='utf-8') as f:
                        images_content = f.read()
                        vector_store.store_document_content(
                            doc_id=doc_id,
                            content=images_content,
                            content_type="image",
                            source_info=f"Images from {filename}",
                            metadata=doc_metadata
                        )
                        
            except Exception as e:
                print(f"Error processing {filename}: {e}")

def process_image_files(images_dir: str, output_dir: str):
    """Process standalone image files and store in vector database"""
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    vector_store = VectorStore()
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "standalone_images_analysis.txt")
    
    for filename in os.listdir(images_dir):
        if filename.lower().endswith(image_extensions):
            img_path = os.path.join(images_dir, filename)
            try:
                with Image.open(img_path).convert("RGB") as img:
                    source_info = f"[Standalone Image: {filename}]"
                    
                    # Process image and save to file
                    process_image_and_save(img, output_file, source_info)
                    
                    # Read the processed content and store in vector database
                    with open(output_file, 'r', encoding='utf-8') as f:
                        image_content = f.read()
                        
                    # Generate unique ID for the image
                    img_id = get_document_id(img_path)
                    
                    # Prepare metadata
                    img_metadata = {
                        "filename": filename,
                        "file_type": os.path.splitext(filename)[1].lower(),
                        "file_path": img_path,
                        "type": "standalone_image"
                    }
                    
                    # Store in vector database
                    vector_store.store_document_content(
                        doc_id=img_id,
                        content=image_content,
                        content_type="image",
                        source_info=source_info,
                        metadata=img_metadata
                    )
                    print(f"✓ Stored standalone image: {filename}")
                    
            except Exception as e:
                print(f"❌ Error processing image {filename}: {e}")

