import os
from typing import List
from PIL import Image
import pytesseract
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

from src.utils.ocr import extract_text_from_image
from src.utils.image_captioning import generate_caption


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
