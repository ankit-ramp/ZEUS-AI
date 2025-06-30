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
    extracted_text: str
    llm_response: InvoiceResponse
    rows: List[dict]
    
    
 
