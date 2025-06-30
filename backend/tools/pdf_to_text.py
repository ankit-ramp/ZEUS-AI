import pdfplumber
import os
from pdf2image import convert_from_path
import pytesseract
from dotenv import load_dotenv
load_dotenv()
tesseract_path = os.getenv("TESSERACT_DEV_PATH")

if not tesseract_path:
    raise RuntimeError("TESSERACT_CMD not set in .env")

pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Poppler path from .env
poppler_path = os.getenv("POPPLER_DEV_PATH")
if not poppler_path:
    raise RuntimeError("POPPLER_DEV_PATH not set in .env")

def extract_text_from_pdf(path):
        try:
            with pdfplumber.open(path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if not text.strip():
                raise Exception("Empty after pdfplumber, trying OCR.")
            return text
        except:
            # fallback to OCR
            images = convert_from_path(path, poppler_path=poppler_path)
            return "\n".join(pytesseract.image_to_string(img) for img in images)