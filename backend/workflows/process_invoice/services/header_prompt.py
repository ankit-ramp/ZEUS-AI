from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import datetime



def get_header_prompt(header: str):

    header_prompt_template = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert data extractor working for Zeus Packaging.
        Your task is to accurately extract structured headers data from PDF invoice documents.

        Current time: {time}

        **Instructions:**

        Extract the following top-level invoice fields:
        {header}

         Maintain data integrity:
            - Use float types for all price-related fields.
            - Preserve all formatting, including leading zeros.
            - Return `""` for missing string fields, `0.0` for missing float fields, and `0` for missing integer fields.
            - Do not include any additional metadata or fields beyond the specified structure.   
              
        """
    ),
    MessagesPlaceholder(variable_name="messages"),
    (
        "system", "Ensure the final output is a valid JSON object that exactly matches the structure and types shown above."
    )
    ]).partial(
    time=lambda: datetime.datetime.now().isoformat(),
    header = header
    )

    return header_prompt_template




       
#         **Final output must strictly follow this JSON format and types:**
#         ```json
#         {{
#             "Vendor_name": "ABC Packaging Ltd",
#             "invoice_number": "INV-20250601",
#             "invoice_date": "2025-06-01",
#             "due_date": "2025-07-01",
#             "currency": "GBP",
#             "net_amount": 950.00,
#             "tax_amount": 190.00,
#             "invoice_amount": 1140.00,
#             "confidence": 0.95,
#             "invoice_lines": [
#                 {{
#                     "Product_name": "Biodegradable Bubble Wrap",
#                     "product_code": "BBRW-450X100",
#                     "product_description": "450mm x 100m eco-friendly bubble wrap roll",
#                     "product_quantity": 10,
#                     "product_unit_price": 5.00,
#                     "product_price": 50.00
#                 }},
#                 {{
#                     "Product_name": "Corrugated Card Sheets",
#                     "product_code": "CCS-A3",
#                     "product_description": "A3 size cardboard sheets, 100gsm",
#                     "product_quantity": 100,
#                     "product_unit_price": 0.90,
#                     "product_price": 90.00
#                 }}
#             ]
#         }}
#         ```