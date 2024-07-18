from decimal import Decimal

import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {
            "label": "<b>Inv#.</b>",
            "fieldname": "inv_no",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 150
        },
        {
            "label": "<b>Date</b>",
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": "<b>Party</b>",
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150
        },
        {
            "label": "<b>Item</b>",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "label": "<b>Qty</b>",
            "fieldname": "qty",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>Bonus</b>",
            "fieldname": "bonus",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": "<b>TP</b>",
            "fieldname": "tp",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "<b>Disc.%</b>",
            "fieldname": "disc_percent",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "<b>Amount</b>",
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 120
        },

        {
            "label": "<b>Claim/BONUS</b>",
            "fieldname": "claim_amount_bonus",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "<b>Claim/DISCOUNT</b>",
            "fieldname": "claim_amount_discount",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "<b>Claim Amount</b>",
            "fieldname": "claim_amount",
            "fieldtype": "Currency",
            "width": 120
        }

    ]
    return columns


def get_conditions(filters):
    conditions = []
    if filters.get("from_date"):
        conditions.append(f"inv.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append(f"inv.posting_date <= %(to_date)s")
    return " AND ".join(conditions)


def get_data(filters):
    data = []
    query = """
    SELECT 
        inv.name AS inv_no,
        inv.posting_date,
        inv.customer,
        item.item_code,
        CASE WHEN item.rate > 0 THEN item.qty ELSE 0 END AS qty,
        CASE WHEN item.rate = 0 THEN item.qty ELSE 0 END AS bonus,
        item.tp,
        item.disc_percent,
        (item.tp * (CASE WHEN item.rate > 0 THEN item.qty ELSE 0 END)) AS amount,
        (item.tp * (CASE WHEN item.rate = 0 THEN item.qty ELSE 0 END))  AS claim_amount_bonus,
        (CASE WHEN item.disc_percent > 0 THEN (item.tp * (CASE WHEN item.rate > 0 THEN item.qty ELSE 0 END))*(item.disc_percent/100) ELSE 0 END)  AS claim_amount_discount,
        ((item.tp * (CASE WHEN item.rate = 0 THEN item.qty ELSE 0 END)) + (CASE WHEN item.disc_percent > 0 THEN (item.tp * (CASE WHEN item.rate > 0 THEN item.qty ELSE 0 END))*(item.disc_percent/100) ELSE 0 END)) AS claim_amount
    FROM 
        `tabSales Invoice` AS inv, `tabSales Invoice Item` AS item
    WHERE 
        item.parent = inv.name 
        AND
        inv.is_return = 0 
        AND 
        inv.docstatus = 1
        AND
        {conditions} 
    ORDER BY
        inv.name
    """.format(conditions=get_conditions(filters))

    query_result = frappe.db.sql(query, filters, as_dict=1)

    # Brand Wise Data Summarization and Appending Summary Row
    # current_brand = None
    # brand_data = []  # Collects data for each brand
    # brand_sum = {"amount": 0, "claim_amount": 0}  # Track sums for each brand
    #
    # for record in query_result:
    #     # Convert to Decimal and handle None values
    #     amount = Decimal(record.get('amount', 0) or 0)
    #     claim_amount = Decimal(record.get('claim_amount', 0) or 0)
    #
    #     # Calculate gross profit for the current record and round to 4 decimal places
    #
    #     # Check if we're still processing the same brand
    #     if current_brand is None:
    #         # First record, set the current brand
    #         current_brand = record['inv_no']
    #     elif record['inv_no'] != current_brand:
    #         # We've hit a new brand, time to insert the summary for the previous brand
    #         brand_data.append({
    #             "inv_no": "TOTAL",
    #             "amount": f"{brand_sum['amount']:.4f}",
    #             "claim_amount": f"{brand_sum['claim_amount']:.4f}"
    #         })
    #         # Reset the sums for the new brand
    #         current_brand = record['inv_no']
    #         brand_sum = {"amount": 0, "claim_amount": 0}
    #
    #     # Update the sums with the current record
    #     brand_sum["amount"] += amount
    #     brand_sum["claim_amount"] += claim_amount
    #
    #     # Append the current record to brand_data
    #     brand_data.append(record)
    #
    # # After looping through all records, insert a summary for the last brand
    # if current_brand is not None:
    #     brand_data.append({
    #         "inv_no": "TOTAL",
    #         "amount": f"{brand_sum['amount']:.4f}",
    #         "claim_amount": f"{brand_sum['claim_amount']:.4f}"
    #     })
    #
    # # Append brand_data to data
    # data.extend(brand_data)

    # TO REMOVE DUPLICATES
    keys_to_check = ['inv_no', 'posting_date', 'customer']
    seen_values = []

    for entry in query_result:
        key_values = tuple(entry[key] for key in keys_to_check)

        if key_values in seen_values:
            for key in keys_to_check:
                entry[key] = None
        else:
            seen_values.append(key_values)

    # END
    data.extend(query_result)
    return data
