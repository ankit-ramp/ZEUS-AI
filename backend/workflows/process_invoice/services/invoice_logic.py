import os
from tools.check_file_type import check_file_type
from tools.pdf_to_text import extract_text_from_pdf
from tools.html_to_text import extract_text_from_html
from tools.word_to_text import docx_to_text
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_google_genai import ChatGoogleGenerativeAI
from process_invoice.models.invoice_graph_schema import SimpleState, InvoiceResponse
from langchain_core.messages import HumanMessage
from process_invoice.services.invoice_prompt import invoice_prompt_template
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import Table, Column, MetaData
from sqlalchemy.types import String, Integer, Float, DateTime
from datetime import datetime
from workflows.process_invoice.services.logger import logger
from tools.connection import Connect

import re
load_dotenv()

def get_invoice_table_schema(table_name: str, metadata: MetaData):
    return Table(
        table_name,
        metadata,
        Column("product_name", String(255)),
        Column("product_code", String(255)),
        Column("product_description", String(255)),
        Column("product_quantity", Integer),
        Column("product_unit_price", Float),
        Column("product_price", Float),
        Column("vendor_name", String(255)),
        Column("invoice_number", String(255)),
        Column("invoice_date", String(255)),  # consider using Date() if always formatted
        Column("due_date", String(255)),
        Column("currency", String(10)),
        Column("net_amount", Float),
        Column("tax_amount", Float),
        Column("invoice_amount", Float),
        Column("file_name", String(255)),
        Column("confidence", Float, default=0.0),  # Confidence score of the extraction
        Column("inserted_at", DateTime)
    )

def create_table_if_not_exists_and_insert(df: pd.DataFrame, table_name: str, engine):
    metadata = MetaData()
    table = get_invoice_table_schema(table_name, metadata)

    # Add inserted_at if not present
    if "inserted_at" not in df.columns:
        df["inserted_at"] = datetime.now()

    # Reorder/match columns exactly as defined
    df = df[[col.name for col in table.columns]]

    # Create table if it doesn't exist
    metadata.create_all(engine, checkfirst=True)

    # Insert into table
    try:
        df.to_sql(table_name, con=engine, if_exists='append', index=False)
        logger.info(f"Inserted {len(df)} rows into '{table_name}' table.")
    except Exception as e:
        logger.error(f"Failed to insert data: {e}")

def load_files(state):
    folder_path = os.getenv("INVOICES_INPUT_FOLDER", "backend/workflows/process_invoice/invoice_input")
    files = [f for f in os.listdir(folder_path)]
    current_index_value = state.get("current_index", 0)
    logger.info(f"successfully loaded files{files[current_index_value]}")
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
    logger.info(f"successfully determined type{file_type}")

    return state 

def file_check(state):    
    file_type = state["file_type"]
    if file_type == "pdf" or file_type == "PDF":
        return "pdf"
    elif file_type == "html" or file_type =="htm":
        return "html"
    elif file_type == "doc" or file_type == "DOCX" or file_type == "docx":
        return "doc"
    else:
        return "other"
    
def process_pdf(state):
    file_path = state["file_path"]
    text = extract_text_from_pdf(file_path)
    state["extracted_text"] = text
    logger.info(f"successfully extracted text from pdf")
    return state
    

def process_html(state):
    file_path = state["file_path"]
    text = extract_text_from_html(file_path)
    state["extracted_text"] = text
    logger.info(f"successfully extracted text from html")

    return state

def process_word(state):
    print("Processing Word Document")
    file_path = state["file_path"]
    text = docx_to_text(file_path)
    state["extracted_text"] = text
    logger.info(f"successfully extracted text from word")

    return state

def increment_index(state):
    state["current_index"] += 1
    logger.info(f"successfully incremented index")

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
    logger.info(f"successfully llm response")
    return state


def check_continue(state):
    counter = state["current_index"]
    no_of_files = len(state["file_list"])
    # print("counter", counter, "total", no_of_files)
    
    if counter < no_of_files:
        logger.info(f"check continue returns loop")
        return "loop"
    else:
        logger.info(f"check continue returns end")
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
    confidence = response.get("confidence", 0.0)
    print(confidence)

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
                "file_name": file_name,
                "confidence": confidence

            }
            for product in response["invoice_lines"]
        ]

    if "rows" in state:
        state["rows"].extend(new_rows)
    else:
        state["rows"] = new_rows

    logger.info(f"Successfully row conversion from flatten response")
    return state


def save_dataframe_to_excel(state):
    rows = state.get("rows", [])
    if not rows:
        print("No rows to save.")
        return state

    df = pd.DataFrame(rows)
    expected_columns = [
        "vendor_name", "invoice_number", "invoice_date", "due_date", "currency",
        "net_amount", "tax_amount", "invoice_amount", "product_name", "product_code",
        "product_description", "product_quantity", "product_unit_price",
        "product_price", "file_name", "confidence"
    ]
    df = df[[col for col in expected_columns if col in df.columns]]
    logger.info("successfull df creation now pushing to sql")

    db_connector = Connect()
    # THIS IS THE CRUCIAL CHANGE: Call the method to get the engine
    engine = db_connector.zeus_automation_connection() 
    
    create_table_if_not_exists_and_insert(df, 'AI_invoice_automation', engine)
    logger.info("successfull push to sql")

    return state
