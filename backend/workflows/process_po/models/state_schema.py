from typing import TypedDict, List
from response_schema import Answer

class SimpleState(TypedDict):
    company: str
    file_list: List[str]
    current_index: int
    folder_path: str
    file_type: str
    file_path: str 
    extracted_text: Answer
    rows: List[dict]
    