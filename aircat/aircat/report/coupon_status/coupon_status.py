# Copyright (c) 2023, Pukat and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters=None):
	return [
		{
			"fieldname": "booklet",
			"label": _("BookLet"),
			"fieldtype": "Data",
			"width": 170,
		},
		{
			"fieldname": "coupon_issue",
			"label": _("Coupon Issue"),
			"fieldtype": "Link",
			"options": "Coupon Issue",
			"width": 170,
		},
		{
			"fieldname": "date_of_issue",
			"label": _("Date of Issue"),
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"fieldname": "date_of_use",
			"label": _("Date of Use"),
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"fieldname": "issue_serial_number",
			"label": _("Issue Serial Number"),
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"fieldname": "status",
			"label": _("Status"),
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"fieldname": "driver",
			"label": _("Driver"),
			"fieldtype": "Data",
			"width": 120,
		},
		{
			"fieldname": "issued_amount",
			"label": _("Issued Amount"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "alter_amount",
			"label": _("Alter Amount"),
			"fieldtype": "Currency",
			"width": 120,
		},

	]

def get_data(filters=None):
	data = []
	if not filters.vehicle:
		vehicle_list = frappe.db.get_list('Vehicle', pluck='name')
	else:
		vehicle_list = []
		vehicle_list.append(filters.vehicle)

	grand_issued_amt = grand_alter_amt = 0.0	
	for row in vehicle_list:
		condition = ""
		if filters.booklet:
			condition += "and booklet = '{0}'".format(filters.booklet)
		if filters.status:
				condition += "and status = '{0}'".format(filters.status)
		entries = frappe.db.sql("""select name as coupon_issue,booklet, vehicle, date_of_issue, date_of_use, issue_serial_number, driver, status,issued_amount, alter_amount
								from `tabCoupon Issue` where date_of_issue >= '{0}' and date_of_issue <= '{1}' and date_of_use >= '{0}' and date_of_use <= '{1}' 
								and vehicle = '{2}' {3}
								group by name""".format(filters.from_date,filters.to_date,row,condition),as_dict=1)
		if entries:
			total_issued_amt = total_alter_amt = 0.0
			for entry in entries:
				total_issued_amt += entry['issued_amount']
				total_alter_amt += entry['alter_amount']
			data.append({'booklet': row , 'issued_amount': total_issued_amt, 'alter_amount': total_alter_amt, 'indent': 0 })
			for entry in entries:
				entry.update({'indent': 1})
				data.append(entry)		
	for row in data:
		if row['indent'] == 0:
			grand_issued_amt += row['issued_amount']
			grand_alter_amt += row['alter_amount']
	data.append({'driver': 'Grand Total', 'issued_amount': grand_issued_amt, 'alter_amount': grand_alter_amt, 'indent': 0})			
	return data
