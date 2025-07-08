import sys
import os

from fastapi.responses import FileResponse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from typing import List
import sys
sys.setrecursionlimit(8000)
from fastapi import APIRouter, File, UploadFile, BackgroundTasks

from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.engine import Engine
import os
from sqlalchemy import text
from process_invoice.services.invoice_logic import load_files
from process_invoice.services.invoice_graph_instance import graph
from dotenv import load_dotenv
from workflows.process_invoice.services.logger import logger
load_dotenv()

router = APIRouter()

INPUT_DIR = os.getenv("INVOICES_INPUT_FOLDER", "backend/workflows/process_invoice/invoice_input")


def clear_input_dir():
    if os.path.exists(INPUT_DIR):
        for f in os.listdir(INPUT_DIR):
            path = os.path.join(INPUT_DIR, f)
            if os.path.isfile(path):
                try:
                    os.remove(path)
                except Exception as e:
                    logger.error(f"Failed to delete file {path}: {e}")
    else:
        os.makedirs(INPUT_DIR, exist_ok=True)

@router.post("/invoice")
async def process_invoice(files: List[UploadFile] = File(...)):
    # Step 1: Clear input directory
    clear_input_dir()

    saved_paths = []

    try:
        # Step 2: Save files
        for file in files:
            file_path = os.path.join(INPUT_DIR, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())
            saved_paths.append(file_path)

        # Step 3: Run the graph
        result = graph.invoke({"file_list": ''}, {"recursion_limit": 8000})

        return result

    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Step 4: Clean up input directory after processing
        clear_input_dir()
    


