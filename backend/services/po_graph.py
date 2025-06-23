from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from pathlib import Path
import os
from dotenv import load_dotenv
import pandas as pd
from services.logic import load_files, process_current_file, file_check, process_html, process_pdf, llm_input, flatten_response, save_dataframe_to_excel, increment_index, check_continue
from models.response_schema import Answer
# from models.state_schema import SimpleState

class SimpleState(TypedDict):
    company: str
    file_list: List[str]
    current_index: int
    folder_path: str
    file_type: str
    file_path: str 
    extracted_text: str
    llm_response: Answer
    rows: List[dict]
    order_cache: List[dict]


def build_graph() -> StateGraph:
    builder = StateGraph(SimpleState)

    builder.add_node("load_files", load_files)
    builder.add_node("process_file", process_current_file)
    builder.add_edge("load_files", "process_file")
    

    builder.add_node("flat", flatten_response)

    builder.add_conditional_edges("process_file", file_check, {
        "pdf": "processPDF",
        "html": "processHTML",
        "other": "increment_index"
    })

    builder.add_node("processPDF", process_pdf)
    builder.add_node("processHTML", process_html)
    builder.add_node("excel", save_dataframe_to_excel)
    builder.add_node("LLM", llm_input)
    builder.add_node("increment_index", increment_index)
    builder.add_node("check_continue", check_continue)

    builder.add_edge("processHTML", "LLM")
    builder.add_edge("processPDF", "LLM")
    builder.add_edge("LLM", "flat")
    builder.add_edge("flat", "increment_index")

    builder.add_conditional_edges("increment_index", check_continue, {
        "loop": "load_files",
        "end": "excel"
    })

    builder.set_entry_point("load_files")
    return builder.compile()
