from typing import List, Optional
from pydantic import BaseModel, Field
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Product(BaseModel):
    product_name: Optional[str] = Field(default=None, description="Name of the product")
    product_code: Optional[str] = Field(default=None, description="Unique code of the product")
    product_description: Optional[str] = Field(default=None, description="Description of the product")
    product_quantity: Optional[int] = Field(default=None, description="Quantity of the product")
    product_unit_price: Optional[float] = Field(default=None, description="Unit price of the product")
    product_price: Optional[float] = Field(default=None, description="Total price of the product, product_quantity * product_unit_price")

class InvoiceResponse(BaseModel):
    """Information from pdf"""
    vendor_name: Optional[str] = Field(default=None, description="Name of the company who generated the invoice, cannot be zeus packaging")
    invoice_number: Optional[str] = Field(default=None, description="Unique invoice number")
    invoice_date: Optional[str] = Field(default=None, description="The date of the invoice generation")
    due_date: Optional[str] = Field(default=None, description="Date the invoice is due")
    currency: Optional[str] = Field(default=None, description="Currency of the invoice, e.g. GBP, EUR")
    net_amount: Optional[float] = Field(default=None, description="Net amount of the invoice, invoice_amount - tax_amount")
    tax_amount: Optional[float] = Field(default=None, description="Tax amount of the invoice, invoice_amount - net_amount")
    invoice_amount: Optional[float] = Field(default=None, description="Total amount of the invoice, net_amount + tax_amount")
    invoice_lines: Optional[List[Product]] = Field(default=None, description="Details of the product")
    confidence: Optional[float] = Field(default=None, description="Confidence score of the extraction, between 0.0 and 1.0")
