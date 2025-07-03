from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from pathlib import Path
import os
from dotenv import load_dotenv
import pandas as pd
from process_invoice.models.invoice_graph_schema import SimpleState, InvoiceResponse
from process_invoice.services.invoice_logic import load_files, process_current_file, file_check, process_pdf, process_html, increment_index, llm_input, check_continue, flatten_response, save_dataframe_to_excel, process_word


def build_graph() -> StateGraph:
    builder = StateGraph(SimpleState)

    builder.add_node("load_files", load_files)
    builder.add_node("process_file", process_current_file)
    builder.add_edge("load_files", "process_file")
    

    builder.add_node("flat", flatten_response)

    builder.add_conditional_edges("process_file", file_check, {
        "pdf": "processPDF",
        "html": "processHTML",
        "doc": "processWord",
        "other": "increment_index"
    })

    builder.add_node("processPDF", process_pdf)
    builder.add_node("processWord", process_word)
    builder.add_node("processHTML", process_html)
    builder.add_node("excel", save_dataframe_to_excel)
    builder.add_node("LLM", llm_input)
    builder.add_node("increment_index", increment_index)
    builder.add_node("check_continue", check_continue)

    builder.add_edge("processHTML", "LLM")
    builder.add_edge("processWord", "LLM")

    builder.add_edge("processPDF", "LLM")
    builder.add_edge("LLM", "flat")
    builder.add_edge("flat", "increment_index")

    builder.add_conditional_edges("increment_index", check_continue, {
        "loop": "load_files",
        "end": "excel"
    })
    builder.add_edge("excel", END)

    builder.set_entry_point("load_files")
    return builder.compile()

  
