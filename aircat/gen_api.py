import frappe
from frappe.utils.password import get_decrypted_password
from frappe.utils import today

@frappe.whitelist()
def get_employee_master():
	employees = frappe.db.sql('''select name,employee_name,gender,status,department,designation,branch,grade,final_confirmation_date,
							employment_type,place_of_birth,race,citizenship,ic_details,ic_color,religion,bank_name,bank_ac_no,
							tap_no,scp_no,marital_status,blood_group,passport_number,cell_number,personal_email,company_email,
							prefered_contact_email,prefered_email,current_address,permanent_address,person_to_be_contacted,emergency_phone_number,
							relation from `tabEmployee`; ''',as_dict=1 )
				  
	return employees

@frappe.whitelist()
def login(company_email,password):
	if frappe.db.exists("Employee", {"company_email": company_email}):
		emp = frappe.db.sql('''select name,company_email,new_password
							from `tabEmployee` where status = "Active" and company_email=%s; ''',(company_email),as_dict=1 )
		for e in emp:					
			hash_password = e.new_password
			plain_text_password = get_decrypted_password("Employee", e.name, "new_password", hash_password)

		if plain_text_password == password:
			employee_data = frappe.db.sql('''select name,employee_name,gender,status,company_email,cell_number,shift_start_time,shift_end_time
								from `tabEmployee` where status = "Active" and company_email=%s; ''',(company_email),as_dict=1 )
		
			return employee_data

		else:
			message = "Invalid Credentials"
			return message				
	else:
		message = "Employee Not Exist on this Email"
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
					attendance = frappe.get_doc({
							"doctype": "Attendance",
							"employee": i.get("employee"),
							"attendance_date": i.get("date"),
							"status": "Present"
						})
					attendance.save(ignore_permissions=True)
					attendance.submit()

					doc.attendance = attendance.name
					doc.save(ignore_permissions=True)

					message = "Office IN and Attendance Entered successfully"
					return message
			else:
				message = "OfficeIn Record Exist Already"
				return message
		elif log_type == "OUT":
			if log_type == "OUT" and frappe.db.exists("Employee Checkin", {"employee": employee, "date": date, "log_type": "IN"}):
				if not frappe.db.exists("Employee Checkin", {"employee": employee, "date": date, "log_type": "OUT"}):
					i['doctype'] = 'Employee Checkin'
					doc = frappe.get_doc(i)
					doc.save()
					if doc.name:
						message = "Office Out Entered successfully"
						return message
				else:
					message = "Office Out Record Exist Already"
				return message			
			else:
				message = "OfficeIn Record Doesn't Exist"
				return message	

@frappe.whitelist()
def employee_allocated_leaves(employee_id):
	if frappe.db.exists("Employee", {"name": employee_id}):
		current_date = today()
		if frappe.db.exists("Leave Allocation",{"employee": employee_id,"docstatus": 1,"from_date": ('<=', current_date),"to_date": ('>=', current_date)}):
			record = frappe.db.sql("""SELECT employee, employee_name, department, leave_type, from_date, to_date, total_leaves_allocated FROM `tabLeave Allocation` WHERE employee=%s and docstatus = 1 and from_date <= %s
						and to_date >= %s""", (employee_id,current_date,current_date), as_dict=True)

			return record
		else:
			message = "Leaves Not Allocated"
			return message	
	else:
		message = "Employee Not Exist"
		return message

@frappe.whitelist()
def employee_leave_application(args):
	for i in args:
		employee = i.get("employee")
		from_date = i.get("from_date")
		to_date = i.get("to_date")
		if frappe.db.exists("Leave Allocation",{"employee": employee,"docstatus": 1,"from_date": ('<=', from_date),"to_date": ('>=', to_date)}):
			if not frappe.db.exists("Leave Application", {"employee": employee,"from_date": from_date,"to_date":to_date}):
				leave = frappe.get_doc({
							"doctype": "Leave Application",
							"employee": i.get("employee"),
							"leave_type": i.get("leave_type"),
							"from_date": i.get("from_date"),
							"to_date": i.get("to_date"),
							"half_day": i.get("half_day"),
							"description": i.get("description")
						})
				leave.save(ignore_permissions=True)

				message = "Leave Application is Applied"
				return message		
			
			else:
				message = "Leave Application already applied of these dates"
				return message
		else:
			message = "Leaves Not Allocated"
			return message		






