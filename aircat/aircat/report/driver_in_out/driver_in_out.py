# Copyright (c) 2023, Pukat and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	conditions = get_conditions(filters)
	data = get_results(filters,conditions)
	return columns, data


def get_columns():
	return [
		
		{
			'fieldname': 'date',
			'label': _('Date'),
			'fieldtype': 'Date',
			'align': 'left',
			'width': 130
		},
		{
			'fieldname': 'employee_name',
			'label': _('Employee Name'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 200
		},
		{
			'fieldname': 'check_out',
			'label': _('Check Out'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 90
		},
		{
			'fieldname': 'out_time',
			'label': _('Out Time'),
			'fieldtype': 'Time',
			'align': 'left',
			'width': 110
		},
		{
			'fieldname': 'out_address',
			'label': _('Out Address'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 275
		},
		{
			'fieldname': 'check_in',
			'label': _('Check In'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 90
		},
		{
			'fieldname': 'in_time',
			'label': _('In Time'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 110
		},
		{
			'fieldname': 'in_address',
			'label': _('In Address'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 275
		},
		]


def get_conditions(filters):
	conds = ""
	conds += " and c_out.employee = %(employee)s " if filters.get("employee") else ""
	conds += " and c_out.date between %(from_date)s and %(to_date)s " if filters.get("from_date") and filters.get("to_date") else ""
	return conds


def get_results(filters,conditions):
	results = frappe.db.sql(f"""
								SELECT
									c_out.date AS date,
									c_out.employee_name AS employee_name,
									c_out.log_type AS check_out,
									c_out.time AS out_time,
									c_out.address AS out_address,
									c_in.log_type AS check_in,
									c_in.time AS in_time,
									c_in.address AS in_address
								FROM
									`tabDriver CheckIn-Out` AS c_out
								JOIN
									`tabDriver CheckIn-Out` AS c_in ON c_out.date = c_in.date
										AND c_out.employee = c_in.employee
										AND c_out.log_type = 'Out'
										AND c_in.log_type = 'In'
										AND c_out.time < c_in.time
								LEFT JOIN
									`tabDriver CheckIn-Out` AS c_in2 ON c_out.date = c_in2.date
										AND c_out.employee = c_in2.employee
										AND c_in2.log_type = 'In'
										AND c_out.time < c_in2.time
										AND c_in2.time < c_in.time
								WHERE
									c_in2.log_type IS NULL
									{conditions}
								""",filters,as_dict=1)
	for result in results:
		result.date = result.date.strftime("%d-%m-%y")
		if result.out_time:
			result.out_time = str(result.out_time).split(".")[0]
		if result.in_time:
			result.in_time = str(result.in_time).split(".")[0]
	return results

