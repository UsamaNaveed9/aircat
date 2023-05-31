import frappe
from frappe.utils.password import get_decrypted_password
from frappe.utils import today, get_first_day, get_last_day, getdate

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
			if from_date and to_date and not (getdate(to_date) < getdate(from_date)):
				if not frappe.db.exists("Leave Application", {"employee": employee, "docstatus": ('<', 2),"to_date": ('>=', from_date),"from_date":('<=', to_date)}):
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
					message = "Leave Application already applied between these dates"
					return message
			else:
				message = "To date cannot be before from date"
				return message	
		else:
			message = "Leaves Not Allocated"
			return message

@frappe.whitelist()
def requisition_request(args):
	for i in args:
		current_date = today()
		req = frappe.get_doc({
					"doctype": "Requisition",
					"employee": i.get("employee"),
					"posting_date": current_date,
					"description": i.get("description"),
					"items_details": i.get("items_details")
				})
		req.save(ignore_permissions=True)
	
		message = "Requisition Request Submitted successfully"
		return message


@frappe.whitelist()
def update_personal_info(args):
	for i in args:
		employee_id = i.get("employee")
		if frappe.db.exists("Employee", {"name": employee_id}):
			doc = frappe.get_doc("Employee", employee_id)
			doc.cell_number = i.get("mobile_no")
			doc.personal_email = i.get("personal_email")
			doc.current_address = i.get("current_address")
			doc.current_accommodation_type = i.get("current_address_type")
			doc.permanent_address = i.get("permanent_address")
			doc.permanent_accommodation_type = i.get("permanent_address_type")
			doc.save(ignore_permissions=True)

			message = "Record Updated successfully"
			return message
		else:
			message = "Employee Not Exist"
			return message					


@frappe.whitelist()
def overtime_entry(args):
	for i in args:
		employee_id = i.get("employee")
		from_time = i.get("from_time")
		to_time = i.get("to_time")
		date = i.get("date")
		if frappe.db.exists("Employee", {"name": employee_id}):
			if not frappe.db.exists("Overtime", {"employee": employee_id,"from_time": from_time,"to_time":to_time,"date":date}):
				overtime = frappe.get_doc({
							"doctype": "Overtime",
							"employee": i.get("employee"),
							"date": i.get("date"),
							"from_time": i.get("from_time"),
							"to_time": i.get("to_time"),
							"total_hrs": i.get("total_hrs"),
							"purpose_of_overtime": i.get("purpose_of_overtime")
						})
				overtime.save(ignore_permissions=True)

				message = "Overtime record entered successfully"
				return message		
			
			else:
				message = "Overtime record already exit of same date and time"
				return message
		else:
			message = "Employee Not Exist"
			return message

@frappe.whitelist()
def driver_checkin_out(args):
	for i in args:
		log_type = i.get("log_type")
		employee = i.get("employee")
		date = i.get("date")
		
		if frappe.db.exists("Driver CheckIn-Out", {"employee": employee, "date": date}):
			last_doc = frappe.get_last_doc('Driver CheckIn-Out', filters={"employee": employee, "date": date})
		
			if log_type == "IN":
				if log_type == "IN" and last_doc and last_doc.log_type == "OUT":
					i['doctype'] = 'Driver CheckIn-Out'
					doc = frappe.get_doc(i)
					doc.save(ignore_permissions=True)
					if doc.name:
						message = "Driver CheckIN Record Entered successfully"
						return message
				else:
					message = "First CheckOut and then CheckIn"
					return message
			elif log_type == "OUT":	
				if log_type == "OUT" and last_doc and last_doc.log_type == "IN":
					i['doctype'] = 'Driver CheckIn-Out'
					doc = frappe.get_doc(i)
					doc.save(ignore_permissions=True)
					if doc.name:
						message = "Driver CheckOut Record Entered successfully"
						return message
				else:
					message = "First CheckIn and then CheckOut"
					return message
		elif log_type == "OUT":
			i['doctype'] = 'Driver CheckIn-Out'
			doc = frappe.get_doc(i)
			doc.save(ignore_permissions=True)
			if doc.name:
				message = "Driver CheckOut Record Entered successfully"
				return message
		else:
			message = "First CheckOut and Then CheckIn"
			return message


@frappe.whitelist()
def attendance_list(employee,month_start_date=None,month_end_date=None):
	if not month_start_date and not month_end_date:
		current_date = today()
		start_date = get_first_day(current_date)
		end_date = get_last_day(current_date)

		sql_query = """
					SELECT `name`,`employee`,`employee_name`, `attendance_date`, `status`
					FROM `tabAttendance`
					WHERE `attendance_date` BETWEEN %(start_date)s AND %(end_date)s
					AND `employee` = %(employee)s
					"""

		# Prepare the query parameters
		query_params = {
			'start_date': start_date,
			'end_date': end_date,
			'employee': employee
		}

		# Execute the SQL query
		attendance_records = frappe.db.sql(sql_query, query_params, as_dict=True)
	else:
		start_date = month_start_date
		end_date = month_end_date

		sql_query = """
					SELECT `name`,`employee`,`employee_name`, `attendance_date`, `status`
					FROM `tabAttendance`
					WHERE `attendance_date` BETWEEN %(start_date)s AND %(end_date)s
					AND `employee` = %(employee)s
					"""

		# Prepare the query parameters
		query_params = {
			'start_date': start_date,
			'end_date': end_date,
			'employee': employee
		}

		# Execute the SQL query
		attendance_records = frappe.db.sql(sql_query, query_params, as_dict=True)

	if attendance_records:			  
		return attendance_records
	else:
		message = "Attendance Records Does not exist"
		return message

