from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from pathlib import Path
import os
from dotenv import load_dotenv
import pandas as pd
from process_invoice.models.invoice_graph_schema import SimpleState, InvoiceResponse
from process_invoice.services.invoice_logic import load_files, process_current_file, file_check, process_pdf, process_html, increment_index, check_continue, process_word,  vendor_llm, header_llm, body_llm, persist_invoice_data, push_data, push_invoice_lines


def build_graph() -> StateGraph:
    builder = StateGraph(SimpleState)

    # builder.add_node("Token", get_dataverse_token)
    builder.add_node("load_files", load_files)
    builder.add_node("process_file", process_current_file)
    builder.add_node("processPDF", process_pdf)
    builder.add_node("processWord", process_word)
    builder.add_node("processHTML", process_html)
    builder.add_node("increment_index", increment_index)
    builder.add_node("vendor_llm", vendor_llm)
    builder.add_node("header_llm", header_llm)
    builder.add_node("body_llm", body_llm)
    builder.add_node("generate_rows", persist_invoice_data)
    builder.add_node("push_data", push_data )
    builder.add_node("push_product", push_invoice_lines)


    # builder.add_edge("Token", "load_files")    
    builder.add_edge("load_files", "process_file")
    builder.add_conditional_edges("process_file", file_check, {
        "pdf": "processPDF",
        "html": "processHTML",
        "doc": "processWord",
        "other": "increment_index"
    })
    builder.add_edge("processHTML", "vendor_llm")
    builder.add_edge("processWord", "vendor_llm")
    builder.add_edge("processPDF", "vendor_llm")
    builder.add_edge("vendor_llm", "header_llm")
    builder.add_edge("header_llm", "body_llm")
    builder.add_edge("body_llm", "generate_rows")
    builder.add_edge("generate_rows", "increment_index")
    builder.add_conditional_edges("increment_index", check_continue, {
        "loop": "process_file",
        "end": "push_data"
    })
    builder.add_edge("push_data", "push_product")
    builder.add_edge("push_product", END)



    

    # builder.add_node("flat", flatten_response)

    

    # builder.add_node("excel", save_dataframe_to_excel)
 
    # builder.add_node("check_continue", check_continue)

 
    # builder.add_edge("LLM", "flat")
    # builder.add_edge("flat", "increment_index")

    
    # builder.add_edge("excel", END)

    builder.set_entry_point("load_files")
    return builder.compile()

  
