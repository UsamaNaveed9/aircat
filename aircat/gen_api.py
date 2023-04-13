import frappe

@frappe.whitelist()
def get_employee_master():
	employees = frappe.db.sql('''select name,employee_name,gender,status,department,designation,branch,grade,final_confirmation_date,
							employment_type,place_of_birth,race,citizenship,ic_details,ic_color,religion,bank_name,bank_ac_no,
							tap_no,scp_no,marital_status,blood_group,passport_number,cell_number,personal_email,company_email,
							prefered_contact_email,prefered_email,current_address,permanent_address,person_to_be_contacted,emergency_phone_number,
							relation from `tabEmployee`; ''',as_dict=1 )
				  
	return employees

@frappe.whitelist()
def login(company_email):
	if frappe.db.exists("Employee", {"company_email": company_email}):
		employee_data = frappe.db.sql('''select name,employee_name,gender,status,company_email,cell_number
							from `tabEmployee` where status = "Active" and company_email=%s; ''',(company_email),as_dict=1 )
		
		return employee_data					
	else:
		message = "Invalid Email"
		return message


@frappe.whitelist()
def employee_checkin(args):
	for i in args:
		log_type = i.get("log_type")
		employee = i.get("employee")
		date = i.get("date")
		if log_type == "IN":
			if log_type == "IN" and not frappe.db.exists("Employee Checkin", {"employee": employee, "date": date, "log_type": "IN"}):
				i['doctype'] = 'Employee Checkin'
				doc = frappe.get_doc(i)
				doc.save()
				if doc.name:
					message = "Record Entered successfully"
					return message
			else:
				message = "CheckIn Record Exist Already"
				return message
		elif log_type == "OUT":
			if log_type == "OUT" and frappe.db.exists("Employee Checkin", {"employee": employee, "date": date, "log_type": "IN"}):
				if not frappe.db.exists("Employee Checkin", {"employee": employee, "date": date, "log_type": "OUT"}):
					i['doctype'] = 'Employee Checkin'
					doc = frappe.get_doc(i)
					doc.save()
					if doc.name:
						message = "Record Entered successfully"
						return message
				else:
					message = "CheckOut Record Exist Already"
				return message			
			else:
				message = "CheckIn Record Doesn't Exist"
				return message	


