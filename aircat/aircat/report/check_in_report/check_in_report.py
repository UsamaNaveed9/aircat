# Copyright (c) 2023, Pukat and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}
    columns, data = [], []
    conditions = get_conditions(filters)
    columns = get_columns()
    data = get_data(filters, conditions)
    return columns, data

def get_conditions(filters):
    conds = ""
    conds += " and employee = %(employee)s " if filters.get("employee") else ""
    conds += " and date between %(from_date)s and %(to_date)s " if filters.get("from_date") and filters.get("to_date") else ""
    return conds

def get_data(filters, conditions):
    data = frappe.db.sql(f"""
        SELECT 
            name,
            employee_name,
            log_type,
            date,
            TIME_FORMAT(time,'%%h:%%i %%p') as time,
            designation,
            device_id,
            officein_address
        FROM `tabEmployee Checkin`
        WHERE 1 = 1  
        {conditions}
    """, filters, as_dict=1)

    return data

def get_columns():
    columns = [
        {
            'fieldname': 'name',
            'label': _('Employee'),
            'fieldtype': 'Data',
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
            'width': 130
        },
        {
            'fieldname': 'log_type',
            'label': _('Log Type'),
            'fieldtype': 'Data',
            'align': 'left',
            'width': 130
        },
        {
            'fieldname': 'time',
            'label': _('Time'),
            'fieldtype': 'Data',
            'align': 'left',
            'width': 130
        },
        {
            'fieldname': 'designation',
            'label': _('Designation'),
            'fieldtype': 'Data',
            'align': 'left',
            'width': 130
        },
        {
            'fieldname': 'device_id',
            'label': _('Location/Device ID'),
            'fieldtype': 'Data',
            'align': 'left',
            'width': 200
        },
        {
            'fieldname': 'officein_address',
            'label': _('Officein Address'),
            'fieldtype': 'Data',
            'align': 'left',
            'width': 250
        }
    ]

    return columns