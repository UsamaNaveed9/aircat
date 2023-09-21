import frappe
from hrms.hr.doctype.leave_allocation.leave_allocation import LeaveAllocation
from hrms.hr.utils import get_leave_period, set_employee_name


class customLeaveAllocation(LeaveAllocation):
	def validate(self):
		self.validate_period()
		self.validate_allocation_overlap()
		self.validate_lwp()
		set_employee_name(self)
		self.set_total_leaves_allocated()
		self.validate_leave_days_and_dates()

	def validate_lwp(self):
		if frappe.db.get_value("Leave Type", self.leave_type, "is_lwp") and self.leave_type != "Unpaid Leave":
			frappe.throw(
				_("Leave Type {0} cannot be allocated since it is leave without pay").format(self.leave_type)
			)