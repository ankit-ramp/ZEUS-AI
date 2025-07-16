import os
from tools.check_file_type import check_file_type
from tools.pdf_to_text import extract_text_from_pdf
from tools.html_to_text import extract_text_from_html
from tools.word_to_text import docx_to_text
import json
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_google_genai import ChatGoogleGenerativeAI
from workflows.process_invoice.models.response_schema import VendorResponse, HeaderResponse, ProductResponse
from langchain_core.messages import HumanMessage
from process_invoice.services.vendor_prompt import get_vendor_prompt
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import Table, Column, MetaData
from sqlalchemy.types import String, Integer, Float, DateTime
from datetime import datetime
from workflows.process_invoice.services.logger import logger
from tools.connection import Connect
from tools.dataverse_connection import Dataverse_read
from workflows.process_invoice.services.crud import create_item, read_item
from workflows.process_invoice.services.header_prompt import get_header_prompt
from workflows.process_invoice.services.body_prompt import get_body_prompt

import re
load_dotenv()


# def get_dataverse_token(state):
#     dv = Dataverse_read()
#     try:
#         token = dv.get_token()
#         state["token"] = token
#         logger.info("successfully fetched token")
#     except Exception as e:
#         logger.error(f"Failed to =fetch token {e}")    
#     return state
    

def vendor_llm(state):
    pydantic_parser = PydanticToolsParser(tools=[VendorResponse])
    text = state["extracted_text"]
    llm = ChatOpenAI(model_name="gpt-4o")
    # llm = ChatGoogleGenerativeAI(
    #     model="gemini-1.5-flash",
    #     google_api_key= os.getenv("GOOGLE_API_KEY")
        
    # )
    vendor_prompt = get_vendor_prompt()
    
    first_responder_chain = vendor_prompt | llm.bind_tools( tools=[VendorResponse], tool_choice="VendorResponse") | pydantic_parser
    response = first_responder_chain.invoke({
        "messages": [HumanMessage(content= str(text))]
    })

    response = response[0].vendor_name
    state["vendor"] = response
    logger.info(f"successfull vendor response")
    return state

def header_llm(state):
    vendor_name = state["vendor"]
    try:
        item = read_item(vendor_name)
        if item is None and vendor_name != "general":
            item = read_item("general")
            logger.info("Fetched the general HEADER prompt")
        else:
            logger.info(f"Fetched the {vendor_name} HEADER prompt")    
        header_prompt = get_header_prompt(item["header_prompt"])
        pydantic_parser = PydanticToolsParser(tools=[HeaderResponse])
        llm = ChatOpenAI(model_name="gpt-4o")
        # llm = ChatGoogleGenerativeAI(
        #     model="gemini-1.5-flash",
        #     google_api_key=os.getenv("GOOGLE_API_KEY")
        # )
        first_responder_chain = header_prompt | llm.bind_tools(tools=[HeaderResponse], tool_choice="HeaderResponse") | pydantic_parser
        response = first_responder_chain.invoke({
            "messages": [HumanMessage(content=str(state["extracted_text"]))]
        })[0]
        state["header"] = response
    except Exception as e:
        raise e
    return state


def body_llm(state):
    vendor_name = state["vendor"]
    try:
        item = read_item(vendor_name)
        if item is None and vendor_name != "general":
            item = read_item("general")
            logger.info("Fetched the general BODY prompt")

        else:
            logger.info(f"Fetched the {vendor_name} BODY prompt")       
        body_prompt = get_body_prompt(item["body_prompt"])
        pydantic_parser = PydanticToolsParser(tools=[ProductResponse])
        llm = ChatOpenAI(model_name="gpt-4o")
        # llm = ChatGoogleGenerativeAI(
        #     model="gemini-1.5-flash",
        #     google_api_key=os.getenv("GOOGLE_API_KEY")
        # )
        first_responder_chain = body_prompt | llm.bind_tools(tools=[ProductResponse], tool_choice="ProductResponse") | pydantic_parser
        response = first_responder_chain.invoke({
            "messages": [HumanMessage(content=str(state["extracted_text"]))]
        })
        state["invoice_lines"] = response
        logger.info("successfull body response")
    except Exception as e:
        logger.error(e)
        raise e
    return state

