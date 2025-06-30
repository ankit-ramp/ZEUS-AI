from pydantic import BaseModel, Field
from typing import List, Optional
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Product(BaseModel):
    stock_code: Optional[str] = Field(default=None, description="product code of the current product/item")
    product_quantity: Optional[float] = Field(default=None, description="quantity of the current product")
    customer_product_code: Optional[str] = Field(default=None, description="supplier ref code of the current product")
    unit_price: Optional[float] = Field(default=None, description="price per unit")
    product_value: Optional[float] = Field(default=None, description="value of the current product")
    product_name: Optional[str] = Field(default=None, description="name of the product")
    company_name: Optional[str] = Field(default=None, description="name of the company who generated the purchase order (can never be zeus packaging)")

class Answer(BaseModel):
    delivery_address: Optional[str] = Field(default=None, description="delivery address of the current company, generally appears after deliver to")
    postal_code: Optional[str] = Field(default=None, description="postal code of the delivery address, generally 7 digit alphanumeric in nature, appears in delivery address")
    customer_order_number: Optional[str] = Field(default=None, description="purchase order number")
    product_details: Optional[List[Product]] = Field(default=None, description="details of the product")
