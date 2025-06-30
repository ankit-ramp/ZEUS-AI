import streamlit as st
import requests
import pandas as pd
from io import BytesIO


st.set_page_config(page_title="Invoice Processor", layout="wide")

st.markdown("# 📄 <u>Invoice Processing App</u>", unsafe_allow_html=True)

uploaded_files = st.file_uploader("Upload multiple files", type=["pdf", "html", "htm"], accept_multiple_files=True)

if st.button("Submit Files") and uploaded_files:
    with st.spinner("Processing your files..."):
        try:
            files = [("files", (file.name, file.read(), file.type)) for file in uploaded_files]

            response = requests.post("http://127.0.0.1:8000/invoice", files=files)
            response.raise_for_status()

            csv_bytes = response.content  # raw bytes of CSV file

            # Load CSV to DataFrame and display
            df = pd.read_csv(BytesIO(csv_bytes))
            st.success("✅ Data extracted successfully!")
            st.dataframe(df)

            # Add a download button to let user download CSV file
            st.download_button(
                label="Download CSV",
                data=csv_bytes,
                file_name="results.csv",
                mime="text/csv"
            )

        except requests.exceptions.RequestException as e:
            st.error(f"❌ Request failed: {e}")
        except Exception as e:
            st.error(f"❌ Failed to load CSV: {e}")