def persist_invoice_data(state: dict) -> dict:
    try:
        vendor = state.get("vendor", "")
        header = state.get("header", {})
        invoice_lines = state.get("invoice_lines", [])

        # Ensure persistent lists exist
        if "header_rows" not in state or not isinstance(state["header_rows"], list):
            state["header_rows"] = []
        if "product_rows" not in state or not isinstance(state["product_rows"], list):
            state["product_rows"] = []

        # Convert header to dict if it's a Pydantic object
        if hasattr(header, "dict"):
            header = header.dict()

        # Append header data with vendor
        header_entry = header.copy()
        header_entry["zp_vendor"] = vendor
        state["header_rows"].append(header_entry)

        # Append product lines
        for line in invoice_lines:
            if hasattr(line, "dict"):
                line = line.dict()
            line_entry = line.copy()
            line_entry["vendor"] = vendor
            line_entry["invoice_number"] = header.get("invoice_number", "")
            state["product_rows"].append(line_entry)

        logger.info("Successfully pushed product_rows and header_rows")

    except Exception as e:
        print(e)
        logger.error(f"persist_invoice_data error: {e}")
        raise e

    return state



def push_data(state):
    try:
        dv = Dataverse_read() # Assuming Dataverse_read() initializes your Dataverse client

        header_data_list = state.get("header_rows")
        product_data_list = state.get("product_rows", []) # Not directly used for header push

        if not header_data_list:
            return {
                "code": 400,
                "message": "Missing header_data in state. No invoice headers to process.",
                "data": None
            }

        all_header_results = []

        # Loop through each header dictionary in the list
        for i, current_header in enumerate(header_data_list):
            print(f"Processing Header {i + 1}...")

            # --- Currency Processing for the current header ---
            original_currency_code = current_header.get("transactioncurrencyid") 
            
            # Remove any pre-existing bind property for currency to ensure clean state before setting
            if "transactioncurrencyid@odata.bind" in current_header:
                del current_header["transactioncurrencyid@odata.bind"]
            
            if original_currency_code: # Only attempt if a currency code is present
                currency_guid = get_currency_guid_by_code(original_currency_code) # Your function to get GUID
                
                if currency_guid:
                    # If GUID found, add bind property
                    current_header["transactioncurrencyid@odata.bind"] = f"/transactioncurrencies({currency_guid})"
                    # Remove the original raw string value field (e.g., "USD") if it was used for the lookup
                    if "transactioncurrencyid" in current_header: # Check before deleting
                        del current_header["transactioncurrencyid"] 
                else:
                    # If GUID not found, set the original field to None.
                    # This will be serialized as 'null' in the final JSON payload to Dataverse.
                    current_header["transactioncurrencyid"] = None
                    print(f"Warning: Currency '{original_currency_code}' not found for Header {i+1}. Setting 'transactioncurrencyid' to null.")
            else:
                # If original_currency_code was already empty or None, ensure the field is explicitly None.
                # This catches cases where 'transactioncurrencyid' might be present but empty string.
                if "transactioncurrencyid" in current_header:
                    current_header["transactioncurrencyid"] = None


            original_vendor = current_header.get("zp_vendor")
            print("original vendor ", original_vendor)
            
            # Remove any pre-existing bind property for currency to ensure clean state before setting
            if  "zp_vendor" in current_header:
                del current_header["zp_vendor"]
            
            if original_vendor: # Only attempt if a currency code is present
                vendor_guid = get_vendor_guid_by_name(original_vendor) # Your function to get GUID
                print("vendor guid is", vendor_guid)
                
                if vendor_guid:
                    # If GUID found, add bind property
                    current_header["zp_VENDOR@odata.bind"] = f"/accounts({vendor_guid})"
                    print(current_header)
                    # Remove the original raw string value field (e.g., "USD") if it was used for the lookup
                    if "zp_VENDOR" in current_header: # Check before deleting
                        del current_header["zp_VENDOR"] 
                else:
                    # If GUID not found, set the original field to None.
                    # This will be serialized as 'null' in the final JSON payload to Dataverse.
                    current_header["zp_VENDOR"] = None
                    print(f"Warning: vendor '{original_vendor}' not found for Header {i+1}. Setting vendor to null.")
            else:
                # If original_currency_code was already empty or None, ensure the field is explicitly None.
                # This catches cases where 'transactioncurrencyid' might be present but empty string.
                if "zp_VENDOR" in current_header:
                    current_header["zp_VENDOR"] = None


            purchaseOrder = current_header.get("zp_PurchaseOrder")
            print("purchase order ", purchaseOrder)
            
            if "zp_PurchaseOrder" in current_header:
                del current_header["zp_PurchaseOrder"]
                
            if "zp_PurchaseOrder@odata.bind" in current_header:
                del current_header["zp_PurchaseOrder@odata.bind"]
            
            if original_vendor: # Only attempt if a currency code is present
                purchaseOrder_guid = get_purchse_order_guid(str(purchaseOrder))  # Your function to get GUID
                print("purchase order guid is", purchaseOrder_guid)
                
                if purchaseOrder_guid:
                    # If GUID found, add bind property
                    current_header["zp_PurchaseOrder@odata.bind"] = f"/zp_purchaseorder1s({purchaseOrder_guid})"
                   
                    if "zp_PurchaseOrder" in current_header: # Check before deleting
                        del current_header["zp_PurchaseOrder"] 
                else:
                   
                    current_header["zp_PurchaseOrder"] = None
                    print(f"Warning: Purchase order '{purchaseOrder}' not found for Header {i+1}. Setting purchase order to null.")
            else:
                
                if "zp_PurchaseOrder" in current_header:
                    current_header["zp_PurchaseOrder"] = None




            for key, value in current_header.items():
                if isinstance(value, str) and value == "":
                    current_header[key] = None

            
            print(f"Payload to Dataverse (Header {i + 1}):", json.dumps(current_header, indent=2))

           
            header_result = dv.insert_records_into_dataverse("zp_invoices", current_header)
            all_header_results.append(header_result) 

            print(f"Result for Header {i + 1}:", header_result)

            
            if header_result.get("code") != 200:
                return {
                    "code": header_result.get("code"),
                    "message": f"Header {i + 1} push failed: {header_result.get('message')}",
                    "data": header_result.get("data")
                }

        
        return {
            "code": 200,
            "message": "All invoice headers processed and pushed successfully!",
            "data": all_header_results 
        }

    except Exception as e:
        # General exception handler for any unforeseen errors
        print(f"An unexpected error occurred during invoice push: {e}") # Use f-string for better debugging
        return {
            "code": 500,
            "message": f"An unexpected error occurred during invoice push: {str(e)}",
            "data": None
        }


