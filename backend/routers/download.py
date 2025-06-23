from typing import List
from fastapi import APIRouter, BackgroundTasks, File, UploadFile
from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException, status, Depends
from services.logic import get_gold_db
from sqlalchemy.engine import Engine
import os
from sqlalchemy import text

router = APIRouter()

@router.get("/download")
async def download_excel(background_tasks: BackgroundTasks):
    output_path = "./output/output.xlsx"
    if os.path.exists(output_path):
        background_tasks.add_task(os.remove, output_path)
        return FileResponse(
            path=output_path,
            filename="results.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    raise HTTPException(status_code=404, detail="Output file not found.")



