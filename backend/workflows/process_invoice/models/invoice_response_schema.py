from typing import List, Optional
from pydantic import BaseModel, Field
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Product(BaseModel):
    product_name: Optional[str] = Field(default="", description="Name of the product")
    product_code: Optional[str] = Field(default="", description="Unique code of the product")
    product_description: Optional[str] = Field(default="", description="Description of the product")
    product_quantity: Optional[int] = Field(default="", description="Quantity of the product")
    product_unit_price: Optional[float] = Field(default="", description="Unit price of the product")
    product_price: Optional[float] = Field(default="", description="Total price of the product, product_quantity * product_unit_price")

class InvoiceResponse(BaseModel):
    """Information from pdf"""
    vendor_name: Optional[str] = Field(default="", description="Name of the company who generated the invoice, cannot be zeus packaging")
    zp_INVOICENUMBER: Optional[str] = Field(default="", description="Unique invoice number")
    invoice_date: Optional[str] = Field(default="", description="The date of the invoice generation")
    due_date: Optional[str] = Field(default="", description="Date the invoice is due")
    currency: Optional[str] = Field(default="", description="Currency of the invoice, e.g. GBP, EUR")
    net_amount: Optional[float] = Field(default="", description="Net amount of the invoice, invoice_amount - tax_amount")
    tax_amount: Optional[float] = Field(default="", description="Tax amount of the invoice, invoice_amount - net_amount")
    invoice_amount: Optional[float] = Field(default="", description="Total amount of the invoice, net_amount + tax_amount")
    invoice_lines: Optional[List[Product]] = Field(default="", description="Details of the product")
    confidence: Optional[float] = Field(default="", description="Confidence score of the extraction, between 0.0 and 1.0")
