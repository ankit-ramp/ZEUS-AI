from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import datetime

actor_prompt_template = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert data extractor working for Zeus Packaging.
        Your primary task is to precisely extract key information from PDF documents.

        Current time: {time}

        **Instructions for Extraction:**
        1. {first_instruction}
        2. Identify the **delivery address**, **company name**, and **product details** from the document.
        3. Extract the **purchase order number**.
        4. The **delivery_address** is the specific physical location where the products are being delivered. It **MUST appear directly after phrases like "Deliver To", "Ship To", or similar explicit delivery indicators**. Do not extract general company addresses found at the top of the document or in header/footer sections. **Crucially, this address must NOT be 'Zeus Packaging' or any variation of Zeus's own address**. If you encounter 'Zeus Packaging' as the delivery address, it indicates an internal note or that Zeus is the sender, in which case you should **leave the delivery_address field as an empty string ("")**.
        5. postal_code: str = Field(description="postal code of the delivery address, generally 7 digit alphanumeric in nature, appears in delivery address")
        6. The **company_name** is the name of the external company that *generated* or *sent* this PDF document (e.g., the supplier of the products or the customer who issued a PO). **This company name must NOT be 'Zeus Packaging' or any variation of Zeus's own company name**.
        7. **Product details** consist of the following attributes for each product line item:
            - `stock_code`: The unique product code or item number.
            - `customer_product_code`: The supplier's reference code for the product.
            - `product_quantity`: The numeric quantity of the current product.
            - `unit_price`: The numeric price per unit of the product.
            - `product_value`: The total numeric value for that specific product line (quantity * unit_price).
            - `product_name`: The full descriptive name of the product.
        8. Be extremely accurate. **Retain all original data, including leading zeros for codes/numbers**.
        9. If any required field is explicitly missing from the document, return an empty string ("") for string fields and 0.0 for numeric fields, but **always strictly maintain the exact JSON structure**.

        **Strict JSON Output Format (adhere precisely to this structure and data types):**
        ```json
        {{
            "delivery_address": "Customer's actual delivery address, e.g., '123 Any Street, Anytown, AB12 3CD, Country'",
             postal_code: str = Field(description="postal code of the delivery address, generally 7 digit alphanumeric in nature, appears in delivery address")
            "customer_order_number": "PO number, e.g., 'AC0105/45'",
            "company_name": "Name of the supplier/customer company that sent this document (NOT Zeus Packaging), e.g., 'ABC Supplies Ltd'",
            "product_details": [
                {{
                    "stock_code": "100230044",
                    "product_quantity": 20.0,
                    "customer_product_code": "ALLFEN010",
                    "unit_price": 120.0,
                    "product_value": 2400.0,
                    "product_name": "PRODUCT A DESCRIPTION"
                }},
                {{
                    "stock_code": "10432345235",
                    "product_quantity": 30.0,
                    "customer_product_code": "ALLFEN210",
                    "unit_price": 150.0,
                    "product_value": 4500.0,
                    "product_name": "FARMSTOKK FENCEPROPOLYTAPE 12MM 200M"
                }}
            ]
        }}
        ```
        """
    ),
    MessagesPlaceholder(variable_name="messages"),
    (
        "system", "Ensure the final output is a valid JSON object matching the provided example structure."
    )
]).partial(
    time=lambda: datetime.datetime.now().isoformat(),
)

def get_company_prompt(company: str):
    first_instruction = f"This specific document pertains to transactions with {company.capitalize()}."

    return actor_prompt_template.partial(
        first_instruction=first_instruction
    )
