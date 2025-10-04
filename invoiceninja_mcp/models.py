from typing import Optional, List
from pydantic import BaseModel, Field


INVOICE_STATUS = {
    1: "Draft",
    2: "Sent",
    3: "Viewed",
    4: "Approved",
    5: "Partial",
    6: "Paid",
}


class InvoiceLineItem(BaseModel):
    product_key: Optional[str] = None
    notes: Optional[str] = None
    cost: Optional[float] = None
    quantity: Optional[float] = None
    tax_name1: Optional[str] = None
    tax_rate1: Optional[float] = None
    tax_name2: Optional[str] = None
    tax_rate2: Optional[float] = None
    line_total: Optional[float] = None


class Invoice(BaseModel):
    id: str
    user_id: Optional[str] = None
    assigned_user_id: Optional[str] = None
    amount: float = 0
    balance: float = 0
    client_id: Optional[str] = None
    vendor_id: Optional[str] = None
    status_id: int = 1
    design_id: Optional[str] = None
    invoice_number: Optional[str] = None
    number: Optional[str] = None
    discount: Optional[float] = 0
    po_number: Optional[str] = None
    date: Optional[str] = None
    last_sent_date: Optional[str] = None
    next_send_date: Optional[str] = None
    due_date: Optional[str] = None
    terms: Optional[str] = None
    public_notes: Optional[str] = None
    private_notes: Optional[str] = None
    uses_inclusive_taxes: bool = False
    tax_name1: Optional[str] = None
    tax_rate1: Optional[float] = 0
    tax_name2: Optional[str] = None
    tax_rate2: Optional[float] = 0
    tax_name3: Optional[str] = None
    tax_rate3: Optional[float] = 0
    total_taxes: Optional[float] = 0
    is_amount_discount: Optional[bool] = False
    footer: Optional[str] = None
    partial: Optional[float] = None
    partial_due_date: Optional[str] = None
    custom_value1: Optional[str] = None
    custom_value2: Optional[str] = None
    custom_value3: Optional[str] = None
    custom_value4: Optional[str] = None
    has_tasks: Optional[bool] = False
    has_expenses: Optional[bool] = False
    custom_surcharge1: Optional[float] = 0
    custom_surcharge2: Optional[float] = 0
    custom_surcharge3: Optional[float] = 0
    custom_surcharge4: Optional[float] = 0
    exchange_rate: Optional[float] = 1
    custom_surcharge_tax1: Optional[bool] = False
    custom_surcharge_tax2: Optional[bool] = False
    custom_surcharge_tax3: Optional[bool] = False
    custom_surcharge_tax4: Optional[bool] = False
    line_items: List[InvoiceLineItem] = Field(default_factory=list)
    entity_type: Optional[str] = "invoice"
    reminder1_sent: Optional[str] = None
    reminder2_sent: Optional[str] = None
    reminder3_sent: Optional[str] = None
    reminder_last_sent: Optional[str] = None
    paid_to_date: Optional[float] = 0
    subscription_id: Optional[str] = None
    auto_bill_enabled: Optional[bool] = False
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    archived_at: Optional[int] = None
    is_deleted: Optional[bool] = False

    def get_invoice_number(self) -> str:
        return self.invoice_number or self.number or f"INV-{self.id[:8]}"

    def get_status_name(self) -> str:
        return INVOICE_STATUS.get(self.status_id, f"Unknown ({self.status_id})")

    def get_amount_incl_tax(self) -> float:
        return self.amount

    def get_amount_excl_tax(self) -> float:
        return self.amount - (self.total_taxes or 0)


class Expense(BaseModel):
    id: str
    user_id: Optional[str] = None
    assigned_user_id: Optional[str] = None
    amount: float
    currency_id: Optional[str] = None
    expense_date: Optional[str] = None
    payment_date: Optional[str] = None
    exchange_rate: Optional[float] = 1
    foreign_amount: Optional[float] = None
    private_notes: Optional[str] = None
    public_notes: Optional[str] = None
    bank_id: Optional[str] = None
    transaction_id: Optional[str] = None
    category_id: Optional[str] = None
    client_id: Optional[str] = None
    invoice_id: Optional[str] = None
    vendor_id: Optional[str] = None
    project_id: Optional[str] = None
    payment_type_id: Optional[str] = None
    recurring_expense_id: Optional[str] = None
    custom_value1: Optional[str] = None
    custom_value2: Optional[str] = None
    custom_value3: Optional[str] = None
    custom_value4: Optional[str] = None
    tax_name1: Optional[str] = None
    tax_rate1: Optional[float] = 0
    tax_name2: Optional[str] = None
    tax_rate2: Optional[float] = 0
    tax_name3: Optional[str] = None
    tax_rate3: Optional[float] = 0
    uses_inclusive_taxes: bool = False
    calculate_tax_by_amount: Optional[bool] = False
    invoice_documents: Optional[bool] = False
    should_be_invoiced: Optional[bool] = False
    is_deleted: Optional[bool] = False
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    archived_at: Optional[int] = None


class Client(BaseModel):
    id: str
    user_id: Optional[str] = None
    assigned_user_id: Optional[str] = None
    name: Optional[str] = None
    website: Optional[str] = None
    private_notes: Optional[str] = None
    public_notes: Optional[str] = None
    phone: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country_id: Optional[str] = None
    industry_id: Optional[str] = None
    size_id: Optional[str] = None
    vat_number: Optional[str] = None
    id_number: Optional[str] = None
    number: Optional[str] = None
    shipping_address1: Optional[str] = None
    shipping_address2: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_postal_code: Optional[str] = None
    shipping_country_id: Optional[str] = None
    is_deleted: Optional[bool] = False
    balance: Optional[float] = 0
    paid_to_date: Optional[float] = 0
    credit_balance: Optional[float] = 0
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    archived_at: Optional[int] = None


class Vendor(BaseModel):
    id: str
    user_id: Optional[str] = None
    assigned_user_id: Optional[str] = None
    name: Optional[str] = None
    website: Optional[str] = None
    private_notes: Optional[str] = None
    public_notes: Optional[str] = None
    phone: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country_id: Optional[str] = None
    currency_id: Optional[str] = None
    vat_number: Optional[str] = None
    id_number: Optional[str] = None
    number: Optional[str] = None
    is_deleted: Optional[bool] = False
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    archived_at: Optional[int] = None


class ExpenseCategory(BaseModel):
    id: str
    user_id: Optional[str] = None
    name: str
    color: Optional[str] = None
    is_deleted: Optional[bool] = False
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    archived_at: Optional[int] = None
