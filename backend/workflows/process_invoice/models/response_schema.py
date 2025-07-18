from typing import List, Optional
from pydantic import BaseModel, Field
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class VendorResponse(BaseModel):
    """Information from pdf"""
    vendor_name: str = Field(default="", description="Name of the company who generated the invoice, cannot be zeus packaging")


class HeaderResponse(BaseModel):
    """Information from pdf"""
    zp_name: Optional[str] = Field(default="", description="Unique invoice number")
    zp_PurchaseOrder: Optional[str] = Field(default="", description= "Purchaseorder/ customer order no/ customer ref no, generally starts with A")
    zp_invoicedate: Optional[str] = Field(default="", description="The date of the invoice generation")
    zp_duedate: Optional[str] = Field(default="", description="Date the invoice is due")
    transactioncurrencyid: Optional[str] = Field(default="", description="Currency of the invoice, e.g. GBP, EUR")
    zp_netamount: Optional[float] = Field(default="", description="Net amount of the invoice, invoice_amount - tax_amount")
    zp_taxamount: Optional[float] = Field(default="", description="Tax amount of the invoice, invoice_amount - net_amount")
    zp_invoiceamount: Optional[float] = Field(default="", description="Total amount of the invoice, net_amount + tax_amount")


class ProductResponse(BaseModel):
    """Information from pdf"""
    zp_productx: Optional[str] = Field(default=None, description="Name of the product dont include quantity like kg no etc") #zp_productx
    # product_code: Optional[str] = Field(default="", description="Unique code of the product")
    zp_description: Optional[str] = Field(default=None, description="Description of the product") #zp_description
    zp_quantity: Optional[int] = Field(default=None, description="Quantity of the product") #zp_quantity
    zp_unitprice: Optional[float] = Field(default=None, description="Unit price of the product") #zp_unitprice
    zp_lineamount: Optional[float] = Field(default=None, description="Total price of the product, product_quantity * product_unit_price") #zp_lineamount
    zp_taxamount: Optional[float] = Field(default=None, description= "Taxed amount on the product ") #zp_taxamount
