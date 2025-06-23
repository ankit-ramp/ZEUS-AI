import pdfplumber
from pdf2image import convert_from_path
import pytesseract


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
            images = convert_from_path(path)
            return "\n".join(pytesseract.image_to_string(img) for img in images)