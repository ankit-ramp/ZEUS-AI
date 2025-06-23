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



@router.get("/cache")
def get_cache(order_cache = Depends(get_order_cache)):
    return {"order_cache": order_cache}

@router.get("/gold")
def health_check(db: Engine = Depends(get_gold_db)):
    try:
        with db.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "db": "gold connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB connection failed: {str(e)}")

