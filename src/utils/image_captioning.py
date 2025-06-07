# File: app/utils/image_captioning.py
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def generate_caption(image: Image.Image) -> str:
    """
    Generate a semantic caption for an image using BLIP model.
    """
    try:
        inputs = blip_processor(image, return_tensors="pt")
        with torch.no_grad():
            output = blip_model.generate(**inputs)
        caption = blip_processor.decode(output[0], skip_special_tokens=True)
        return caption
    except Exception as e:
        print(f"Image captioning error: {e}")
        return ""
