import os
import sys
import re
import openpyxl
from rapidfuzz import process, fuzz
from langchain_core.messages import HumanMessage
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools.check_file_type import check_file_type
from tools import html_to_text, pdf_to_text
from langchain_google_genai import ChatGoogleGenerativeAI
from models.response_schema import Answer
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from services.prompts import get_company_prompt
from dotenv import load_dotenv
import pandas as pd
import re
from tools.connection import Connect
from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.engine import Engine
from langchain_openai import ChatOpenAI

load_dotenv()
db_connector = Connect()
INPUT_DIR = os.getenv("PO_INPUT_FOLDER", "workflows/process_po/po_input")
OUTPUT_DIR = os.getenv("PO_OUTPUT_FOLDER", "workflows/process_po/po_output")

def get_gold_db() -> Generator[Engine, None, None]:
    try:
        engine = db_connector.gold_connection()
        if isinstance(engine, dict):  # check if it failed
            raise ConnectionError(engine["message"])
        yield engine
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gold DB connection failed: {e}"
        )
    finally:
        if 'engine' in locals() and engine:
            engine.dispose()

def load_files(state):
    folder_path = INPUT_DIR
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
    text = pdf_to_text.extract_text_from_pdf(file_path)
    state["extracted_text"] = text
    return state
    

def process_html(state):
    file_path = state["file_path"]
    text = html_to_text.extract_text_from_html(file_path)
    state["extracted_text"] = text
    return state

def  llm_input(state):
    
    pydantic_parser = PydanticToolsParser(tools=[Answer])
    company = state["company"]
    text = state["extracted_text"]
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    company_prompt = get_company_prompt(company)
    first_responder_chain = company_prompt| llm.bind_tools( tools=[Answer], tool_choice="Answer") | pydantic_parser
    response = first_responder_chain.invoke({
        "messages": [HumanMessage(content= str(text))]
    })
    state["llm_response"] = response
    return state


def flatten_response(state):
    response = state["llm_response"] 
    response = dict(response[0])  
    file_list = state["file_list"]
    current_index = state["current_index"]
    file_name = file_list[current_index]
    delivery_address = response.get("delivery_address")
    customer_order_number = response.get("customer_order_number")
    postal_code = response.get("postal_code")
    order_cache = state.get("order_cache", [])

    order_cache = state.get("order_cache", [])
    customer_ref_match, delivery_ref_match = find_best_postal_reference(postal_code, order_cache)

    new_rows = [
            {
                **product.dict(),
                "delivery_address": delivery_address,
                "postal_code": postal_code,
                "customer_order_number": customer_order_number,
                "file_name": file_name,
                "Customer Ref": customer_ref_match,
                "Delivery reference": delivery_ref_match

            }
            for product in response["product_details"]
        ]

    if "rows" in state:
        state["rows"].extend(new_rows)
    else:
        state["rows"] = new_rows

    return state


def save_dataframe_to_csv(state):
    rows = state.get("rows", [])

    if not rows:
        print("No rows to save.")
        return state 
    
    df = pd.DataFrame(rows)

    def remove_special_chars(text):
        if isinstance(text, str):
            return re.sub(r'[^A-Za-z0-9\s]', '', text)
        return text

    if 'customer_product_code' in df.columns:
        df['customer_product_code'] = df['customer_product_code'].apply(remove_special_chars)

    filename = "output.csv"
    output_dir = OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    # Optional: select specific columns (only if they all exist in df)
    expected_cols = [
        "Customer Ref", "Delivery reference", "delivery_address", "postal_code",
        "customer_order_number", "stock_code", "product_quantity", "unit_price",
        "product_value", "product_name", "company_name", "customer_product_code", "file_name"
    ]
    df = df[[col for col in expected_cols if col in df.columns]]

    df.to_csv(output_path, index=False)
    print("Saved to CSV.")
    
    return state

def increment_index(state):
    state["current_index"] += 1
    return state

def check_continue(state):
    counter = state["current_index"]
    no_of_files = len(state["file_list"])
    # print("counter", counter, "total", no_of_files)
    
    if counter < no_of_files:
        return "loop"
    else:
        return "end"



def find_best_postal_reference(postal_code: str, order_cache: list, score_threshold=70):
    if not postal_code:
        return "", ""
    postal_code = postal_code.strip().replace(" ", "").replace("-", "").upper()  # Normalize postal code
    postal_code = re.sub(r'[^A-Za-z0-9]', '', postal_code).upper()

    # Extract addresses from cache
    addresses = [entry.get("Address", "") for entry in order_cache]
    print("Normalized postal_code:", postal_code)
    print("Normalized addresses:", addresses[:1])   
    # Find best fuzzy match
    match, score, idx = process.extractOne(postal_code, addresses, scorer=fuzz.partial_ratio)
    
    if score >= score_threshold:
        customer_ref = order_cache[idx].get("Customer_Reference")
        delivery_ref = order_cache[idx].get("Delivery_Reference")
        print("The customer code is", customer_ref)
        print("The delivery reference is", delivery_ref)
        return customer_ref, delivery_ref # Return both values as a tuple
    
    return "", ""