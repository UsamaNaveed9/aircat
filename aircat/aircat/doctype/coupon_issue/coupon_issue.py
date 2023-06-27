# Copyright (c) 2023, Pukat and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from frappe.model.document import Document

class CouponIssue(Document):
	def before_submit(self):
		if self.booklet:
			booklet_doc = frappe.get_doc('BookLet',self.booklet)
			booklet_doc.issued_serial_number = self.issue_serial_number
			booklet_doc.save()
			
			# if booklet_doc.issued_serial_number == 0:
			# 	booklet_doc.issued_serial_number = self.issue_serial_number
			# 	booklet_doc.save()
			# else:
			# 	if self.issue_serial_number <= booklet_doc.issued_serial_number:
			# 		frappe.throw(_("The Issued Serial Number already used"))
			# 	else:
			# 		booklet_doc.issued_serial_number = self.issue_serial_number
			# 		booklet_doc.save()


			
