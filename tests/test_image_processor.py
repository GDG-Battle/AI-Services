# File: test_image_processor.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.image_processor import process_images,process_image_and_save
from PIL import Image

def collect_image_paths(directory: str, extensions={".jpg", ".jpeg", ".png", ".bmp"}):
    """
    Collect image file paths from a directory with supported extensions.
    """
    image_paths = []
    for fname in os.listdir(directory):
        if os.path.splitext(fname)[1].lower() in extensions:
            image_paths.append(os.path.join(directory, fname))
    return image_paths

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, "data", "extracted_data")
    output_file = os.path.join(output_dir, "image_analysis.txt")
    image_dir = os.path.join(project_root, "data", "images")
    image_paths = collect_image_paths(image_dir)

    print(f"Found {len(image_paths)} images.")
    
    os.makedirs(output_dir, exist_ok=True)
    
    for idx, img_path in enumerate(image_paths):
        try:
            with Image.open(img_path).convert("RGB") as img:
                source_info = f"[Standalone Image: {os.path.basename(img_path)}]"
                process_image_and_save(img, output_file, source_info)
        except Exception as e:
            print(f"Error processing image {img_path}: {e}")