@frappe.whitelist()
def overtime_list(employee,month_start_date=None,month_end_date=None):
	if not month_start_date and not month_end_date:
		current_date = today()
		start_date = get_first_day(current_date)
		end_date = get_last_day(current_date)

		sql_query = """
					SELECT `name`,`employee`,`employee_name`, `date`, `status`, `from_time`, `to_time`, `total_hrs`,`purpose_of_overtime`
					FROM `tabOvertime`
					WHERE `date` BETWEEN %(start_date)s AND %(end_date)s
					AND `employee` = %(employee)s
					"""

		# Prepare the query parameters
		query_params = {
			'start_date': start_date,
			'end_date': end_date,
			'employee': employee
		}

		# Execute the SQL query
		overtime_records = frappe.db.sql(sql_query, query_params, as_dict=True)
	else:
		start_date = month_start_date
		end_date = month_end_date

		sql_query = """
					SELECT `name`,`employee`,`employee_name`, `date`, `status`, `from_time`, `to_time`, `total_hrs`,`purpose_of_overtime`
					FROM `tabOvertime`
					WHERE `date` BETWEEN %(start_date)s AND %(end_date)s
					AND `employee` = %(employee)s
					"""

		# Prepare the query parameters
		query_params = {
			'start_date': start_date,
			'end_date': end_date,
			'employee': employee
		}

		# Execute the SQL query
		overtime_records = frappe.db.sql(sql_query, query_params, as_dict=True)

	if overtime_records:			  
		return overtime_records
	else:
		message = "Overtime Records Does not exist"
		return message

@frappe.whitelist()
def requisition_list(employee,month_start_date=None,month_end_date=None):
	if not month_start_date and not month_end_date:
		current_date = today()
		start_date = get_first_day(current_date)
		end_date = get_last_day(current_date)

		sql_query = """
					SELECT `name`,`employee`,`employee_name`, `posting_date`, `description`
					FROM `tabRequisition`
					WHERE `posting_date` BETWEEN %(start_date)s AND %(end_date)s
					AND `employee` = %(employee)s
					"""

		# Prepare the query parameters
		query_params = {
			'start_date': start_date,
			'end_date': end_date,
			'employee': employee
		}

		# Execute the SQL query
		requisition_records = frappe.db.sql(sql_query, query_params, as_dict=True)
	else:
		start_date = month_start_date
		end_date = month_end_date

		sql_query = """
					SELECT `name`,`employee`,`employee_name`, `posting_date`, `description`
					FROM `tabRequisition`
					WHERE `posting_date` BETWEEN %(start_date)s AND %(end_date)s
					AND `employee` = %(employee)s
					"""

		# Prepare the query parameters
		query_params = {
			'start_date': start_date,
			'end_date': end_date,
			'employee': employee
		}

		# Execute the SQL query
		requisition_records = frappe.db.sql(sql_query, query_params, as_dict=True)

	if requisition_records:
		for rr in requisition_records:
			sql_query = """
					SELECT `item_description`,`quantity`
					FROM `tabRequisition Details`
					WHERE `parent` = %(parent)s
					"""

			# Prepare the query parameters
			query_params = {
				'parent': rr.name
			}

			# Execute the SQL query
			item_details = frappe.db.sql(sql_query, query_params, as_dict=True)

			rr["items"] = item_details

		return requisition_records
	else:
		message = "Requisition Records Does not exist"
		return message

@frappe.whitelist()
def salary_slip_details(employee):
	sql_query = """
				SELECT `name`,`employee`,`employee_name`, `posting_date`,`start_date`,`end_date`,`total_working_days`,`absent_days`,
							`payment_days`,`gross_pay`,`total_deduction`,`net_pay`
				FROM `tabSalary Slip`
				WHERE `employee` = %(employee)s AND `docstatus` = 1
				"""

	# Prepare the query parameters
	query_params = {
		'employee': employee
	}

	# Execute the SQL query
	slip_records = frappe.db.sql(sql_query, query_params, as_dict=True)

	if slip_records:
		for sl in slip_records:
			sql_query = """
					SELECT `salary_component`,`day_amount`,`amount`
					FROM `tabSalary Detail`
					WHERE `parent` = %(parent)s
					"""

			# Prepare the query parameters
			query_params = {
				'parent': sl.name
			}

			# Execute the SQL query
			salary_components = frappe.db.sql(sql_query, query_params, as_dict=True)

			sl["components"] = salary_components

		return slip_records
	else:
		message = "Salary Slip Records Does not exist"
		return message