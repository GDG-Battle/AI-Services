import os
import sys
# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.image_extractor import extract_images_from_docx, extract_images_from_pdf, extract_images_from_pptx
from src.services.table_extractor import extract_tables_from_docx, extract_tables_from_pdf, extract_tables_from_pptx
from src.services.text_extractor import extract_text_by_format
import warnings

# Filter the specific warning
warnings.filterwarnings('ignore', message='.*CropBox missing.*')

def process_documents(input_dir, output_dir):
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.pdf', '.docx', '.pptx')):
            file_path = os.path.join(input_dir, filename)
            base_name = os.path.splitext(filename)[0]
            doc_output_dir = os.path.join(output_dir, base_name)

            # Create output directories for images, tables, and text
            os.makedirs(os.path.join(doc_output_dir, 'images'), exist_ok=True)
            os.makedirs(os.path.join(doc_output_dir, 'tables'), exist_ok=True)
            os.makedirs(os.path.join(doc_output_dir, 'text'), exist_ok=True)

            # Extract images, tables, and text
            if filename.lower().endswith('.docx'):
                extract_images_from_docx(file_path, os.path.join(doc_output_dir, 'images'))
                extract_tables_from_docx(file_path, os.path.join(doc_output_dir, 'tables'))
                extract_text_by_format(file_path, os.path.join(doc_output_dir, 'text'))
            elif filename.lower().endswith('.pdf'):
                extract_images_from_pdf(file_path, os.path.join(doc_output_dir, 'images'))
                extract_tables_from_pdf(file_path, os.path.join(doc_output_dir, 'tables'))
                extract_text_by_format(file_path, os.path.join(doc_output_dir, 'text'))
            elif filename.lower().endswith('.pptx'):
                extract_images_from_pptx(file_path, os.path.join(doc_output_dir, 'images'))
                extract_tables_from_pptx(file_path, os.path.join(doc_output_dir, 'tables'))
                extract_text_by_format(file_path, os.path.join(doc_output_dir, 'text'))

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_directory = os.path.join(project_root, 'data', 'documents')
    output_directory = os.path.join(project_root, 'data', 'extracted_data')
    process_documents(input_directory, output_directory)