from fastapi import HTTPException
from workflows.mail_draft.models.mail_graph_schema import AgentState
from workflows.mail_draft.services.chasing_graph import create_chasing_workflow
import traceback
from pydantic import BaseModel
from tools.connection import Connect
import traceback
from datetime import datetime
import httpx  
import os
from dotenv import load_dotenv
from fastapi import APIRouter

load_dotenv()
connector = Connect()
chasing_workflow_app = create_chasing_workflow()

router = APIRouter()

CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")
TENANT_ID = os.getenv("MICROSOFT_TENANT_ID")

@router.post("/run-chasing-workflow")
async def run_chasing_workflow():
    """
    Endpoint to trigger the PO chasing workflow.
    This workflow fetches PO data, identifies items to chase,
    sends appropriate emails, and logs the actions.
    """
    try:
        initial_state = AgentState()
        final_state = await chasing_workflow_app.ainvoke(initial_state, config={"recursion_limit": 500})
        return {
            "status": "Chasing workflow completed"
        }
    except Exception as e:
        traceback.print_exc()

        raise HTTPException(status_code=500, detail=f"Error running chasing workflow: {str(e)}")
    
class TokenData(BaseModel):
    user_id: str
    access_token: str
    refresh_token: str | None = None
    expires_at: int | None = None  


@router.post("/api/store-tokens")
async def store_tokens(data: TokenData):
    """
    Endpoint to store or update Microsoft tokens for a user.
    
    - Accepts user_id, access_token, refresh_token, expires_at.
    - Performs UPSERT using SQL MERGE into User_tokens table in MS SQL.
    """
    try:
        engine = connector.zeus_automation_connection()
        conn = engine.raw_connection()

        cursor = conn.cursor()

        merge_query = """
        MERGE INTO [ZeusAutomation].[dbo].[User_tokens] AS target
        USING (SELECT ? AS user_id) AS source
        ON target.user_id = source.user_id
        WHEN MATCHED THEN
            UPDATE SET access_token = ?, 
                       refresh_token = ?, 
                       expires_at = ?, 
                       updated_at = GETDATE()
        WHEN NOT MATCHED THEN
            INSERT (user_id, access_token, refresh_token, expires_at)
            VALUES (?, ?, ?, ?);
        """

        params = (
            data.user_id,
            data.access_token,
            data.refresh_token,
            data.expires_at,
            data.user_id,
            data.access_token,
            data.refresh_token,
            data.expires_at
        )

        cursor.execute(merge_query, params)
        conn.commit()
        cursor.close()
        conn.close()

        return {"status": "Token saved successfully"}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to save token: {str(e)}")
    

@router.get("/api/mail-draft/health")
def mail_health():
    return "mail draft workflow is online"


@router.get("/api/get-valid-token")
async def get_valid_token(user_id: str):
    try:
        engine = connector.zeus_automation_connection()
        conn = engine.raw_connection()
        cursor = conn.cursor()


        cursor.execute("""
            SELECT access_token, refresh_token, expires_at
            FROM [ZeusAutomation].[dbo].[User_tokens]
            WHERE user_id = ?
        """, (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="No token found for this user.")

        access_token, refresh_token, expires_at = row
        now = int(datetime.utcnow().timestamp())

        if expires_at and now < expires_at - 60:
            print(f"[Token] Valid access token. Expires at: {expires_at}, Now: {now}")
            return { "access_token": access_token }

        if not refresh_token:
            print("[Token] Missing refresh token. User must login again.")
            raise HTTPException(status_code=401, detail="Refresh token missing. User must login again.")


        # Refresh the token using Microsoft OAuth
        async with httpx.AsyncClient() as client:
            refresh_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

            response = await client.post(
                refresh_url,
                data={
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "scope": "https://graph.microsoft.com/.default"
                },
                headers={ "Content-Type": "application/x-www-form-urlencoded" }
            )


        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Refresh failed. User must login again.")

        refreshed = response.json()
        new_access_token = refreshed["access_token"]
        new_refresh_token = refreshed["refresh_token"] if "refresh_token" in refreshed else refresh_token
        new_expires_at = now + refreshed.get("expires_in", 3600)

        engine = connector.zeus_automation_connection()
        conn = engine.raw_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE [ZeusAutomation].[dbo].[User_tokens]
            SET access_token = ?, refresh_token = ?, expires_at = ?, updated_at = GETDATE()
            WHERE user_id = ?
        """, (new_access_token, new_refresh_token, new_expires_at, user_id))
        conn.commit()
        cursor.close()
        conn.close()

        return { "access_token": new_access_token }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")
