import frappe
from hrms.hr.utils import validate_active_employee
from frappe.utils import (
	flt,
	rounded,
)

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

from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip

class customSalary(SalarySlip):
	# def validate(self):
	# 	self.status = self.get_status()
	# 	validate_active_employee(self.employee)
	# 	self.validate_dates()
	# 	self.check_existing()
	# 	if not self.salary_slip_based_on_timesheet:
	# 		self.get_date_details()

	# 	if not (len(self.get("earnings")) or len(self.get("deductions"))):
	# 		# get details from salary structure
	# 		self.get_emp_and_working_day_details()
	# 	else:
	# 		self.get_working_days_details(lwp=self.leave_without_pay)

	# 	self.calculate_net_pay()
	# 	self.compute_year_to_date()
	# 	self.compute_month_to_date()
	# 	self.compute_component_wise_year_to_date()
	# 	self.add_leave_balances()

	# 	if frappe.db.get_single_value("Payroll Settings", "max_working_hours_against_timesheet"):
	# 		max_working_hours = frappe.db.get_single_value(
	# 			"Payroll Settings", "max_working_hours_against_timesheet"
	# 		)
	# 		if self.salary_slip_based_on_timesheet and (self.total_working_hours > int(max_working_hours)):
	# 			frappe.msgprint(
	# 				_("Total working hours should not be greater than max working hours {0}").format(
	# 					max_working_hours
	# 				),
	# 				alert=True,
	# 			)

	def set_net_pay(self):
		self.total_deduction = self.get_component_totals("deductions")
		self.base_total_deduction = flt(
			flt(self.total_deduction) * flt(self.exchange_rate), self.precision("base_total_deduction")
		)
		self.gross_pay = self.get_component_totals("earnings")
		self.net_pay = flt(self.gross_pay) - (flt(self.total_deduction) + flt(self.total_loan_repayment))
		self.rounded_total = rounded(self.net_pay)
		self.base_net_pay = flt(
			flt(self.net_pay) * flt(self.exchange_rate), self.precision("base_net_pay")
		)
		self.base_rounded_total = flt(rounded(self.base_net_pay), self.precision("base_net_pay"))
		if self.hour_rate:
			self.base_hour_rate = flt(
				flt(self.hour_rate) * flt(self.exchange_rate), self.precision("base_hour_rate")
			)
		self.set_net_total_in_words()