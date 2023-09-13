# Copyright (c) 2023, Pukat and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.data import getdate

class AdditionalSalaryEarningTool(Document):
	def on_submit(self):
		if not self.additional_salry:
			frappe.throw(f"Please add Additional Salary details in the given table below.")
		for row in self.additional_salry:
			if not row.salary_component or not row.amount or not row.payroll_year or not row.payroll_month:
				frappe.throw(f"Please add the mandatory field in the table below.")

			else:
				payroll_date = getdate(f"{row.payroll_month} {row.payroll_year}-28")
				addition_salary = frappe.get_doc({
					"doctype": "Additional Salary",
					"company": self.company,
					"employee": self.employee,
					"salary_component": row.salary_component,
					"salary_component_type": row.salary_component_type,
					"please_specify":row.please_specify,
					"phone_bill":row.phone_bill,
					"payroll_date":payroll_date,
					"amount":row.amount,
					"ref_doctype":"Additional Salary Earning Tool",
					"ref_docname":self.name,
				})
				addition_salary.flags.ignore_permissions = True
				addition_salary.insert()
				addition_salary.submit()
		frappe.msgprint(f"""Additional Salary records have been successfully created.""",alert=True)