import os
from typing import List
from PIL import Image
from .ocr import extract_text_from_image
from .image_captioning import generate_caption


def process_images(image_paths: List[str]) -> List[str]:
    """
    Process images and return extracted textual content using OCR and image captioning.
    Each image is processed by both OCR and BLIP model to maximize text coverage.
    """
    results = []
    for image_path in image_paths:
        try:
            print(f"Processing image: {image_path}")
            image = Image.open(image_path).convert("RGB")
            
            # OCR Text
            ocr_text = extract_text_from_image(image)

            # Semantic Caption
            caption = generate_caption(image)

            # Combine both results
            full_description = f"[OCR]: {ocr_text.strip()}\n[Caption]: {caption.strip()}"
            results.append(full_description)
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
    return results


def process_image_and_save(image: Image.Image, output_path: str, source_info: str) -> None:
    """
    Process a single image with OCR and captioning and save results to file.
    """
    try:
        # OCR Text
        ocr_text = extract_text_from_image(image)

        # Semantic Caption
        caption = generate_caption(image)

        # Combine results
        full_description = f"{source_info}\n[OCR]: {ocr_text.strip()}\n[Caption]: {caption.strip()}\n"
        
        # Append to file
        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(full_description + "\n" + "-"*50 + "\n")
            
    except Exception as e:
        print(f"Error processing image: {e}")
