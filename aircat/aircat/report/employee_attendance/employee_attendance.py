# Copyright (c) 2023, Ameer Muavia Shah and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from datetime import datetime, timedelta


def execute(filters=None):
	if not filters:
		filters = {}
	columns, data = [], []
	columns = get_columns()
	conditions = get_conditions(filters)
	data = get_results(filters,conditions)
	return columns, data

def get_conditions(filters):
	conds = ""
	conds += " and ec.employee = %(employee)s " if filters.get("employee") else ""
	conds += " and DATE(ec.time) between %(from_date)s and %(to_date)s " if filters.get("from_date") and filters.get("to_date") else ""
	return conds


def get_results(filters,conditions):

	results = frappe.db.sql(f"""
							SELECT DATE(time) AS date, DAYNAME(DATE(time)) AS day_name,
									TIME(MIN(CASE WHEN log_type = 'IN' THEN time END)) AS morning_in,
									CASE WHEN COUNT(CASE WHEN log_type = 'IN' THEN 1 END) > 1
										THEN TIME(MAX(CASE WHEN log_type = 'IN' THEN time END))
									END AS afternoon_in,
									TIME((SELECT MIN(time) FROM `tabEmployee Checkin` WHERE log_type = 'OUT' and DATE(time) = DATE(ec.time) and employee = ec.employee)) AS morning_out,
									CASE WHEN COUNT(CASE WHEN log_type = 'OUT' THEN 1 END) > 1
										THEN TIME(MAX(CASE WHEN log_type = 'OUT' THEN time END))
									END AS afternoon_out
							FROM
								`tabEmployee Checkin` ec
							WHERE
								ec.log_type IN ('IN', 'OUT')
								and ec.docstatus < 2 
								{conditions}
							GROUP BY
								ec.employee, date
							""",filters,as_dict=1)
	for result in results:
		status = frappe.db.get_value("Attendance",{"attendance_date":result.date,"employee":filters.get("employee")},"status")
		if status and status == "Present":
			result["days"] = 1
		elif status and status == "Half Day":
			result["days"] = 0.5
		else:
			result["days"] = 0


		result["late_entry"] = "00:00:00"
		result.date = result.date.strftime("%d-%m-%y")
		afternoon_hours = morning_hours = 0
		if result.shift:
			start_time = frappe.db.get_value("Shift Type",result.shift,"start_time")
			if start_time:
				result["start_time"] = start_time
				if result.morning_in:
					if result.morning_in > start_time:
						entry_delay = result.morning_in - start_time
						seconds = entry_delay.total_seconds()
						hours = seconds // 3600  # Calculate the total number of hours
						minutes = (seconds % 3600) // 60  # Calculate the remaining minutes
						remaining_seconds = seconds % 60
						total_minutes = hours * 60 + minutes
						if total_minutes > 1:
							result["late_entry"] = f"{int(hours)}:{int(minutes)}:{round(int(remaining_seconds),2)}"
		if result.morning_in and result.morning_out:
			morning_hours = result.morning_out - result.morning_in
		if result.afternoon_in and result.afternoon_out:
			afternoon_hours = result.afternoon_out - result.afternoon_in
		elif result.morning_in and result.morning_out and not result.afternoon_in and result.afternoon_out:
			morning_hours = result.afternoon_out - result.morning_in
		
		if morning_hours and afternoon_hours:
			result["total_working_hours"] = morning_hours + afternoon_hours
		else:
			result["total_working_hours"] = morning_hours
		if result.overtime_hours and result.total_working_hours:
			result["actual_working_hours"] = result["total_working_hours"] + result.overtime_hours
		elif result.overtime_hours and not result.total_working_hours:
			result["actual_working_hours"] = result.overtime_hours
		else:
			result["actual_working_hours"] = result["total_working_hours"]
		
		if result.morning_in:
			result.morning_in = str(result.morning_in).split(".")[0]
		if result.afternoon_in:
			result.afternoon_in = str(result.afternoon_in).split(".")[0]
		if result.morning_out:
			result.morning_out = str(result.morning_out).split(".")[0]
		if result.afternoon_out:
			result.afternoon_out = str(result.afternoon_out).split(".")[0]


	return results
    

def get_columns():

	columns = [
		{
			'fieldname': 'date',
			'label': _('Date'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 100
			
		},
		{
			'fieldname': 'day_name',
			'label': _('Day Name'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 100
		},
		{
			'fieldname': 'morning_in',
			'label': _('Morning In'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 150
		},
		{
			'fieldname': 'morning_out',
			'label': _('Morning Out'),
			'fieldtype': 'Time',
			'align': 'left',
			'width': 150
		},
		{
			'fieldname': 'afternoon_in',
			'label': _('Afternoon In'),
			'fieldtype': 'Time',
			'align': 'left',
			'width': 150
		},
		{
			'fieldname': 'afternoon_out',
			'label': _('Afternoon Out'),
			'fieldtype': 'Time',
			'align': 'left',
			'width': 150
		},
		{
			'fieldname': 'total_working_hours',
			'label': _('Working Hours'),
			'fieldtype': 'Time',
			'align': 'left',
			'width': 150
		},
		{
			'fieldname': 'days',
			'label': _('Days'),
			'fieldtype': 'float',
			'align': 'left',
			'width': 75
		},
		
	]
	return columns

