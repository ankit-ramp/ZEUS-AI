import os
import cv2
import re
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
from dotenv import load_dotenv
import pytesseract
import ocrmypdf
from io import BytesIO

# Load environment
load_dotenv()
TESSERACT_PATH = os.getenv("TESSERACT_DEV_PATH")
POPPLER_PATH = os.getenv("POPPLER_DEV_PATH")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def extract_pods_from_pdf(input_pdf_path: str, output_dir: str = "PODs_Visual") -> dict:
    
    os.makedirs(output_dir, exist_ok=True)

    images = convert_from_path(input_pdf_path, dpi=300, poppler_path=POPPLER_PATH)
    pod_count, skipped_count = 0, 0
    seen_refs = set()

    for page_num, pil_image in enumerate(images):
        print(f"📄 Page {page_num + 1}")
        img = np.array(pil_image)
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if h < 150 or w < 300 or h > img.shape[0] * 0.95:
                continue

            pod_region = img[y:y+h, x:x+w]
            pod_pil = Image.fromarray(pod_region)

            # Extract Order Reference
            text = pytesseract.image_to_string(pod_pil)
            match = re.search(r"Order Reference[:\s]*([A-Z0-9]+)", text, re.IGNORECASE)
            label = match.group(1) if match else f"page{page_num+1}_pod{pod_count}"
            final_pdf = os.path.join(output_dir, f"POD_{label}.pdf")

            if label in seen_refs:
                print(f"⏭️ Skipping duplicate Order Ref: {label}")
                skipped_count += 1
                continue

            seen_refs.add(label)

            # Convert and OCR
            buffer = BytesIO()
            pod_pil.convert("RGB").save(buffer, format="PDF")
            buffer.seek(0)

            try:
                ocrmypdf.ocr(
                    input_file=buffer,
                    output_file=final_pdf,
                    deskew=True,
                    skip_text=True,
                    progress_bar=False
                )
                print(f"✅ Saved: {final_pdf}")
            except Exception as e:
                print(f"⚠️ OCR failed for {label}, saving as image-only: {e}")
                pod_pil.convert("RGB").save(final_pdf)

            pod_count += 1

    summary = {
        "pages_processed": len(images),
        "pods_saved": pod_count,
        "duplicates_skipped": skipped_count,
        "output_dir": output_dir
    }

    print(f"\n🎉 Done! {summary}")
    return summary
