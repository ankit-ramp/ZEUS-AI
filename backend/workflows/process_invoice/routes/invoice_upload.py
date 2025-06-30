import sys
import os

from fastapi.responses import FileResponse
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from typing import List
import sys
sys.setrecursionlimit(3000)
from fastapi import APIRouter, File, UploadFile, BackgroundTasks

from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.engine import Engine
import os
from sqlalchemy import text
from process_invoice.services.invoice_logic import load_files
from process_invoice.services.invoice_graph_instance import graph
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

INPUT_DIR = os.getenv("INVOICES_INPUT_FOLDER", "backend/workflows/process_invoice/invoice_input")
OUTPUT_DIR = os.getenv("INVOICES_OUTPUT_FOLDER", "backend/workflows/process_invoice/invoice_output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "output.csv")

def schedule_cleanup(background_tasks: BackgroundTasks, input_files: List[str], output_file: str):
    for path in input_files:
        background_tasks.add_task(os.remove, path)
    background_tasks.add_task(os.remove, output_file)

@router.post("/invoice")
async def upload_files(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --- Start of the enhanced cleanup ---
    # Clean up old input and output files before processing new ones
    for leftover in os.listdir(INPUT_DIR):
        leftover_path = os.path.join(INPUT_DIR, leftover)
        if os.path.isfile(leftover_path):
            try:
                os.remove(leftover_path)
            except Exception as cleanup_error:
                print(f"Warning: Failed to remove leftover input file {leftover_path}: {cleanup_error}")
    
    if os.path.exists(OUTPUT_FILE):
        try:
            os.remove(OUTPUT_FILE)
            print(f"Removed old output file: {OUTPUT_FILE}")
        except Exception as cleanup_error:
            print(f"Warning: Failed to remove old output file {OUTPUT_FILE}: {cleanup_error}")
    # --- End of the enhanced cleanup ---
    
    saved_file_paths = []
    for file in files:
        file_path = os.path.join(INPUT_DIR, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        saved_file_paths.append(file_path)

    try:
        print(graph.get_graph().draw_ascii())
        result = graph.invoke({"file_list": ''}, {"recursion_limit": 3000})

        if os.path.exists(OUTPUT_FILE):
            # Schedule cleanup only after successful processing
            schedule_cleanup(background_tasks, saved_file_paths, OUTPUT_FILE)

            return FileResponse(
                path=OUTPUT_FILE,
                filename="results.csv",
                media_type="text/csv"
            )
        else:
            # Clean only inputs, output is not created
            for path in saved_file_paths:
                background_tasks.add_task(os.remove, path)
            raise HTTPException(status_code=404, detail="Output file not found.")

    except Exception as e:
        for path in saved_file_paths:
            background_tasks.add_task(os.remove, path)
        raise HTTPException(status_code=500, detail=str(e))