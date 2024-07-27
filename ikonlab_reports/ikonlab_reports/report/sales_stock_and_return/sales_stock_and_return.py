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
            "label": _("Brand"),
            "fieldname": "brand",
            "fieldtype": "Link",
            "options": "Brand",
            "width": 100
        },
        {"label": _("Item Name"),
         "fieldname": "item_name",
         "width": 150
         },
        {
            "label": _("Item Group"),
            "fieldname": "item_group",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 100,
        },

        {
            "label": _("TP"),
            "fieldname": "trade_price",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 100
        },

        {
            "label": _("OPEN Qty"),
            "fieldname": "opening_qty",
            "fieldtype": "Float",
            "width": 100
        },

        {
            "label": _("Open Qty Amount"),
            "fieldname": "open_qty_amount",
            "fieldtype": "Currency",
            "width": 140
        },

        {
            "label": _("RCVD Qty"),
            "fieldname": "in_qty",
            "fieldtype": "Float",
            "width": 80
        },

        {
            "label": _("RCVD AMT."),
            "fieldname": "received_amount",
            "fieldtype": "Currency",
            "width": 140
        },
        {
            "label": _("Total Qty"),
            "fieldname": "total_qty",
            "fieldtype": "Float",
            "width": 80

        },

        {
            "label": _("Out Qty"),
            "fieldname": "out_qty",
            "fieldtype": "Float",
            "width": 80,
        },
        {
            "label": _("Sale Qty"),
            "fieldname": "sale_qty",
            "fieldtype": "Float",
            "width": 80

        },


        {
            "label": _("Sale AMT."),
            "fieldname": "out_amount",
            "fieldtype": "Currency",
            "width": 100
        },

        {
            "label": _("Bonus"),
            "fieldname": "bonus",
            "fieldtype": "Float",
            "width": 100
        },

        {
            "label": _("Bonus AMT."),
            "fieldname": "bonus_amount",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Net Sale Qty"),
            "fieldname": "net_sale_qty",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Net Sale AMT."),
            "fieldname": "net_sale_amount",
            "fieldtype": "Currency",
            "width": 140
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
            "label": _("Balance Qty"),
            "fieldname": "balance_qty",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Balance AMT."),
            "fieldname": "balance_value",
            "fieldtype": "Currency",
            "width": 120

        }
    ]

    return columns


def get_conditions_first(filters):
    conditions = []
    if filters.get("item_code"):
        conditions.append(f"AND sii.item_code = %(item_code)s")
    if filters.get("item_group"):
        conditions.append(f"AND sii.item_group = %(item_group)s")
    return " ".join(conditions)


def get_conditions_second(filters):
    conditions = []
    if filters.get("item_code"):
        conditions.append(f"AND sle.item_code = %(item_code)s")
    if filters.get("item_group"):
        conditions.append(f"AND item.item_group = %(item_group)s")
    return " ".join(conditions)


def get_data(filters):
    data = []
    conditions_first = get_conditions_first(filters)
    conditions_second = get_conditions_second(filters)

    bonus_query = f"""
        SELECT 
            sii.item_code,
            sii.rate AS rate,
            sii.brand,
            SUM(sii.qty) AS bonus
        FROM `tabSales Invoice` AS si, `tabSales Invoice Item` AS sii
        WHERE
            si.docstatus = 1
            AND si.is_return = 0
            AND si.posting_date >= '{filters.get('from_date')}'
            AND si.posting_date <= '{filters.get('to_date')}'
            AND si.name = sii.parent
            AND sii.rate = 0
           {conditions_first}
        GROUP BY sii.item_code
        """
    bonus_result = frappe.db.sql(bonus_query, filters, as_dict=1)

    stock_balance_query = f"""
    SELECT 
        sle.item_code,
        item.item_name,
        item.item_group,
        AVG(sle.incoming_rate) AS trade_price,
        SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Purchase Invoice' AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) AS in_qty,
        (SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Purchase Invoice' AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) * AVG(sle.incoming_rate)) AS received_amount,
        SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Sales Invoice' AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) AS return_qty,
        (SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Sales Invoice' AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) * AVG(sle.incoming_rate)) AS return_amount,
        SUM(CASE WHEN sle.posting_date < '{filters.get('from_date')}' THEN sle.actual_qty ELSE 0 END) AS opening_qty,
        (SUM(CASE WHEN sle.posting_date < '{filters.get('from_date')}' THEN sle.actual_qty ELSE 0 END) * AVG(sle.incoming_rate)) AS open_qty_amount,
        (SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Purchase Invoice' AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) + SUM(CASE WHEN sle.posting_date < '{filters.get('from_date')}' THEN sle.actual_qty ELSE 0 END)) AS total_qty,
        ABS(SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Sales Invoice' AND sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END)) AS out_qty,
         (((SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Purchase Invoice' AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) + SUM(CASE WHEN sle.posting_date < '{filters.get('from_date')}' THEN sle.actual_qty ELSE 0 END)) + SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Sales Invoice' AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END))-ABS(SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Sales Invoice' AND sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END)))  AS balance_qty,
         ((((SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Purchase Invoice' AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) + SUM(CASE WHEN sle.posting_date < '{filters.get('from_date')}' THEN sle.actual_qty ELSE 0 END)) + SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Sales Invoice' AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END))-ABS(SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Sales Invoice' AND sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END)))*AVG(sle.incoming_rate)) AS balance_value
         
    FROM `tabStock Ledger Entry` AS sle, `tabItem` AS item
    WHERE
        sle.is_cancelled = 0
        AND item.name = sle.item_code
        {conditions_second}
    GROUP BY sle.item_code
    """


    stock_balance_result = frappe.db.sql(stock_balance_query, filters, as_dict=1)
    # getting bonus
    for item_second in stock_balance_result:
        for item_first in bonus_result:
            if item_second["item_code"] == item_first["item_code"]:
                item_second["bonus"] = item_first["bonus"]
                item_second["bonus_amount"] = Decimal(item_first["bonus"]) * Decimal(item_second["trade_price"])
                item_second["sale_qty"] = Decimal(item_second["out_qty"]) - Decimal(item_first["bonus"])
                item_second["brand"] = item_first["brand"]
                item_second["net_sale_qty"] = Decimal(item_second["sale_qty"]) - Decimal(item_second["return_qty"])
                item_second["net_sale_amount"] = (item_second["net_sale_qty"] if item_second["net_sale_qty"] > 0 else 0) * item_second["trade_price"]
                break
        else:
            item_second["bonus"] = 0
    # end
    data.extend(stock_balance_result)
    return data