def get_vendor_guid_by_name(vendor_name):
    
    dv = Dataverse_read()
    
    response = dv.read_dataverse_withfilter("accounts", "name", vendor_name) 
    
    if response.get("code") == 200 and response.get("data"):
        
        return response["data"][0]["accountid"] 
    else:
         
        return None



def get_purchse_order_guid(purchseOrder):
    print("entered purchase order guid")
    dv = Dataverse_read()
    
    # Using the new read_dataverse_withfilter method
    # Entity set for Accounts is 'accounts', filter column for name is 'name', select accountid
    response = dv.read_dataverse_withfilter("zp_purchaseorder1s", "zp_newcolumn", purchseOrder) 
    print(response)
    if response.get("code") == 200 and response.get("data"):
        # The GUID for an account (vendor) is in the 'accountid' field
        return response["data"][0]["zp_purchaseorder1id"] 
    else:
         
        return None

def get_currency_guid_by_code(currency_code):

    dv = Dataverse_read()
    
    # Using the new read_dataverse_withfilter method
    response = dv.read_dataverse_withfilter("transactioncurrencies", "isocurrencycode", currency_code)
    
    if response.get("code") == 200 and response.get("data"):
        return response["data"][0]["transactioncurrencyid"]
    else:
        # The read_dataverse_withfilter already prints warnings/errors, so a simple return None is fine here.
        return None


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
    logger.info(f"successfully loaded files{files}")
    return {
        "file_list": files,
        "current_index": 0,
        "folder_path": folder_path
    }


def process_current_file(state):

    index = state["current_index"]
    file_list = state["file_list"]
    file_name = file_list[index]
    logger.info(f"Prcessing file {file_name}")
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
