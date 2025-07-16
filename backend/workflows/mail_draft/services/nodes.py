import pandas as pd
from datetime import date, datetime, timedelta
from workflows.mail_draft.models.mail_graph_schema import AgentState
# from db.connection import get_sqlalchemy_engine, get_pyodbc_connection
from workflows.mail_draft.services.mail_draft import (
    sendEmail,
    generate_chasing_email,
    get_access_token_from_backend
)
from tools.connection import Connect
# from config.settings import settings
from collections import defaultdict
from typing import Any

connector = Connect()

def fetch_po_data_node(state: AgentState) -> AgentState:
    print("Node: Fetching PO Data...")
    engine = connector.zeus_automation_connection()

    query = """
          SELECT GUID, PONumber,Container, SupplierName, Supplier_Email, StockCode, StockDesc,
            ShipDate, RequiredDate, QuantityPO, UnitCost, chase_counter, next_chase_date,
            entity_code, is_complete, PODate, SupplierRef, target_date, Confirmed_ETD, InReplyTo, message_id
        FROM [ZeusAutomation].[dbo].[Purchase_order_chasing]
        WHERE (
            (ShipDate BETWEEN CAST(GETDATE() AS DATE) AND DATEADD(day, 40, CAST(GETDATE() AS DATE)))
        )
        AND (
            Container IS NULL
            OR Container = ''
            OR Container NOT LIKE '%[A-Za-z]%'
        )
        AND SupplierRef IN (
            'HUH001',
            'HAN003',
            'JIAN HUA1',
            'WEA001',
            'BYT001',
            'JIA002',
            'WEI001',
            'FOR003',
            'SHA002',
            'ADA001',
            'ANP001',
            'APP001',
            'ART001'
        )

    """
    try:
        df = pd.read_sql(query, engine)
        print(f"Number of rows fetched from database: {len(df)}")

        df['chase_counter'] = df['chase_counter'].fillna(0).astype(int)
        df['is_complete'] = df['is_complete'].fillna(0).astype(int)
        date_cols = ['ShipDate', 'RequiredDate', 'PODate', 'Confirmed_ETD', 'next_chase_date']
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        state['po_data'] = df.to_dict(orient='records')

    except Exception as e:
        print(f"Error fetching PO data: {e}")
        state['po_data'] = []
    return state


def filter_eligible_chasing_pos_node(state: dict[str, Any]) -> dict[str, Any]:
    print("Node: Filtering Eligible Chasing POs...")

    today = date.today()
    future_cutoff = today + timedelta(days=10)
    print("Today:", today)

    eligible_chasing_pos = []
    supplier_po_map = defaultdict(list)
    suppliers_with_today_due_po = set()

    if state.get('po_data'):
        print("Total PO records received:", len(state['po_data']))

        for po in state['po_data']:
            chase_counter = int(po.get('chase_counter') or 0)
            is_complete = po.get('is_complete', 0)

            ship_date = pd.to_datetime(po.get('ShipDate'), errors='coerce')
            required_date = pd.to_datetime(po.get('RequiredDate'), errors='coerce')

            if ship_date == pd.Timestamp("1900-01-01"):
                ship_date = pd.NaT
            if required_date == pd.Timestamp("1900-01-01"):
                required_date = pd.NaT

            target_date = ship_date if not pd.isna(ship_date) else required_date
            if pd.isna(target_date):
                continue

            po["chasing_basis"] = "ShipDate" if not pd.isna(ship_date) else "RequiredDate"
            po["target_date"] = target_date

            next_chase_date = (target_date - timedelta(days=30)).date()
            po["next_chase_date"] = next_chase_date

            if chase_counter == 0 and not is_complete:
                supplier = po.get("SupplierName", "").strip()

                if today <= next_chase_date <= future_cutoff:
                    supplier_po_map[supplier].append(po)

                    if next_chase_date == today:
                        suppliers_with_today_due_po.add(supplier)

        for supplier in suppliers_with_today_due_po:
            eligible_chasing_pos.extend(supplier_po_map[supplier])

    state['eligible_chasing_pos'] = eligible_chasing_pos
    print(f"Total eligible POs for chasing today: {len(eligible_chasing_pos)}")
    return state

