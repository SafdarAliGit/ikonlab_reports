from decimal import Decimal

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {
            "label": _("Item"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 100,
        },
        {
            "label": _("Opening Qty"),
            "fieldname": "opening_qty",
            "fieldtype": "Float",
            "width": 100
        },
        # {
        #     "label": _("Incoming Rate"),
        #     "fieldname": "incoming_rate",
        #     "fieldtype": "Currency",
        #     "width": 100
        # },
        {
            "label": _("Sold Qty"),
            "fieldname": "sold_qty",
            "fieldtype": "Float",
            "width": 100,
        },

        {
            "label": _("Sale Amount"),
            "fieldname": "sale_amount",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": _("Purchased Qty"),
            "fieldname": "purchased_qty",
            "fieldtype": "Float",
            "width": 100
        },

        {
            "label": _("Purchase Amount"),
            "fieldname": "purchase_amount",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": _("Balance Stock"),
            "fieldname": "balance_stock",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Return Qty"),
            "fieldname": "return_qty",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Return Amount"),
            "fieldname": "return_amount",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": _("Balance Stock Amount"),
            "fieldname": "balance_stock_amount",
            "fieldtype": "Currency",
            "width": 140
        }
    ]

    return columns


def get_conditions(filters):
    conditions = []
    if filters.get("item_code"):
        conditions.append(f"AND sle.item_code = %(item_code)s")
    if filters.get("from_date"):
        conditions.append(f"AND sle.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append(f"AND sle.posting_date <= %(to_date)s")
    return " ".join(conditions)


def get_data(filters):
    data = []
    conditions = get_conditions(filters)

    stock_balance_query = f"""
    SELECT 
        sle.item_code,
        ((COALESCE(SUM(sle.actual_qty),0) + COALESCE(SUM(sii.qty), 0)) - COALESCE(SUM(pii.qty), 0)) AS opening_qty,
        AVG(sle.incoming_rate) AS incoming_rate,
        COALESCE(SUM(CASE WHEN sii.qty > 0 THEN sii.qty ELSE 0 END), 0) AS sold_qty,
        ABS(COALESCE(SUM(CASE WHEN sii.qty < 0 THEN sii.qty ELSE 0 END), 0)) AS return_qty,
        ABS(COALESCE(SUM(CASE WHEN sii.amount < 0 THEN sii.amount ELSE 0 END), 0)) AS return_amount,
        COALESCE(SUM(CASE WHEN sii.amount > 0 THEN sii.amount ELSE 0 END), 0) AS sale_amount,
        COALESCE(SUM(pii.qty), 0) AS purchased_qty,
        COALESCE(SUM(pii.amount), 0) AS purchase_amount,
        SUM(sle.actual_qty) AS balance_stock,
        (SUM(sle.actual_qty) * AVG(sle.incoming_rate)) AS balance_stock_amount

    FROM `tabStock Ledger Entry` AS sle
    LEFT JOIN `tabSales Invoice Item` AS sii ON sii.name = sle.voucher_detail_no AND sle.voucher_type = 'Sales Invoice'
    LEFT JOIN `tabPurchase Invoice Item` AS pii ON pii.name = sle.voucher_detail_no AND sle.voucher_type = 'Purchase Invoice'
    WHERE
        sle.is_cancelled = 0
        {conditions}
    GROUP BY sle.item_code
    """

    result = frappe.db.sql(stock_balance_query, filters, as_dict=1)

    data.extend(result)
    return data

