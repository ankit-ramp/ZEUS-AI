from typing import List
from fastapi import APIRouter, File, UploadFile
from main import get_order_cache
from fastapi import FastAPI, HTTPException, status, Depends
from services.logic import get_gold_db
from sqlalchemy.engine import Engine
import os
from sqlalchemy import text
from services.po_graph_instance import graph

router = APIRouter()

@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...), order_cache=Depends(get_order_cache)):
    saved_file_paths = []

    # Save files to input/ folder
    for file in files:
        file_path = os.path.join("./input", file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        saved_file_paths.append(file_path)

    try:
        # print(graph.get_graph().draw_ascii())
        company = "company"
        initial_state = {"company": company, "order_cache": order_cache}
        result = graph.invoke(initial_state, {"recursion_limit": 100})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Simulate processing (print filenames)
    for path in saved_file_paths:
        print(f"Processing: {path}")
        # Add your actual logic here

    # Clean up the input folder
    for path in saved_file_paths:
        os.remove(path)

    return {"message": f"{len(saved_file_paths)} files processed and input folder cleared."}



