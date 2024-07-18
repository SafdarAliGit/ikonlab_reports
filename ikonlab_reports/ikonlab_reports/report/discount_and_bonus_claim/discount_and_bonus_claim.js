// Copyright (c) 2024, Safdar Ali and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Discount And Bonus Claim"] = {
    "filters": [
        {
            label: __("From Date"),
            fieldname: "from_date",
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            reqd: 1
        },
        {
            label: __("To Date"),
            fieldname: "to_date",
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        }
    ]
};
