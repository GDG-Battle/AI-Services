from PIL import Image
import pytesseract

# # Add this to the top of ocr.py if Tesseract isn't in PATH
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image: Image.Image) -> str:
    """
    Extract text from an image using OCR.
    
    Args:
        image (Image.Image): PIL Image object to process
        
    Returns:
        str: Extracted text from the image
    """
    try:
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"Error during OCR processing: {e}")
        return ""

