# File: test_image_processor.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.image_processor import process_images

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
    # Use os.path.join to create platform-independent path
    # Create path relative to the project root
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    image_dir = os.path.join(project_root, "data", "images")
    image_paths = collect_image_paths(image_dir)

    print(f"Found {len(image_paths)} images.")
    results = process_images(image_paths)

    for idx, result in enumerate(results):
        print(f"\n--- Result for Image {idx+1} ---")
        print(result)
