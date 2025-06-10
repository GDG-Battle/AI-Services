import os
from werkzeug.utils import secure_filename
from io import BytesIO

from src.utils.image_processor import process_image_and_save
from src.utils.text_extractor import extract_text_by_format

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_files(files, upload_folder):
    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            saved_files.append(filepath)
    return saved_files

def process_file_content(file_content, file_type):
    """Process file content directly from memory"""
    content = BytesIO(file_content)
    if file_type in ['pdf', 'docx', 'pptx']:
        return extract_text_by_format(content, file_type, in_memory=True)
    elif file_type in ['png', 'jpg', 'jpeg']:
        return process_image_and_save(content, in_memory=True)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")