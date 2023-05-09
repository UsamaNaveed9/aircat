import frappe

@frappe.whitelist()
def get_salary_components(employee, salary_str, payment_days):

	earnings = frappe.db.sql('''select salary_component,day_amount,fixed_amount,amount from `tabSalary Detail` 
				where `tabSalary Detail`.parent = "{0}" and `tabSalary Detail`.parentfield = "earnings"'''.format(salary_str),as_dict = 1)

	deductions = frappe.db.sql('''select salary_component,day_amount,fixed_amount,amount from `tabSalary Detail` 
				where `tabSalary Detail`.parent = "{0}" and `tabSalary Detail`.parentfield = "deductions"'''.format(salary_str),as_dict = 1)

	for e in earnings:
		if e.fixed_amount == 0:
			e.amount = float(e.day_amount) * float(payment_days)

	for d in deductions:
		if d.fixed_amount == 0:
			d.amount = float(d.day_amount) * float(payment_days)		
	return earnings,deductions