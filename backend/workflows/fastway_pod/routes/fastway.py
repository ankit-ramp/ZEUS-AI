from fastapi import APIRouter
from main import get_order_cache
from fastapi import FastAPI, HTTPException, status, Depends
from services.logic import get_gold_db
from sqlalchemy.engine import Engine
from sqlalchemy import text

router = APIRouter()


@router.get("/")
def healthCheck():
    return "api is online"



@router.get("/fastway")
def process_fastway_pod():
    print("processing fastway POD files")
    return "Processed all files"
