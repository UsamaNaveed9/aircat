// Copyright (c) 2023, Pukat and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Coupon Status"] = {
	"filters": [
		{
			"fieldname": "booklet",
			"label": __("BookLet"),
			"fieldtype": "Link",
			"options": "BookLet"
		},
		{
			"fieldname": "vehicle",
			"label": __("Vehicle"),
			"fieldtype": "Link",
			"options": "Vehicle"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "Issued\nInvoiced"
		}
	]
};
