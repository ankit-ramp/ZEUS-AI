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

router = APIRouter()

@router.post("/invoice")
async def upload_files(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    input_dir = "../invoice_input"
    os.makedirs(input_dir, exist_ok=True)

    # 🔥 Step 1: Clean up leftover files from previous runs
    for leftover in os.listdir(input_dir):
        leftover_path = os.path.join(input_dir, leftover)
        if os.path.isfile(leftover_path):
            try:
                os.remove(leftover_path)
            except Exception as cleanup_error:
                print(f"Warning: Failed to remove leftover file {leftover_path}: {cleanup_error}")

    # 🔄 Step 2: Save uploaded files
    saved_file_paths = []
    for file in files:
        file_path = os.path.join(input_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        saved_file_paths.append(file_path)

    # ⚙️ Step 3: Process with graph
    try:
        initial_state = {"file_list": ''}
        print(graph.get_graph().draw_ascii())
        result = graph.invoke(initial_state, {"recursion_limit": 3000})

        output_dir = os.path.join(os.path.dirname(__file__), "../invoice_output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "output.csv")
        print("Checking if file exists:", output_path)
        print("Directory listing:", os.listdir(os.path.dirname(output_path)))

        if os.path.exists(output_path):
            # Schedule cleanup of output and input files
            background_tasks.add_task(os.remove, output_path)
            for path in saved_file_paths:
                background_tasks.add_task(os.remove, path)

            return FileResponse(
                path=output_path,
                filename="results.csv",
                media_type="text/csv"
            )
        else:
            for path in saved_file_paths:
                background_tasks.add_task(os.remove, path)
            raise HTTPException(status_code=404, detail="Output file not found.")
        
    except Exception as e:
        for path in saved_file_paths:
            background_tasks.add_task(os.remove, path)
        raise HTTPException(status_code=500, detail=str(e))