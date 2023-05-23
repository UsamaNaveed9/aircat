// Copyright (c) 2023, Pukat and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Vehicle Budget Summary"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.month_start()
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.month_end()
		},
		{
			"fieldname": "vehicle",
			"label": __("Vehicle"),
			"fieldtype": "Link",
			"options": "Vehicle"
		},
		{
			"fieldname": "vehicle_budget",
			"label": __("Vehicle Budget"),
			"fieldtype": "Link",
			"options": "Vehicle Budget"
		}
	]
};
