# # Copyright (c) 2023, Pukat and contributors
# # For license information, please see license.txt


import frappe
from frappe import _
from datetime import datetime


def execute(filters=None):
	if not filters:
		filters = {}
	columns, data = [], []
	columns = get_columns()
	conditions = get_conditions(filters)
	data = get_data(filters,conditions)
	return columns, data


def get_conditions(filters):
	conds = ""
	conds += " and tabAttendance.employee = %(employee)s " if filters.get("employee") else ""
	conds += " and DATE(attendance_date) between %(from_date)s and %(to_date)s " if filters.get("from_date") and filters.get("to_date") else ""
	return conds


def get_data(filters, conditions):
    data = frappe.db.sql(f"""
        SELECT
            tabAttendance.employee,
            tabAttendance.employee_name,
            tabAttendance.attendance_date,
            DAYNAME(tabAttendance.attendance_date) AS day_of_week,
            TIME_FORMAT(tabAttendance.in_time, '%%h:%%i %%p') AS in_time,
            TIME_FORMAT(tabAttendance.out_time, '%%h:%%i %%p') AS out_time,
            TIME_FORMAT(tabAttendance.afternoon_in_time, '%%h:%%i %%p') AS time_afternoon_in,
            TIME_FORMAT(tabAttendance.afternoon_out_time, '%%h:%%i %%p') AS time_afternoon_out,
            TIME_FORMAT(TIMEDIFF(out_time, in_time), '%%H:%%i') AS total_time_morning,
            TIME_FORMAT(TIMEDIFF(afternoon_out_time, afternoon_in_time), '%%H:%%i') AS total_time_afternoon,
            IF(tabOvertime.employee IS NOT NULL,
                TIME_FORMAT(TIMEDIFF(to_time, from_time), '%%H:%%i'),
                '00:00'
            ) AS over_time,
            TIME_FORMAT(
                IFNULL(
                    ADDTIME(
                        TIMEDIFF(tabAttendance.out_time, tabAttendance.in_time),
                        TIMEDIFF(tabAttendance.afternoon_out_time, tabAttendance.afternoon_in_time)
                    ),
                    IFNULL(
                        TIMEDIFF(tabAttendance.out_time, tabAttendance.in_time),
                        TIMEDIFF(tabAttendance.afternoon_out_time, tabAttendance.afternoon_in_time)
                    )
                ),
                '%%H:%%i'
            ) AS total_work_time,
            TIME_FORMAT(
                ADDTIME(
                    ADDTIME(
                        IFNULL(TIMEDIFF(tabAttendance.out_time, tabAttendance.in_time), '00:00'),
                        IFNULL(TIMEDIFF(tabAttendance.afternoon_out_time, tabAttendance.afternoon_in_time), '00:00')
                    ),
                    IFNULL(TIMEDIFF(tabOvertime.to_time, tabOvertime.from_time), '00:00')
                ),
                '%%H:%%i'
            ) AS total_work_time_over
        FROM tabAttendance
        LEFT JOIN (
            SELECT employee, date, from_time, to_time
            FROM tabOvertime
            WHERE docstatus = 1
        ) AS tabOvertime
        ON tabAttendance.employee = tabOvertime.employee
        AND tabAttendance.attendance_date = tabOvertime.date
        WHERE tabAttendance.docstatus = 1
        {conditions}
    """, filters, as_dict=1)
    return data

