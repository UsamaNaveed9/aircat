# Copyright (c) 2023, Pukat and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from frappe.model.document import Document

class CouponInvoiced(Document):
	def before_submit(self):
		if self.coupon_issues:
			for cpn in self.coupon_issues:
				coupon_iss_doc = frappe.get_doc('Coupon Issue',cpn.coupon_issue)
				coupon_iss_doc.alter_amount = cpn.alter_amount
				coupon_iss_doc.date_of_invoice = self.date_of_invoice
				coupon_iss_doc.status = "Invoiced"
				coupon_iss_doc.save()
