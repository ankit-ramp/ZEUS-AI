import streamlit as st
import requests
import pandas as pd
from io import BytesIO
from PIL import Image # PIL is imported but not used in the provided snippet. Keeping it for completeness.

st.set_page_config(page_title="Document Processor", layout="wide")

st.markdown("# 📄 <u>Document Processing App (PO/Invoice)</u>", unsafe_allow_html=True)

# --- Invoice Processing Section ---
st.header("Invoice Processing")
st.subheader("Upload Invoice Files")

uploaded_invoice_files = st.file_uploader(
    "Upload your invoice files (PDF, HTML, DOC)",
    type=["pdf", "html", "htm", "doc", "docx"],
    accept_multiple_files=True,
    key="invoice_uploader"
) 

if st.button("Process Invoices", key="process_invoices_button"):
    if not uploaded_invoice_files:
        st.warning("Please upload at least one invoice file to process.")
    else:
        with st.spinner("Processing invoice files..."):
            try:
                files_to_send = []
                for file in uploaded_invoice_files:
                    files_to_send.append(("files", (file.name, file.read(), file.type)))

                response = requests.post("http://127.0.0.1:8000/invoice", files=files_to_send)
                response.raise_for_status()
                
                # --- MODIFIED SECTION ---
                
                # Parse the new JSON response format
                result_json = response.json()
                header_rows = result_json.get("header_rows", [])
                product_rows = result_json.get("product_rows", [])

                if not header_rows and not product_rows:
                    st.warning("No invoice data (header or line items) was found in the processed files.")
                else:
                    st.success("✅ Invoice data extracted successfully!")

                    # Display the Header data
                    if header_rows:
                        st.subheader("Invoice Header")
                        df_header = pd.DataFrame(header_rows)
                        st.dataframe(df_header)

                    # Display the Product/Line Items data
                    if product_rows:
                        st.subheader("Invoice Line Items")
                        df_products = pd.DataFrame(product_rows)
                        st.dataframe(df_products)
                
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Invoice request failed: {e}")
                if 'response' in locals() and response is not None:
                    st.error(f"Server response: {response.text}")
            except Exception as e:
                st.error(f"❌ Failed to process invoices or load response: {e}")


st.markdown("---") # Separator for visual clarity

# --- Purchase Order Processing Section ---
st.header("Purchase Order Processing")
st.subheader("Upload Purchase Order (PO) Files")
uploaded_po_files = st.file_uploader(
    "Upload your purchase order files (PDF, HTML)",
    type=["pdf", "html", "htm"],
    accept_multiple_files=True,
    key="po_uploader" # Unique key for this uploader
)

if st.button("Process Purchase Orders", key="process_pos_button"): # Separate button for POs
    if not uploaded_po_files:
        st.warning("Please upload at least one purchase order file to process.")
    else:
        with st.spinner("Processing purchase order files..."):
            try:
                # Prepare files for multipart/form-data request for POs
                files_to_send = []
                for file in uploaded_po_files:
                    files_to_send.append(("files", (file.name, file.read(), file.type)))

                # Make the POST request to your FastAPI backend for PO upload
                upload_response = requests.post("http://127.0.0.1:8000/upload", files=files_to_send)
                upload_response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

                st.success("Files uploaded successfully. Now fetching processed data...")

                # Make the GET request to your FastAPI backend to download the processed CSV
                download_response = requests.get("http://127.0.0.1:8000/download")
                download_response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

                csv_bytes = download_response.content  # Raw bytes of CSV file from the response

                # Load CSV to DataFrame and display
                df = pd.read_csv(BytesIO(csv_bytes))
                st.success("✅ Purchase order data extracted successfully!")
                st.dataframe(df)

                # Add a download button to let the user download the CSV file
                st.download_button(
                    label="Download PO Results CSV",
                    data=csv_bytes,
                    file_name="processed_pos_results.csv",
                    mime="text/csv",
                    key="download_pos_button"
                )

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Purchase Order request failed: {e}")
                if 'upload_response' in locals() and upload_response is not None:
                    st.error(f"Upload server response: {upload_response.text}")
                if 'download_response' in locals() and download_response is not None:
                    st.error(f"Download server response: {download_response.text}")
            except Exception as e:
                st.error(f"❌ Failed to process purchase orders or load CSV: {e}")