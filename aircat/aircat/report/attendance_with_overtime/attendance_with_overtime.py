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


# Query with time having values after .

# SELECT ec.employee,ec.employee_name, DATE(time) AS date, DAYNAME(DATE(time)) AS day_name,
# 		(SELECT default_shift FROM `tabEmployee` WHERE name = ec.employee) as shift,
# 		TIME(MIN(CASE WHEN log_type = 'IN' THEN time END)) AS morning_in,
# 		CASE WHEN COUNT(CASE WHEN log_type = 'IN' THEN 1 END) > 1
# 			THEN TIME(MAX(CASE WHEN log_type = 'IN' THEN time END))
# 		END AS afternoon_in,
# 		TIME((SELECT MIN(time) FROM `tabEmployee Checkin` WHERE log_type = 'OUT' and DATE(time) = DATE(ec.time) and employee = ec.employee)) AS morning_out,
# 		TIME((SELECT MAX(time) FROM `tabEmployee Checkin` WHERE log_type = 'OUT' and DATE(time) = DATE(ec.time) and employee = ec.employee)) AS afternoon_out,
# 		(SELECT from_time FROM `tabOvertime` WHERE employee = ec.employee and status = 'Approved' and date = Date(ec.time)) as overtime_in,
# 		(SELECT to_time FROM `tabOvertime` WHERE employee = ec.employee and status = 'Approved' and date = Date(ec.time)) as overtime_out,
# 		(SELECT purpose_of_overtime FROM `tabOvertime` WHERE employee = ec.employee and status = 'Approved' and date = Date(ec.time)) as overtime_purpose,
# (SELECT approver_suppervisor_ FROM `tabOvertime` WHERE employee = ec.employee AND status = 'Approved' AND date = DATE(ec.time)) AS supervisor,
# 		(SELECT authorize_person_name FROM `tabOvertime` WHERE employee = ec.employee and status = 'Approved' and date = Date(ec.time)) as authorizing_person,
# 		TIMEDIFF((SELECT to_time FROM `tabOvertime` WHERE employee = ec.employee and status = 'Approved' and date = Date(ec.time)),(SELECT from_time FROM `tabOvertime` WHERE employee = ec.employee and status = 'Approved' and date = Date(ec.time))) as overtime_hours
# FROM
# 	`tabEmployee Checkin` ec
# WHERE
# 	ec.log_type IN ('IN', 'OUT')
# 	and ec.docstatus < 2 
# 	{conditions}
# GROUP BY
# 	ec.employee, date

