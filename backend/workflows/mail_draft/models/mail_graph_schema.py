from typing import TypedDict, List, Dict, Optional
from datetime import date

class AgentState(TypedDict, total=False):
    po_data: Optional[List[Dict]]
    eligible_chasing_pos: Optional[List[Dict]]
    current_po_group: Optional[Dict]
    current_email_details: Optional[Dict]
    sent_email_status: Optional[Dict]
    db_connection_string: Optional[str]
    today_date: date
    grouped_po_queue: Optional[List[List[Dict]]]
    access_token: Optional[str]