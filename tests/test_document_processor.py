import os
import sys
import time
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.documents_pipeline import process_documents, process_image_files

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def format_time(seconds):
    """Convert seconds to human readable format"""
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)}h {int(minutes)}m {seconds:.2f}s"

if __name__ == "__main__":
    try:
        input_directory = os.path.join(project_root, 'data', 'documents')
        output_directory = os.path.join(project_root, 'data', 'extracted_data')
        image_directory = os.path.join(project_root, 'data', 'images')

        # Start timing for documents
        start_time = time.time()
        print(f"Started processing documents at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("Processing documents...")
        process_documents(input_directory, output_directory)
        
        # Document processing time
        doc_time = time.time() - start_time
        print(f"Document processing took: {format_time(doc_time)}")
        
        # Start timing for images
        img_start_time = time.time()
        print(f"\nStarted processing images at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("Processing standalone images...")
        process_image_files(image_directory, output_directory)
        
        # Image processing time
        img_time = time.time() - img_start_time
        print(f"Image processing took: {format_time(img_time)}")
        
        # Total processing time
        total_time = time.time() - start_time
        print(f"\nTotal processing completed in: {format_time(total_time)}")
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
