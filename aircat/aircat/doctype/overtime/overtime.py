# Copyright (c) 2023, Pukat and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.data import getdate

from datetime import datetime, timedelta

class Overtime(Document):
	# def validate(self):
	# 	# only once for updating add_salaries
	# 	current_date = datetime.now()
	# 	current_month_start = current_date.replace(day=1)
	# 	current_month_end = (current_month_start.replace(month=current_month_start.month + 1) - timedelta(days=1)).date()

	# 	# Get Additional Salary records with overtime component and 0 amount for the current month
	# 	missing_overtime_salaries = frappe.get_all(
	# 		"Additional Salary",
	# 		filters={
	# 			"salary_component": "Overtime",
	# 			"amount": 0,
	# 			"payroll_date": [">=", current_month_start],
	# 			"payroll_date": ["<=", current_month_end],
	# 				"docstatus":1
	# 		},
	# 		fields=["name", "employee", "company"]
	# 	)

	# 	for record in missing_overtime_salaries:
	# 		employee = record["employee"]
	# 		company = record["company"]
	# 		record_name = record["name"]

	# 		# Fetch overtime records for the same employee in the current month
	# 		overtime_records = frappe.get_all(
	# 			"Overtime",
	# 			filters={
	# 				"employee": employee,
	# 				"date": [">=", current_month_start],
	# 				"date": ["<=", current_month_end],
	# 				"docstatus":1
	# 			},
	# 			fields=["date", "total_hrs"]
	# 		)

	# 		if not overtime_records:
	# 			continue

	# 		# Get daily salary from the latest Salary Structure Assignment
	# 		latest_assignment = frappe.get_all(
	# 			"Salary Structure Assignment",
	# 			filters={"employee": employee, "docstatus": 1},
	# 			order_by="creation DESC",
	# 			limit=1
	# 		)
			
	# 		if latest_assignment:
	# 			daily_salary = frappe.db.get_value("Salary Structure Assignment",
	# 												latest_assignment[0]["name"], "daily_salary")

	# 			# Calculate total overtime hours and the corresponding amount
	# 			total_overtime_hours = sum([overtime["total_hrs"] for overtime in overtime_records])
	# 			overtime_salary = ((daily_salary / 8) * 1.5) * total_overtime_hours

	# 			# Update Additional Salary record with the calculated overtime amount
	# 			frappe.db.set_value("Additional Salary", record_name, "amount", overtime_salary)

	# 			# Update the child table in the Additional Salary document
	# 			additional_salary_doc = frappe.get_doc("Additional Salary", record_name)
	# 			additional_salary_doc.set("overtime_breakup", [])

	# 			for overtime in overtime_records:
	# 				overtime_date = overtime["date"]
	# 				overtime_hours = overtime["total_hrs"]

	# 				overtime_breakup = {
	# 					"basic_per_hour": daily_salary,
	# 					"overtime_hours": overtime_hours,
	# 					"amount": ((daily_salary / 8) * 1.5) * overtime_hours,
	# 					"overtime_link": overtime_date,  # Change this to the appropriate field
	# 				}
	# 				additional_salary_doc.append("overtime_breakup", overtime_breakup)

	# 			additional_salary_doc.save()

	def on_submit(self):
		latest_assignment = frappe.get_all(
			"Salary Structure Assignment",
			filters={"employee": self.employee, "docstatus": 1},
			order_by="creation DESC",
			limit=1
		)

		if latest_assignment:
			daily_salary = frappe.db.get_value("Salary Structure Assignment",
												latest_assignment[0], "daily_salary")

			company = frappe.db.get_value("Employee",
											self.employee, "company")

			# Calculate overtime salary
			overtime_salary = ((daily_salary / 8) * 1.5) * self.total_hrs

			# Convert self.date to a datetime object
			overtime_date = datetime.strptime(self.date, "%Y-%m-%d")

			# Get month start and end dates
			month_start = overtime_date.replace(day=1)
			next_month_start = month_start.replace(month=month_start.month + 1, day=1)
			month_end = next_month_start - timedelta(days=1)

			# Check if Additional Salary record exists within the month range
			existing_additional_salary = frappe.db.exists(
				"Additional Salary",
				{
					"employee": self.employee,
					"salary_component": "Overtime",
					"payroll_date": [">=", month_start],
					"payroll_date": ["<=", month_end],
				}
			)

			if existing_additional_salary:
				frappe.msgprint("Additional Salary record already exists for this employee in the current month.")
				add_salary = frappe.db.get_value(
				"Additional Salary",
				{
					"employee": self.employee,
					"salary_component": "Overtime",
					"payroll_date": [">=", month_start],
					"payroll_date": ["<=", month_end],
				},
				"name"
				)
				# Perform your action here
				amount = frappe.db.sql(f"select ifnull(amount,0) from `tabAdditional Salary` where name = '{add_salary}'")[0][0]
				new_amount = float(amount) + float(overtime_salary)
				frappe.db.set_value("Additional Salary",add_salary,"amount",new_amount)
				# Append a new row to the child table in the existing "Additional Salary" document
				add_salary = frappe.get_doc("Additional Salary", add_salary)
				add_salary.append("overtime_breakup", {
					"basic_per_hour": daily_salary,
					"overtime_hours": self.total_hrs,
					"amount": overtime_salary,
					"overtime_link": self.name,
				})
				add_salary.save()
			else:
				addition_salary = frappe.get_doc({
					"doctype": "Additional Salary",
					"company": company,
					"employee": self.employee,
					"salary_component": "Overtime",
					"salary_component_type": "Earning",
					"against_overtime": 1,
					"payroll_date": self.date,
					"amount": overtime_salary,
					"overtime_breakup": [
						{
								"basic_per_hour": daily_salary,
								"overtime_hours": self.total_hrs,
								"amount": overtime_salary,
								"overtime_link": self.name,
						}
					],
				})
				addition_salary.flags.ignore_permissions = True
				addition_salary.insert()
				addition_salary.submit()
		else:
			frappe.throw(f"Please assign a Salary Structure to the employee '{self.employee}'.")


	def on_cancel(self):
		latest_assignment = frappe.get_all(
			"Salary Structure Assignment",
			filters={"employee": self.employee, "docstatus": 1},
			order_by="creation DESC",
			limit=1
		)
		daily_salary = frappe.db.get_value("Salary Structure Assignment",
											latest_assignment[0], "daily_salary")

		# Calculate overtime salary
		overtime_salary = ((daily_salary / 8) * 1.5) * self.total_hrs
		# Convert self.date to a datetime object
		overtime_date = datetime.strptime(str(self.date), "%Y-%m-%d")

		# Get month start and end dates
		month_start = overtime_date.replace(day=1)
		next_month_start = month_start.replace(month=month_start.month + 1, day=1)
		month_end = next_month_start - timedelta(days=1)

		# Find the corresponding Additional Salary entry
		additional_salary_entry = frappe.get_value(
				"Additional Salary",
				{
					"employee": self.employee,
					"salary_component": "Overtime",
					"payroll_date": [">=", month_start],
					"payroll_date": ["<=", month_end],
				},
				"name"
				)

		if additional_salary_entry:
			additional_salary_doc = frappe.get_doc("Additional Salary", additional_salary_entry)
			overtime_salary = ((daily_salary / 8) * 1.5) * self.total_hrs

			# If there's only one row and it corresponds to the canceled overtime, cancel the entire Additional Salary
			if len(additional_salary_doc.overtime_breakup) == 1 and additional_salary_doc.overtime_breakup[0].overtime_link == self.name:
				additional_salary_doc.cancel()
				frappe.msgprint("Canceled entire Additional Salary document.")
			else:
				# Remove the corresponding row from the child table and adjust the amount
                # Use query builder to delete the row based on overtime_link
				frappe.db.sql(f"DELETE FROM `tabAdd Salary Overtime` WHERE parent=%s AND overtime_link=%s",
								(additional_salary_doc.name, self.name))

				# Adjust the amount
				new_amount = additional_salary_doc.amount - overtime_salary
				frappe.db.set_value("Additional Salary", additional_salary_entry, "amount", new_amount)
				frappe.msgprint("Removed row from the child table and adjusted amount.")
