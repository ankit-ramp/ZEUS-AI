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
    "Upload your invoice files (PDF, HTML)",
    type=["pdf", "html", "htm"],
    accept_multiple_files=True,
    key="invoice_uploader" # Unique key for this uploader
)

if st.button("Process Invoices", key="process_invoices_button"): # Separate button for invoices
    if not uploaded_invoice_files:
        st.warning("Please upload at least one invoice file to process.")
    else:
        with st.spinner("Processing invoice files..."):
            try:
                # Prepare files for multipart/form-data request for invoices
                files_to_send = []
                for file in uploaded_invoice_files:
                    files_to_send.append(("files", (file.name, file.read(), file.type)))

                # Make the POST request to your FastAPI backend for invoices
                response = requests.post("http://127.0.0.1:8000/invoice", files=files_to_send)
                response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

                csv_bytes = response.content  # Raw bytes of CSV file from the response

                # Load CSV to DataFrame and display
                df = pd.read_csv(BytesIO(csv_bytes))
                st.success("✅ Invoice data extracted successfully!")
                st.dataframe(df)

                # Add a download button to let the user download the CSV file
                st.download_button(
                    label="Download Invoice Results CSV",
                    data=csv_bytes,
                    file_name="processed_invoices_results.csv",
                    mime="text/csv",
                    key="download_invoices_button"
                )

            except requests.exceptions.RequestException as e:
                st.error(f"❌ Invoice request failed: {e}")
                if 'response' in locals() and response is not None:
                    st.error(f"Server response: {response.text}") # Show detailed error from backend
            except Exception as e:
                st.error(f"❌ Failed to process invoices or load CSV: {e}")

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