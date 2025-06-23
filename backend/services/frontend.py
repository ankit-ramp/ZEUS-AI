import streamlit as st
import requests
import pandas as pd
from PIL import Image
st.markdown("# 📂 <u>Extract values from files </u>", unsafe_allow_html= True)

st.header("Features")
st.markdown("""
- Read PDF's and html/htm files.
- Fallback to OCR if scanned files are provided.
- structured data output in single excel file.                        
""")

st.header("Stack Used")
st.markdown("""
- Python
- FastAPI
- Pydantic
- Langchain 
- BeautifulSoup
- PdfPlumber      
- Tesseract
- PDdf2image
- Pandas   
- Langgraph                                                                                                                                                
""")

st.header("ControlFlow")
# st.markdown(""
# """
# 1. Send get request on the defined endpoint.
# 2. Primaryhandler function is called.
# 3. Check_file_type function to check type of file, return pdf,html, other.
# 4. Extract data from pdf/html from their respective functions (Fallback to OCR using tesseract).
# 5. Send the text data to generate_parameters function.
# 6. Chains are defined in chains.py and prompts that are given to AI are in prompts.py, returns the data in structured format.
# 7. Flatten function is called to pivot the data in rows format, data is saved in an array.
# 8. After processing all files the array is used to construct dataframe and then generate and excel file.
# """)
image = Image.open("/Users/ankitchaturvedi/Desktop/ml_practice/image.png")
st.image(image, caption="langgraph workflow")


st.header("Endpoints")
st.subheader("HealthCheck")
st.code("""

@app.get("/")
def health_path():
    response = process.healthCheck()
    return response

""", language="python")

if st.button("Check Status"):
    with st.spinner("Checking Status"):
        try:
            response = requests.get("http://127.0.0.1:8000/")
            response.raise_for_status()
            result = response.json()

            st.success(result)

        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")

st.subheader("Process PO's")

st.code("""     
@app.get("/po/company")
def handle_files():
    response, df = process.primaryHandler()
    return {
        "message": response,
        "data": df.to_dict(orient="records") 
    }

""", language="python")


company = st.text_input("Enter Company Name", placeholder="e.g., drinagh")

if st.button("Run") and company:
    with st.spinner(f"Processing the file for {company.title()}..."):
        try:
            url = f"http://127.0.0.1:8000/{company.lower()}"
            response = requests.get(url)
            response.raise_for_status()
            result = response.json()

            st.success("OK response")

            if "rows" in result:
                df = pd.DataFrame(result["rows"])
                st.dataframe(df)
        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")