def get_results(filters,conditions):

	results = frappe.db.sql(f"""
							SELECT ec.employee,ec.employee_name, DATE(time) AS date, DAYNAME(DATE(time)) AS day_name,
									(SELECT default_shift FROM `tabEmployee` WHERE name = ec.employee) as shift,
									TIME(MIN(CASE WHEN log_type = 'IN' THEN time END)) AS morning_in,
									CASE WHEN COUNT(CASE WHEN log_type = 'IN' THEN 1 END) > 1
										THEN TIME(MAX(CASE WHEN log_type = 'IN' THEN time END))
									END AS afternoon_in,
									TIME((SELECT MIN(time) FROM `tabEmployee Checkin` WHERE log_type = 'OUT' and DATE(time) = DATE(ec.time) and employee = ec.employee)) AS morning_out,
									CASE WHEN COUNT(CASE WHEN log_type = 'OUT' THEN 1 END) > 1
										THEN TIME(MAX(CASE WHEN log_type = 'OUT' THEN time END))
									END AS afternoon_out,
									(SELECT from_time FROM `tabOvertime` WHERE employee = ec.employee and status = 'Approved' and date = Date(ec.time) and docstatus = 1 ORDER BY creation LIMIT 1) as overtime_in,
									(SELECT to_time FROM `tabOvertime` WHERE employee = ec.employee and status = 'Approved' and date = Date(ec.time) and docstatus = 1 ORDER BY creation LIMIT 1) as overtime_out,
									(SELECT purpose_of_overtime FROM `tabOvertime` WHERE employee = ec.employee and status = 'Approved' and date = Date(ec.time) and docstatus = 1 ORDER BY creation LIMIT 1) as overtime_purpose,
									(SELECT approver_suppervisor_ FROM `tabOvertime` WHERE employee = ec.employee AND status = 'Approved' AND date = DATE(ec.time) and docstatus = 1 ORDER BY creation LIMIT 1) AS supervisor,
									(SELECT authorize_person_name FROM `tabOvertime` WHERE employee = ec.employee and status = 'Approved' and date = Date(ec.time) and docstatus = 1 ORDER BY creation LIMIT 1) as authorizing_person,
									TIMEDIFF((SELECT to_time FROM `tabOvertime` WHERE employee = ec.employee and status = 'Approved' and date = Date(ec.time) and docstatus = 1 ORDER BY creation LIMIT 1),(SELECT from_time FROM `tabOvertime` WHERE employee = ec.employee and status = 'Approved' and date = Date(ec.time) and docstatus = 1 ORDER BY creation LIMIT 1)) as overtime_hours
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
		if result.overtime_in:
			result.overtime_in = str(result.overtime_in).split(".")[0]
		if result.morning_out:
			result.morning_out = str(result.morning_out).split(".")[0]
		if result.afternoon_out:
			result.afternoon_out = str(result.afternoon_out).split(".")[0]
		if result.overtime_out:
			result.overtime_out = str(result.overtime_out).split(".")[0]

	return results
    

def get_columns():

	columns = [
		{
			'fieldname': 'employee',
			'label': _('Employee'),
			'fieldtype': 'Link',
			'options': 'Employee',
			'align': 'left',
			'width': 200
		},
		{
			'fieldname': 'employee_name',
			'label': _('Employee Name'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 200
		},
		{
			'fieldname': 'date',
			'label': _('Date'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 100
			
		},
		{
			'fieldname': 'shift',
			'label': _('Shift'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 100
			
		},
		{
			'fieldname': 'start_time',
			'label': _('Start Time'),
			'fieldtype': 'Time',
			'align': 'left',
			'width': 100
			
		},
		{
			'fieldname': 'late_entry',
			'label': _('Late Entry'),
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
			'width': 100
		},
		{
			'fieldname': 'morning_out',
			'label': _('Morning Out'),
			'fieldtype': 'Time',
			'align': 'left',
			'width': 100
		},
		{
			'fieldname': 'afternoon_in',
			'label': _('Afternoon In'),
			'fieldtype': 'Time',
			'align': 'left',
			'width': 100
		},
		{
			'fieldname': 'afternoon_out',
			'label': _('Afternoon Out'),
			'fieldtype': 'Time',
			'align': 'left',
			'width': 100
		},
		{
			'fieldname': 'total_working_hours',
			'label': _('Working Hours'),
			'fieldtype': 'Time',
			'align': 'left',
			'width': 100
		},
		{
			'fieldname': 'overtime_in',
			'label': _('Overtime In'),
			'fieldtype': 'Time',
			'align': 'left',
			'width': 100
		},
		{
			'fieldname': 'overtime_out',
			'label': _('Overtime Out'),
			'fieldtype': 'Time',
			'align': 'left',
			'width': 100
		},
		{
			'fieldname': 'overtime_purpose',
			'label': _('Overtime Purpose'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 100
		},
		{
			'fieldname': 'supervisor',
			'label': _('Supervisor'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 100
		},
		{
			'fieldname': 'authorizing_person',
			'label': _('Authorized By'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 100
		},
		{
			'fieldname': 'overtime_hours',
			'label': _('Overtime Working Hours'),
			'fieldtype': 'Time',
			'align': 'left',
			'width': 100
		},
		{
			'fieldname': 'actual_working_hours',
			'label': _('Actual Working Hours'),
			'fieldtype': 'Time',
			'align': 'left',
			'width': 100
		}
		
	]
	return columns




# Old Query
			 							# MIN(CASE WHEN log_type = 'IN' THEN time END) AS morning_checkin,
										# CASE WHEN COUNT(CASE WHEN log_type = 'IN' THEN 1 END) > 1
										# 	THEN MAX(CASE WHEN log_type = 'IN' THEN time END)
										# END AS evening_checkin,
										# MIN(CASE WHEN log_type = 'OUT' THEN time END) AS morning_checkout,
										# MAX(CASE WHEN log_type = 'OUT' THEN time END) AS evening_checkout
			 

										# CASE WHEN COUNT(CASE WHEN log_type = 'IN' THEN 1 END) > 0
										# 	THEN MIN(CASE WHEN log_type = 'IN' THEN time END)
										# END AS morning_checkin,
										# CASE WHEN COUNT(CASE WHEN log_type = 'IN' THEN 1 END) > 0
										# 	THEN MAX(CASE WHEN log_type = 'IN' THEN time END)
										# END AS evening_checkin,
										# CASE WHEN COUNT(CASE WHEN log_type = 'OUT' THEN 1 END) > 0
										# 	THEN MIN(CASE WHEN log_type = 'OUT' THEN time END)
										# END AS morning_checkout,
										# CASE WHEN COUNT(CASE WHEN log_type = 'OUT' THEN 1 END) > 0
										# 	THEN MAX(CASE WHEN log_type = 'OUT' THEN time END)
										# END AS evening_checkout