from pydantic import BaseModel, Field
import sys
from typing import List
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Product(BaseModel):
    stock_code: str = Field(description="product code of the current product/item")
    product_quantity: float = Field(description= "quantity of the current product")
    customer_product_code: str = Field(description="supplier ref code of the current product") 
    unit_price: float = Field(description= "price per unit")
    product_value: float = Field(description= "value of the current product")
    product_name: str = Field(description= "name of the product")
    company_name: str = Field(description= "name of the company who genereated the purchase order (can never be zeus packaging)")

class Answer(BaseModel):
    "Information from pdf"
    delivery_address: str = Field(description="delivery address of the current company, generally appears after deliver to")
    postal_code: str = Field(description="postal code of the delivery address, generally 7 digit alphanumeric in nature, appears in delivery address")
    customer_order_number: str =Field(description="purchase order number ")
    product_details: List[Product]= Field(description= "detials of the product")
    
 