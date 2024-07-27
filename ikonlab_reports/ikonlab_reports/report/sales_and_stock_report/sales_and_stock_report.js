frappe.query_reports["Sales And Stock Report"] = {
    "filters": [

        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "width": "80",
            "reqd": 1,
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "width": "80",
            "reqd": 1,
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "item_group",
            "label": __("Item Group"),
            "fieldtype": "Link",
            "width": "80",
            "options": "Item Group"
        },
        {
            "fieldname": "item_code",
            "label": __("Item"),
            "fieldtype": "Link",
            "width": "80",
            "options": "Item",
            "get_query": function () {
                return {
                    query: "erpnext.controllers.queries.item_query",
                };
            }
        }

    ],

    "formatter": function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname == "out_qty" && data && data.out_qty > 0) {
            value = "<span style='color:red'>" + value + "</span>";
        } else if (column.fieldname == "in_qty" && data && data.in_qty > 0) {
            value = "<span style='color:green'>" + value + "</span>";
        }

        return value;
    }
};

