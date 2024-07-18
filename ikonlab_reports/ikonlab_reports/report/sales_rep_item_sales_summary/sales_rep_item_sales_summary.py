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
            "label": _("Sale Qty"),
            "fieldname": "sale_qty",
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
            "label": _("Bonus"),
            "fieldname": "bonus",
            "fieldtype": "Float",
            "width": 100
        },

        {
            "label": _("Net Qty"),
            "fieldname": "net_qty",
            "fieldtype": "Float",
            "width": 100

        },
        {
            "label": _("Sale Amount"),
            "fieldname": "sale_amount",
            "fieldtype": "Currency",
            "width": 200
        }

    ]

    return columns


def get_conditions_first(filters):
    conditions = []
    if filters.get("item_code"):
        conditions.append(f"AND sii.item_code = %(item_code)s")
    if filters.get("item_group"):
        conditions.append(f"AND sii.item_group = %(item_group)s")
    if filters.get("from_date"):
        conditions.append(f"AND si.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append(f"AND si.posting_date <= %(to_date)s")
    if filters.get("sales_person_name"):
        conditions.append(f"AND si.sales_person_name = %(sales_person_name)s")
    return " ".join(conditions)


def get_data(filters):
    data = []
    conditions_first = get_conditions_first(filters)

    sales_query = f"""
        SELECT 
            sii.item_code,
            sii.brand,
            SUM(sii.qty) AS sale_qty,
            ABS(SUM(CASE WHEN sii.qty < 0 THEN sii.qty ELSE 0 END)) AS return_qty,
            SUM(CASE WHEN sii.rate = 0 THEN sii.qty ELSE 0 END) AS bonus,
            (SUM(sii.qty) -  ABS(SUM(CASE WHEN sii.qty < 0 THEN sii.qty ELSE 0 END))) AS net_qty ,
            SUM(sii.amount) AS sale_amount           
        FROM `tabSales Invoice` si
        LEFT JOIN `tabSales Invoice Item` sii ON si.name = sii.parent
        WHERE
            si.docstatus = 1
           {conditions_first}
        GROUP BY sii.item_code
    """
    sales_result = frappe.db.sql(sales_query, filters, as_dict=1)
    data.extend(sales_result)
    return data