def get_columns():

	columns = [
		{
			'fieldname': 'employee',
			'label': _('Employee'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 130
			
		},
		{
			'fieldname': 'employee_name',
			'label': _('Employee Name'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 130
		},
		{
			'fieldname': 'attendance_date',
			'label': _('Attendance Date'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 130
		},
		{
			'fieldname': 'day_of_week',
			'label': _('Day Of Week'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 130
		},
		{
			'fieldname': 'in_time',
			'label': _('Morning In'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 130
		},
		{
			'fieldname': 'out_time',
			'label': _('Morning Out'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 130
		},
		{
			'fieldname': 'time_afternoon_in',
			'label': _('Afternoon In'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 130
		},
		{
			'fieldname': 'time_afternoon_out',
			'label': _('Afternoon Out'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 130
		},
		{
			'fieldname': 'total_time_morning',
			'label': _('Total Morning Time'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 150
		},
		{
			'fieldname': 'total_time_afternoon',
			'label': _('Total Afternoon Time'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 150
		},
		{
			'fieldname': 'total_work_time',
			'label': _('Total Work Time'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 130
		},
		{
			'fieldname': 'over_time',
			'label': _('Over Time'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 130
		},
		{
			'fieldname': 'total_work_time_over',
			'label': _('Total Work Over Time'),
			'fieldtype': 'Data',
			'align': 'left',
			'width': 150
		},

	]
	return columns



# import frappe
# from frappe import _


# def execute(filters=None):
# 	if not filters:
# 		filters = {}
# 	columns, data = [], []
# 	columns = get_columns()
# 	conditions = get_conditions(filters)
# 	data = get_data(filters,conditions)
# 	return columns, data

# def get_conditions(filters):
# 	conds = ""
# 	conds += " AND tabAttendance.employee = %(employee)s " if filters.get("employee") else ""
# 	conds += " AND tabAttendance.attendance_date BETWEEN %(from_date)s AND %(to_date)s " if filters.get("from_date") and filters.get("to_date") else ""
# 	return conds

# def get_data(filters,conditions):
#     data = frappe.db.sql(f"""
#         SELECT
# 			tabAttendance.employee,
# 			tabAttendance.employee_name,
# 			tabAttendance.attendance_date,
# 			DAYNAME(tabAttendance.attendance_date) AS day_of_week,
# 			TIME_FORMAT(tabAttendance.in_time, '%%H:%%i') AS in_time,
# 			TIME_FORMAT(tabAttendance.out_time, '%%H:%%i') AS out_time,
# 			TIME_FORMAT(tabAttendance.afternoon_in_time, '%%H:%%i') AS time_afternoon_in,
# 			TIME_FORMAT(tabAttendance.afternoon_out_time, '%%H:%%i') AS time_afternoon_out,
# 			TIME_FORMAT(TIMEDIFF(out_time, in_time), '%%H:%%i') AS total_time_morning,
# 			TIME_FORMAT(TIMEDIFF(afternoon_out_time, afternoon_in_time), '%%H:%%i') AS total_time_afternoon,
# 			TIME_FORMAT(TIMEDIFF(to_time, from_time), '%%H:%%i') AS over_time,
# 			TIME_FORMAT(
# 					IFNULL(
# 						ADDTIME(TIMEDIFF(tabAttendance.out_time, tabAttendance.in_time), TIMEDIFF(tabAttendance.afternoon_out_time, tabAttendance.afternoon_in_time)),
# 						IFNULL(TIMEDIFF(tabAttendance.out_time, in_time), TIMEDIFF(tabAttendance.afternoon_out_time, tabAttendance.afternoon_in_time))
# 					),
# 					'%%H:%%i'
# 				) AS total_work_time,

# 			TIME_FORMAT(
# 					ADDTIME(
# 						ADDTIME(
# 							IFNULL(TIMEDIFF(tabAttendance.out_time, tabAttendance.in_time), '00:00'),
# 							IFNULL(TIMEDIFF(tabAttendance.afternoon_out_time, tabAttendance.afternoon_in_time), '00:00')
# 						),
# 						IFNULL(TIMEDIFF(tabOvertime.to_time, tabOvertime.from_time), '00:00')
# 					),
				

# 				'%%H:%%i'
# 			) AS total_work_time_over

# 			FROM tabAttendance
# 			RIGHT JOIN tabOvertime
# 			ON tabAttendance.employee=tabOvertime.employee
# 			WHERE tabOvertime.docstatus = 1
# 			AND tabAttendance.docstatus = 1
# 			AND tabOvertime.date = tabAttendance.attendance_date
# 			{conditions}
# 	""",filters,as_dict=1)

#     return data


# def get_columns():

# 	columns = [
# 		{
# 			'fieldname': 'employee',
# 			'label': _('Employee'),
# 			'fieldtype': 'Link',
# 			'options': 'Employee',
# 			'align': 'left',
# 			'width': 200
# 		},
# 		{
# 			'fieldname': 'employee_name',
# 			'label': _('Employee Name'),
# 			'fieldtype': 'Data',
# 			'align': 'left',
# 			'width': 200
# 		},
# 		{
# 			'fieldname': 'date',
# 			'label': _('Date'),
# 			'fieldtype': 'Data',
# 			'align': 'left',
# 			'width': 100
			
# 		},
# 		{
# 			'fieldname': 'shift',
# 			'label': _('Shift'),
# 			'fieldtype': 'Data',
# 			'align': 'left',
# 			'width': 100
			
# 		},
# 		{
# 			'fieldname': 'start_time',
# 			'label': _('Start Time'),
# 			'fieldtype': 'Time',
# 			'align': 'left',
# 			'width': 100
			
# 		},
# 		{
# 			'fieldname': 'late_entry',
# 			'label': _('Late Entry'),
# 			'fieldtype': 'Data',
# 			'align': 'left',
# 			'width': 100
			
# 		},
# 		{
# 			'fieldname': 'day_name',
# 			'label': _('Day Name'),
# 			'fieldtype': 'Data',
# 			'align': 'left',
# 			'width': 100
# 		},
# 		{
# 			'fieldname': 'morning_in',
# 			'label': _('Morning In'),
# 			'fieldtype': 'Data',
# 			'align': 'left',
# 			'width': 100
# 		},
# 		{
# 			'fieldname': 'morning_out',
# 			'label': _('Morning Out'),
# 			'fieldtype': 'Time',
# 			'align': 'left',
# 			'width': 100
# 		},
# 		{
# 			'fieldname': 'afternoon_in',
# 			'label': _('Afternoon In'),
# 			'fieldtype': 'Time',
# 			'align': 'left',
# 			'width': 100
# 		},
# 		{
# 			'fieldname': 'afternoon_out',
# 			'label': _('Afternoon Out'),
# 			'fieldtype': 'Time',
# 			'align': 'left',
# 			'width': 100
# 		},
# 		{
# 			'fieldname': 'total_working_hours',
# 			'label': _('Working Hours'),
# 			'fieldtype': 'Time',
# 			'align': 'left',
# 			'width': 100
# 		},
# 		{
# 			'fieldname': 'overtime_in',
# 			'label': _('Overtime In'),
# 			'fieldtype': 'Time',
# 			'align': 'left',
# 			'width': 100
# 		},
# 		{
# 			'fieldname': 'overtime_out',
# 			'label': _('Overtime Out'),
# 			'fieldtype': 'Time',
# 			'align': 'left',
# 			'width': 100
# 		},
# 		{
# 			'fieldname': 'overtime_purpose',
# 			'label': _('Overtime Purpose'),
# 			'fieldtype': 'Data',
# 			'align': 'left',
# 			'width': 100
# 		},
# 		{
# 			'fieldname': 'supervisor',
# 			'label': _('Supervisor'),
# 			'fieldtype': 'Data',
# 			'align': 'left',
# 			'width': 100
# 		},
# 		{
# 			'fieldname': 'authorizing_person',
# 			'label': _('Authorized By'),
# 			'fieldtype': 'Data',
# 			'align': 'left',
# 			'width': 100
# 		},
# 		{
# 			'fieldname': 'overtime_hours',
# 			'label': _('Overtime Working Hours'),
# 			'fieldtype': 'Time',
# 			'align': 'left',
# 			'width': 100
# 		},
# 		{
# 			'fieldname': 'actual_working_hours',
# 			'label': _('Actual Working Hours'),
# 			'fieldtype': 'Time',
# 			'align': 'left',
# 			'width': 100
# 		}
		
# 	]
# 	return columns



