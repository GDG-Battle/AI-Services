import os
from PIL import Image
from src.utils.image_extractor import extract_images_by_format
from src.utils.table_extractor import extract_tables_by_format
from src.utils.text_extractor import extract_text_by_format
from src.utils.image_processor import process_images, process_image_and_save

import warnings

def process_documents(input_dir, output_dir):
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.pdf', '.docx', '.pptx')):
            file_path = os.path.join(input_dir, filename)
            base_name = os.path.splitext(filename)[0]
            doc_output_dir = os.path.join(output_dir, base_name)

            # Create output directory for document
            os.makedirs(doc_output_dir, exist_ok=True)

            # Extract all content using format-specific extractors
            extract_images_by_format(file_path, doc_output_dir)
            extract_tables_by_format(file_path, doc_output_dir)
            extract_text_by_format(file_path, doc_output_dir)

def process_image_files(images_dir, output_dir):
    """Process standalone image files and extract their content"""
    image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "standalone_images_analysis.txt")
    
    for filename in os.listdir(images_dir):
        if filename.lower().endswith(image_extensions):
            img_path = os.path.join(images_dir, filename)
            try:
                with Image.open(img_path).convert("RGB") as img:
                    source_info = f"[Standalone Image: {filename}]"
                    process_image_and_save(img, output_file, source_info)
            except Exception as e:
                print(f"Error processing image {filename}: {e}")

