# Copyright (c) 2023, smb and contributors
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
			"fieldname": "vehicle",
			"label": _("Vehicle"),
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"fieldname": "budget_amount",
			"label": _("Budget_amount"),
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"fieldname": "coupon_amount",
			"label": _("Coupon Amount"),
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"fieldname": "m_amount",
			"label": _("Maintenance Amount"),
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"fieldname": "total_amount",
			"label": _("Total Amount"),
			"fieldtype": "Currency",
			"width": 150,
		},
		{
			"fieldname": "variance",
			"label": _("Variance"),
			"fieldtype": "Currency",
			"width": 120,
		},
		{
			"fieldname": "variance_ptg",
			"label": _("Variance %"),
			"fieldtype": "Float",
			"width": 120,
		},
	]

def get_data(filters=None):
	data = []
	if not filters.vehicle_budget:
		filterss = {
			"from_date": filters.from_date,
			"to_date": filters.to_date,
		}

		vb_list = frappe.get_list("Vehicle Budget", filters=filterss, pluck='name')
	else:
		vb_list = []
		vb_list.append(filters.vehicle_budget)
	
	for row in vb_list:
		condition = ""
		if filters.vehicle:
			condition += "and vehicles = '{0}'".format(filters.vehicle)
			
		entries = frappe.db.sql("""select vehicles as vehicle,budget_amount from `tabVehicles` where parent = '{0}' {1}
									group by vehicles""".format(row,condition),as_dict=1)

		main_list = []
		for en in entries:
			main = frappe.db.sql("""select vl.license_plate as vehicle, (sum(vs.expense_amount) + vl.price) as m_amount from `tabVehicle Log` as vl join `tabVehicle Service` as vs where vs.parent = vl.name
									and vl.date >= '{0}' and vl.date <= '{1}' and vl.license_plate = '{2}' """.format(filters.from_date,filters.to_date,en.vehicle),as_dict=1)							
			for m in main:
				en["m_amount"] = m.m_amount
				main_list.append(m)

		coupon_list = []
		for en in entries:
			coup = frappe.db.sql("""select vehicle,sum(issued_amount) as coupon_amount from `tabCoupon Issue` 
									where date_of_issue >= '{0}' and date_of_issue <= '{1}' and vehicle = '{2}' """.format(filters.from_date,filters.to_date,en.vehicle),as_dict=1)							
			for c in coup:
				en["coupon_amount"] = c.coupon_amount
				en["total_amount"] = en['coupon_amount'] + en['m_amount']
				en["variance"] = en['budget_amount'] - en['total_amount']
				en["variance_ptg"] = en['total_amount']/en['budget_amount'] * 100

				coupon_list.append(c)		
	
		if entries:
			total_budget = total_coupon = total_maintenance = total_amt = total_variance = total_vptg = 0.0
			for entry in entries:
				total_budget += entry['budget_amount']
				total_coupon += entry['coupon_amount']
				total_maintenance += entry['m_amount']
				total_amt += entry['total_amount']
				total_variance = total_budget - total_amt
				total_vptg = total_amt/total_budget * 100
	
			data.append({'vehicle': row, 'budget_amount': total_budget , 'coupon_amount': total_coupon, 'm_amount': total_maintenance, 'total_amount': total_amt, 'variance': total_variance, 'variance_ptg': total_vptg, 'indent': 0 })
			for entry in entries:
				entry.update({'indent': 1})
				data.append(entry)
	return data

