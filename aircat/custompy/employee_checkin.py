from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import json
from frappe import _, msgprint

@frappe.whitelist()
def mark_attendance(employee, date, time, checkin_doc):
	attendance = frappe.get_doc({
			"doctype": "Attendance",
			"employee": employee,
			"attendance_date": date,
			"in_time": time,
			"status": "Present"
		})
	attendance.save(ignore_permissions=True)
	attendance.submit()
	if attendance.name:
		ch_doc = frappe.get_doc("Employee Checkin", checkin_doc)
		ch_doc.attendance = attendance.name
		ch_doc.save(ignore_permissions=True)



@frappe.whitelist()
def update_time(self,method):
	if self.attendance:
		attend_doc = frappe.get_doc("Attendance", self.attendance)
		if attend_doc.morning_in_record == self.name:
			attend_doc.in_time = self.time
			attend_doc.save(ignore_permissions=True)
		elif attend_doc.morning_out_record == self.name:
			attend_doc.out_time = self.time
			attend_doc.save(ignore_permissions=True)
		elif attend_doc.afternoon_in_record == self.name:
			attend_doc.afternoon_in_time = self.time
			attend_doc.save(ignore_permissions=True)
		elif attend_doc.afternoon_out_record == self.name:
			attend_doc.afternoon_out_time = self.time
			attend_doc.save(ignore_permissions=True)		
