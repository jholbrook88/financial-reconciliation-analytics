"""Build a cash-ledger extract from the Charles River accounting tables."""

from datetime import timedelta

import pandas as pd

from .config import ReconciliationConfig
from .data_loading import load_csv, require_columns


def _mapping(frame: pd.DataFrame, key: str, value: str) -> dict:
    return frame.set_index(key)[value].fillna("").to_dict()


def build_cash_ledger(config: ReconciliationConfig) -> pd.DataFrame:
    gl = load_csv(config.source_dir, "GLEntry")
    require_columns(
        gl,
        {
            "GLEntryID",
            "PostingDate",
            "AccountID",
            "Debit",
            "Credit",
            "VoucherNumber",
            "SourceDocumentType",
            "SourceDocumentID",
        },
        "GLEntry",
    )

    gl = gl.loc[gl["AccountID"].eq(config.cash_account_id)].copy()
    gl["PostingDate"] = pd.to_datetime(gl["PostingDate"], errors="raise")
    gl["Debit"] = pd.to_numeric(gl["Debit"], errors="coerce").fillna(0.0)
    gl["Credit"] = pd.to_numeric(gl["Credit"], errors="coerce").fillna(0.0)
    gl["Amount"] = (gl["Debit"] - gl["Credit"]).round(2)

    start = pd.Timestamp(config.statement_start) - timedelta(days=config.ledger_lookback_days)
    end = pd.Timestamp(config.statement_end) + timedelta(days=config.ledger_lookahead_days)
    gl = gl.loc[gl["PostingDate"].between(start, end)].copy()

    receipts = load_csv(config.source_dir, "CashReceipt")
    disbursements = load_csv(config.source_dir, "DisbursementPayment")
    refunds = load_csv(config.source_dir, "CustomerRefund")
    payroll = load_csv(config.source_dir, "PayrollPayment")
    remittances = load_csv(config.source_dir, "PayrollLiabilityRemittance")
    commissions = load_csv(config.source_dir, "SalesCommissionPayment")
    customers = load_csv(config.source_dir, "Customer")
    suppliers = load_csv(config.source_dir, "Supplier")
    journals = load_csv(config.source_dir, "JournalEntry")

    customer_names = _mapping(customers, "CustomerID", "CustomerName")
    supplier_names = _mapping(suppliers, "SupplierID", "SupplierName")

    receipt_reference = _mapping(receipts, "CashReceiptID", "ReferenceNumber")
    receipt_number = _mapping(receipts, "CashReceiptID", "ReceiptNumber")
    receipt_customer = _mapping(receipts, "CashReceiptID", "CustomerID")

    payment_number = _mapping(disbursements, "DisbursementID", "PaymentNumber")
    payment_check = _mapping(disbursements, "DisbursementID", "CheckNumber")
    payment_method = _mapping(disbursements, "DisbursementID", "PaymentMethod")
    payment_supplier = _mapping(disbursements, "DisbursementID", "SupplierID")

    refund_reference = _mapping(refunds, "CustomerRefundID", "ReferenceNumber")
    refund_number = _mapping(refunds, "CustomerRefundID", "RefundNumber")
    payroll_reference = _mapping(payroll, "PayrollRegisterID", "ReferenceNumber")
    remittance_reference = _mapping(
        remittances, "PayrollLiabilityRemittanceID", "ReferenceNumber"
    )
    remittance_agency = _mapping(
        remittances, "PayrollLiabilityRemittanceID", "AgencyOrVendor"
    )
    commission_reference = _mapping(
        commissions, "SalesCommissionPaymentID", "ReferenceNumber"
    )
    commission_number = _mapping(
        commissions, "SalesCommissionPaymentID", "PaymentNumber"
    )
    journal_number = _mapping(journals, "JournalEntryID", "EntryNumber")
    journal_description = _mapping(journals, "JournalEntryID", "Description")

    def describe(row: pd.Series) -> tuple[str, str]:
        source_type = row["SourceDocumentType"]
        source_id = int(row["SourceDocumentID"])
        voucher = str(row["VoucherNumber"])

        if source_type == "CashReceipt":
            customer_id = receipt_customer.get(source_id)
            name = customer_names.get(customer_id, "Customer")
            return (
                str(receipt_reference.get(source_id, voucher)),
                f"CUSTOMER DEPOSIT - {name} - {receipt_number.get(source_id, voucher)}",
            )
        if source_type == "DisbursementPayment":
            supplier_id = payment_supplier.get(source_id)
            name = supplier_names.get(supplier_id, "Supplier")
            check = str(payment_check.get(source_id, "")).strip()
            reference = check if check and check.lower() != "nan" else payment_number.get(source_id, voucher)
            return (
                str(reference),
                f"{str(payment_method.get(source_id, 'Payment')).upper()} PAYMENT - {name} - {payment_number.get(source_id, voucher)}",
            )
        if source_type == "CustomerRefund":
            return (
                str(refund_reference.get(source_id, voucher)),
                f"CUSTOMER REFUND - {refund_number.get(source_id, voucher)}",
            )
        if source_type == "PayrollPayment":
            reference = str(payroll_reference.get(source_id, voucher))
            return reference, f"PAYROLL DIRECT DEPOSIT - {reference}"
        if source_type == "PayrollLiabilityRemittance":
            return (
                str(remittance_reference.get(source_id, voucher)),
                f"PAYROLL REMITTANCE - {remittance_agency.get(source_id, 'Agency')}",
            )
        if source_type == "SalesCommissionPayment":
            reference = commission_reference.get(source_id) or commission_number.get(source_id, voucher)
            return str(reference), f"SALES COMMISSION - {commission_number.get(source_id, voucher)}"
        if source_type == "JournalEntry":
            return (
                str(journal_number.get(source_id, voucher)),
                str(journal_description.get(source_id, "Manual journal entry")).upper(),
            )
        return voucher, f"{source_type} - {voucher}"

    labels = gl.apply(describe, axis=1, result_type="expand")
    labels.columns = ["Reference", "ReconciliationDescription"]
    gl = pd.concat([gl.reset_index(drop=True), labels.reset_index(drop=True)], axis=1)
    gl["Reference"] = gl["Reference"].fillna("").astype(str).str.strip()
    gl["Description"] = (
        gl.pop("ReconciliationDescription").fillna("").astype(str).str.strip()
    )

    return gl[
        [
            "GLEntryID",
            "PostingDate",
            "Reference",
            "Description",
            "Amount",
            "VoucherNumber",
            "SourceDocumentType",
            "SourceDocumentID",
        ]
    ].sort_values(["PostingDate", "GLEntryID"])
