# main.py
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
import re
import pandas as pd
import sys
from typing import Generator
from typing import List
from sqlalchemy import text
from services.po_graph_instance import graph
from fastapi import File, UploadFile
from fastapi.responses import FileResponse
import shutil
import os
from fastapi.middleware.cors import CORSMiddleware
sys.setrecursionlimit(200)
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import BackgroundTasks
from sqlalchemy.engine import Engine
from services.logic import get_gold_db
from tools.connection import Connect


load_dotenv()
order_cache = []

def get_order_cache():
    return order_cache

from routers import download, health, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = Connect()
    engine = db.gold_connection()

    if not isinstance(engine, dict):
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT Customer_Reference, Delivery_Reference, Address FROM Sales.tblDelivery"))
                order_cache.clear()
                order_cache.extend([
                    {
                        **dict(row._mapping),
                        "Address": re.sub(r'[^A-Za-z0-9]', '', row._mapping["Address"]).upper() if row._mapping["Address"] else row._mapping["Address"]
                    }
                    for row in result
                ])
                print("✅ Order cache loaded on startup")
            
        except Exception as e:
            print("❌ Error loading order cache:", e)
    else:
        print("❌ DB connection failed during startup cache load")

    yield  


app = FastAPI(lifespan=lifespan)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GraphInput(BaseModel):
    company: str


app.include_router(download.router)
app.include_router(upload.router)
app.include_router(health.router)

