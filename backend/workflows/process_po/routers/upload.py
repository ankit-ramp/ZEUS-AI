from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from main import get_order_cache
from services.logic import get_gold_db
from sqlalchemy.engine import Engine
from sqlalchemy import text
from services.po_graph_instance import graph
import os
import shutil

router = APIRouter()
INPUT_DIR = os.getenv("PO_INPUT_FOLDER", "workflows/process_po/po_input")
OUTPUT_DIR = os.getenv("PO_OUTPUT_FOLDER", "workflows/process_po/po_output")

@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...), order_cache=Depends(get_order_cache)):
    input_folder = INPUT_DIR
    os.makedirs(input_folder, exist_ok=True)

    # ✅ Clear the input folder before uploading
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to clear input folder: {str(e)}")

    saved_file_paths = []

    # Save new uploaded files
    for file in files:
        file_path = os.path.join(input_folder, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        saved_file_paths.append(file_path)

    try:
        company = "company"
        initial_state = {"company": company, "order_cache": order_cache}
        result = graph.invoke(initial_state, {"recursion_limit": 5000})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Optional: Log processing
    for path in saved_file_paths:
        print(f"Processing: {path}")

    # Clean up after processing
    for path in saved_file_paths:
        os.remove(path)

    return {"message": f"{len(saved_file_paths)} files processed and input folder cleared."}
