import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.documents_pipeline import process_documents, process_image_files

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        input_directory = os.path.join(project_root, 'data', 'documents')
        output_directory = os.path.join(project_root, 'data', 'extracted_data')
        image_directory = os.path.join(project_root, 'data', 'images')

        print("Processing documents...")
        process_documents(input_directory, output_directory)
        
        print("\nProcessing standalone images...")
        process_image_files(image_directory, output_directory)
        
        print("Processing completed successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