def regroup_chasing_pos_by_supplier_node(state: AgentState) -> AgentState:
    print("Node: Grouping POs by supplier name...")
    supplier_groups = defaultdict(list)

    for po in state.get("eligible_chasing_pos", []):
        supplier_name = po.get("SupplierName")
        if supplier_name:
            supplier_groups[supplier_name].append(po)

    state['grouped_po_queue'] = list(supplier_groups.values())
    print(f"Grouped into {len(state['grouped_po_queue'])} supplier groups.")
    return state


def determine_chase_email_type_node(state: AgentState) -> AgentState:
    print("Node: Determining Chase Email Type...")
    current_group = state.get('current_po_group')
    if not current_group:
        return state

    row = current_group[0]
    to_email = row.get("Supplier_Email")

    po_numbers = sorted({po.get("PONumber").strip() for po in current_group if po.get("PONumber")})
    po_list_str = ", ".join(po_numbers)
    subject = f"Status of PO {po_list_str}"

    body = generate_chasing_email(current_group)

    message_type = "status_chase"

    email_type = {
        "subject": subject,
        "body": body,
        "message_type": message_type,
        "to_email": to_email,
        "original_message_id": None
    }

    state['current_email_details'] = email_type
    return state


def initialize_token_node(state:AgentState) -> AgentState:
    print("Node: Getting access token...")
    try:
        access_token = get_access_token_from_backend(user_id="adminprocurement@Zeus.ie")
        state["access_token"] = access_token
    except Exception as e:
        print(f"Failed to get access token: {e}")
        state["access_token"] = None
    return state

def send_chase_email_node(state: AgentState) -> AgentState:
    print("Node: Sending Chase Email...")

    email_details = state.get('current_email_details')
    access_token = state.get("access_token")

    if not email_details:
        print("No email details found, skipping.")
        return state

    if not access_token:
        print("Access token missing, skipping email.")
        return state

    try:
        print("Preparing to send email with the following details:")
        print(f"Subject: {email_details['subject']}")
        print(f"To: {email_details['to_email']}")
        print(f"Type: {email_details['message_type']}")

        success, message_id = sendEmail(
            subject=email_details['subject'],
            body=email_details['body'],
            to_email=email_details['to_email'],
            message_type=email_details['message_type'],
            access_token=access_token
        )

    except Exception as e:
        print(f"Error sending email: {e}")
        success = False
        message_id = None

    state['sent_email_status'] = {
        'success': success,
        'message_id': message_id,
        'type': email_details['message_type']
    }

    return state



def update_po_status_and_log_sent_email_node(state: AgentState) -> AgentState:
    print("Node: Updating PO Status and Logging Sent Email...")
    current_group = state.get('current_po_group')
    email = state.get('current_email_details')
    email_status = state.get('sent_email_status')

    if not email or not email_status or not email_status.get('success'):
        print("Skipping DB update - email not sent or details missing.")
        return state

    po_group = current_group


    engine = connector.zeus_automation_connection()
    conn = engine.raw_connection()

    cursor = conn.cursor()
    try:
        today = date.today()
        next_chase_date = today + timedelta(days=1)
        message_id = email_status['message_id']

        for po in po_group:
            cursor.execute("""
                UPDATE [ZeusAutomation].[dbo].[Purchase_order_chasing]
                SET chase_counter = ISNULL(chase_counter, 0) + 1,
                    last_chased_date = ?,
                    message_id = ?,
                    next_chase_date = ?
                WHERE GUID = ?
            """, today, message_id, next_chase_date, po["GUID"])

            cursor.execute("""
                INSERT INTO [ZeusAutomation].[dbo].[email_logs](
                    po_number, entity_code, email_subject, email_body, to_email, sent_date, message_type,
                    message_id, has_attachment, missing_fields
                )    
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, po["PONumber"], po["entity_code"], email['subject'], email['body'],
                  email['to_email'], datetime.now(),
                 email['message_type'], message_id, False, None)

        conn.commit()
        print(f"Email ({email['message_type']}) sent and DB updated for {len(po_group)} POs.")
    except Exception as e:
        print(f"Error updating PO status or logging email: {e}")
    finally:
        cursor.close()
        conn.close()

    return state



def chase_po_iterator_node(state: AgentState) -> AgentState:
    print("Node: Chase PO Iterator...")

    if 'grouped_po_queue' not in state or not state['grouped_po_queue']:
        state['grouped_po_queue'] = []

    if state['grouped_po_queue']:
        state['current_po_group'] = state['grouped_po_queue'].pop(0)
    else:
        state['current_po_group'] = None

    return state