import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import requests
import msal
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
import requests

load_dotenv()


def generate_chasing_email(po_details: List[Dict], future_po_details: Optional[List[Dict]] = None) -> str:
    if not po_details:
        return ""

    all_pos = po_details + (future_po_details or [])

    def extract_date(po):
        return po.get("ShipDate") or po.get("RequiredDate") or datetime.max

    grouped = defaultdict(list)
    for po in all_pos:
        grouped[po["PONumber"]].append(po)

    for group in grouped.values():
        group.sort(key=extract_date)

    sorted_groups = sorted(grouped.values(), key=lambda group: extract_date(group[0]))
    all_pos = [po for group in sorted_groups for po in group]
    supplier_name = all_pos[0].get("SupplierName", "Supplier")

    body = f"""
    <html>
    <body>
        <p style="margin-bottom: 14px;">Hi,</p>
        <p style="margin-bottom: 14px;">Hope you are doing well.</p>
        <p style="margin-bottom: 14px;"><b>Can you please confirm if the below order(s) will be ready for loading and dispatch as scheduled below?</b></p>
        <p style="margin-bottom: 14px;"><b>Kindly fill in the <u>Supplier Remarks</u> column in the table below when replying.</b></p>

        <table border="1" cellspacing="0" cellpadding="6" style="border-collapse: collapse; width: 100%; border: 1px solid black;">
            <thead>
                <tr>
                    <th colspan="6" style="text-align: left; border: 1px solid black;">Supplier: {supplier_name}</th>
                </tr>
                <tr>
                    <th style="border: 1px solid black; text-align: center;">Purchase Order</th>
                    <th style="border: 1px solid black; text-align: center;">Stock Code</th>
                    <th style="border: 1px solid black; text-align: center;">Stock Description</th>
                    <th style="border: 1px solid black; text-align: center;">Quantity Ordered</th>
                    <th style="border: 1px solid black; text-align: center;">Ship By Date</th>
                    <th style="border: 1px solid black; text-align: center;">Supplier Remarks</th>
                </tr>
            </thead>
            <tbody>
    """

    for po in all_pos:
        po_number = po.get("PONumber", "")
        stock_code = po.get("StockCode", "N/A")
        stock_desc = po.get("StockDesc", "N/A")

        raw_qty = po.get("QuantityPO")
        quantity = int(raw_qty) if isinstance(raw_qty, (int, float)) and raw_qty == int(raw_qty) else raw_qty or "N/A"

        ship_date = po.get("ShipDate")
        required_date = po.get("RequiredDate")

        if isinstance(ship_date, datetime):
            target_date_str = ship_date.strftime("%d/%m/%Y")
        elif isinstance(required_date, datetime):
            target_date_str = required_date.strftime("%d/%m/%Y")
        else:
            target_date_str = "N/A"

        body += f"""
            <tr>
                <td style="border: 1px solid black; text-align: center; vertical-align: middle;">{po_number}</td>
                <td style="border: 1px solid black; text-align: center; vertical-align: middle;">{stock_code}</td>
                <td style="border: 1px solid black; text-align: center; vertical-align: middle;">{stock_desc}</td>
                <td style="border: 1px solid black; text-align: center; vertical-align: middle;">{quantity}</td>
                <td style="border: 1px solid black; text-align: center; vertical-align: middle;">{target_date_str}</td>
                <td style="border: 1px solid black; text-align: center; vertical-align: middle;"></td>
            </tr>
        """

    body += """
            </tbody>
        </table>

        <p style="margin-top: 20px;">Looking forward to your response at the earliest.</p>

        <p>Thank you.<br>
        Best Regards,<br>
        <b>Procurement Team</b></p>
    </body>
    </html>
    """
    return body


def get_access_token_from_backend(user_id: str) -> str:
    try:
        response = requests.get(
            "http://localhost:5000/api/get-valid-token",
            params={"user_id": user_id},
        )

        if response.status_code == 200:
            return response.json()["access_token"]
        elif response.status_code == 401:
            raise RuntimeError("User must login again - refresh token expired.")
        else:
            raise RuntimeError(f"Failed to get token: {response.status_code} - {response.text}")
    except Exception as e:
        raise RuntimeError(f"Error while getting token from backend: {e}")

        raise HTTPException(status_code=500, detail=f"Failed to get token: {str(e)}") 
    

def sendEmail(subject: str, body: str, to_email: str,
              message_type: str = "status_chase",
              access_token: Optional[str] = None) -> Tuple[bool, Optional[str]]:

    try:
        if not access_token:
            access_token = get_access_token_from_backend(user_id="adminprocurement@Zeus.ie")

        success, message_id = save_email_as_draft(
            subject=subject,
            body=body,
            to_email=to_email,
            access_token=access_token,
        )
        return success, message_id

    except Exception as e:
        print(f"Failed to save email draft: {e}")
        return False, None


def save_email_as_draft(subject, body, to_email,access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    email_payload = {
        "subject": subject,
        "body": {
            "contentType": "HTML",
            "content": body
        },
        "toRecipients": [
            {
                "emailAddress": {
                    "address": to_email
                }
            }
        ]
    }

    response = requests.post(
        "https://graph.microsoft.com/v1.0/me/messages",
        headers=headers,
        json=email_payload
    )

    if response.status_code == 201:
        message_id = response.json().get("internetMessageId")
        print("Draft email created successfully.")
        return True, message_id
    else:
        print("Failed to save draft:", response.status_code, response.text)
        return False, None