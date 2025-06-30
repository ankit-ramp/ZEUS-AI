import os
from tools.check_file_type import check_file_type
from tools.pdf_to_text import extract_text_from_pdf
from tools.html_to_text import extract_text_from_html
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_google_genai import ChatGoogleGenerativeAI
from process_invoice.models.invoice_graph_schema import SimpleState, InvoiceResponse
from langchain_core.messages import HumanMessage
from process_invoice.services.invoice_prompt import invoice_prompt_template
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import pandas as pd

import re
load_dotenv()




def load_files(state):
    folder_path = os.getenv("INVOICES_INPUT_FOLDER", "backend/workflows/process_invoice/invoice_input")
    files = [f for f in os.listdir(folder_path)]
    current_index_value = state.get("current_index", 0)
    return {
        "file_list": files,
        "current_index": current_index_value,
        "folder_path": folder_path
    }


def process_current_file(state):

    index = state["current_index"]
    file_list = state["file_list"]
    file_name = file_list[index]
    file_path = state["folder_path"] + "/" +file_name
    file_type = check_file_type(file_name)
    state["file_path"] = file_path
    state["file_type"] = file_type
    return state 

def file_check(state):    
    file_type = state["file_type"]
    if file_type == "pdf" or file_type == "PDF":
        return "pdf"
    elif file_type == "html" or file_type =="htm":
        return "html"
    else:
        return "other"
    
def process_pdf(state):
    file_path = state["file_path"]
    text = extract_text_from_pdf(file_path)
    state["extracted_text"] = text
    return state
    

def process_html(state):
    file_path = state["file_path"]
    text = extract_text_from_html(file_path)
    state["extracted_text"] = text
    return state

def increment_index(state):
    state["current_index"] += 1
    return state


def  llm_input(state):
    
    pydantic_parser = PydanticToolsParser(tools=[InvoiceResponse])
    text = state["extracted_text"]
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.0,
        
    )
    invoice_prompt = invoice_prompt_template
    first_responder_chain = invoice_prompt | llm.bind_tools( tools=[InvoiceResponse], tool_choice="InvoiceResponse") | pydantic_parser
    response = first_responder_chain.invoke({
        "messages": [HumanMessage(content= str(text))]
    })
    state["llm_response"] = response
    return state


def check_continue(state):
    counter = state["current_index"]
    no_of_files = len(state["file_list"])
    # print("counter", counter, "total", no_of_files)
    
    if counter < no_of_files:
        return "loop"
    else:
        return "end"


def flatten_response(state):
    response = state["llm_response"] 
    response = dict(response[0])  
    file_list = state["file_list"]
    current_index = state["current_index"]
    file_name = file_list[current_index]
    vendor_name = response.get("vendor_name")
    invoice_number = response.get("invoice_number")
    invoice_date = response.get("invoice_date")
    due_date = response.get("due_date")
    currency = response.get("currency")
    net_amount = response.get("net_amount")
    tax_amount = response.get("tax_amount")
    invoice_amount = response.get("invoice_amount")

    new_rows = [
            {
                **product.dict(),
                "vendor_name": vendor_name,
                "invoice_number": invoice_number,
                "invoice_date": invoice_date,
                "due_date": due_date,
                "currency": currency,
                "net_amount": net_amount,
                "tax_amount": tax_amount,
                "invoice_amount": invoice_amount,
                "file_name": file_name

            }
            for product in response["invoice_lines"]
        ]

    if "rows" in state:
        state["rows"].extend(new_rows)
    else:
        state["rows"] = new_rows

    return state


def save_dataframe_to_excel(state):
    rows = state.get("rows", [])
    if not rows:
        print("No rows to save.")
        return state

    df = pd.DataFrame(rows)
    print(df)

    # ✅ Get output directory from environment variable
    output_dir = os.getenv("INVOICES_OUTPUT_FOLDER", "backend/workflows/process_invoice/invoice_output")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "output.csv")

    expected_columns = [
        "vendor_name", "invoice_number", "invoice_date", "due_date", "currency",
        "net_amount", "tax_amount", "invoice_amount", "product_name", "product_code",
        "product_description", "product_quantity", "product_unit_price",
        "product_price", "file_name"
    ]
    df = df[[col for col in expected_columns if col in df.columns]]

    df.to_csv(output_path, index=False)
    print("Saved to CSV:", output_path)

    return state
