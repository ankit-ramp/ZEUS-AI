from typing import TypedDict, List
from pydantic import BaseModel, Field
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from workflows.process_invoice.models.invoice_response_schema import InvoiceResponse

class SimpleState(TypedDict):
    file_list: List[str]
    current_index: int
    folder_path: str
    file_type: str
    file_path: str 
    token: str
    vendor: str
    extracted_text: str
    header: dict
    invoice_lines:List[dict]
    header_rows: dict
    product_rows: List[dict]

   
    
    
 
