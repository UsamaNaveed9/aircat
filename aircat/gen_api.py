import frappe
from frappe.utils.password import get_decrypted_password
from frappe.utils import today, get_first_day, get_last_day, getdate
from datetime import date, timedelta, datetime
import requests
import json

@frappe.whitelist()
def get_employee_master():
	employees = frappe.db.sql('''select name,employee_name,gender,status,department,designation,branch,grade,final_confirmation_date,
							employment_type,place_of_birth,race,citizenship,ic_details,ic_color,religion,bank_name,bank_ac_no,
							tap_no,scp_no,marital_status,blood_group,passport_number,cell_number,personal_email,company_email,
							prefered_contact_email,prefered_email,current_address,permanent_address,person_to_be_contacted,emergency_phone_number,
							relation from `tabEmployee`; ''',as_dict=1 )
				  
	return employees

@frappe.whitelist()
def login(company_email,password,player_id=None):
	if frappe.db.exists("Employee", {"company_email": company_email}):
		emp = frappe.db.sql('''select name,company_email,new_password
							from `tabEmployee` where status = "Active" and company_email=%s; ''',(company_email),as_dict=1 )
		for e in emp:					
			hash_password = e.new_password
			plain_text_password = get_decrypted_password("Employee", e.name, "new_password", hash_password)

		if plain_text_password == password:
			employee_data = frappe.db.sql('''select name,employee_name,gender,status,company_email,cell_number,shift_start_time,shift_end_time,
											personal_email,current_address,current_accommodation_type,permanent_address,
											permanent_accommodation_type,image as image_link
								from `tabEmployee` where status = "Active" and company_email=%s; ''',(company_email),as_dict=1 )
			for row in employee_data:
				if row["image_link"]:
					row["image_link"] = "https://aircat.oneerp.com.my"+row["image_link"]

				row["error"] = False
				
				if player_id:
					doc = frappe.get_doc("Employee", row["name"] )
					doc.player_id = player_id
					doc.save(ignore_permissions=True)

			return employee_data

		else:
			response = [] 
			msg = {
				"error": True,
				"message": "Invalid Credentials"
			}
			response.append(msg)
			return response				
	else:
		response = [] 
		msg = {
			"error": True,
			"message": "Employee Not Exist on this Email"
		}
		response.append(msg)
		return response


@frappe.whitelist()
def employee_checkin(args):
	for i in args:
		log_type = i.get("log_type")
		employee = i.get("employee")
		date = i.get("date")

		count =	frappe.db.count("Employee Checkin",filters={"employee": employee, "date": date},debug=False)
		if count < 4:
			if frappe.db.exists("Employee Checkin", {"employee": employee, "date": date}):
				last_doc = frappe.get_last_doc('Employee Checkin', filters={"employee": employee, "date": date})
			
				if log_type == "IN":
					if log_type == "IN" and last_doc and last_doc.log_type == "OUT":
						i['doctype'] = 'Employee Checkin'
						doc = frappe.get_doc(i)
						doc.save(ignore_permissions=True)
						if doc.name:
							doc.attendance = last_doc.attendance
							doc.save(ignore_permissions=True)

							attend_doc = frappe.get_doc("Attendance", last_doc.attendance)
							attend_doc.afternoon_in_time = i.get("time")
							attend_doc.afternoon_in_record = doc.name
							attend_doc.afternoon_in_address = i.get("officein_address")
							attend_doc.save(ignore_permissions=True)

							response = [] 
							msg = {
								"error": False,
								"message": "Employee OfficeIn Record Entered successfully"
							}
							response.append(msg)
							return response
					else:
						response = [] 
						msg = {
							"error": True,
							"message": "First OfficeOut and then OfficeIn"
						}
						response.append(msg)
						return response
				elif log_type == "OUT":
					if log_type == "OUT" and last_doc and last_doc.log_type == "IN":
						i['doctype'] = 'Employee Checkin'
						doc = frappe.get_doc(i)
						doc.save(ignore_permissions=True)
						if doc.name:
							doc.attendance = last_doc.attendance
							doc.save(ignore_permissions=True)

							if count == 1:								
								attend_doc = frappe.get_doc("Attendance", last_doc.attendance)
								attend_doc.out_time = i.get("time")
								attend_doc.morning_out_record = doc.name
								attend_doc.morning_out_address = i.get("officein_address")
								attend_doc.save(ignore_permissions=True)
							elif count == 3:
								attend_doc = frappe.get_doc("Attendance", last_doc.attendance)
								attend_doc.afternoon_out_time = i.get("time")
								attend_doc.afternoon_out_record = doc.name
								attend_doc.afternoon_out_address = i.get("officein_address")
								attend_doc.save(ignore_permissions=True)


							response = [] 
							msg = {
								"error": False,
								"message": "Employee OfficeOut Record Entered successfully"
							}
							response.append(msg)

							emp_doc = frappe.get_doc('Employee', employee)
							players = []
							players.append(emp_doc.player_id)

							header = {"Accept": "application/json",
									"Authorization": "Basic MmFkMWNmYWYtMGJjNy00NmQ3LTlkNDItZTgyNTg0MjhjY2Yz",
									"Content-Type": "application/json"
									}

							payload = {"app_id": "6f3dd902-8546-45ac-922a-0d272d0d575b",
										#"included_segments": ["Subscribed Users"],
										"include_player_ids": players,
										"contents": {"en": "Have a great Lunch","es": "Spanish Message",},
										"name": "New",
										"data": {"url": "/home",}
									}
								
							requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
							
							return response
					else:
						response = [] 
						msg = {
							"error": True,
							"message": "First OfficeIn and then OfficeOut"
						}
						response.append(msg)
						return response
			elif log_type == "IN":
				i['doctype'] = 'Employee Checkin'
				doc = frappe.get_doc(i)
				doc.save(ignore_permissions=True)
				if doc.name:
						attendance = frappe.get_doc({
								"doctype": "Attendance",
								"employee": i.get("employee"),
								"attendance_date": i.get("date"),
								"in_time": i.get("time"),
								"morning_in_record": doc.name,
								"morning_in_address": i.get("officein_address"),
								"status": "Present"
							})
						attendance.save(ignore_permissions=True)
						attendance.submit()

						doc.attendance = attendance.name
						doc.save(ignore_permissions=True)

						response = [] 
						msg = {
							"error": False,
							"message": "Office IN and Attendance Entered successfully"
						}
						response.append(msg)
						return response
			else:
				response = [] 
				msg = {
					"error": True,
					"message": "First OfficeIn then OfficeIn"
				}
				response.append(msg)
				return response
		else:
			response = [] 
			msg = {
				"error": True,
				"message": "Meet the OfficeIn-Out Day Limit"
			}
			response.append(msg)
			return response



@frappe.whitelist()
def employee_allocated_leaves(employee_id):
	if frappe.db.exists("Employee", {"name": employee_id}):
		current_date = today()
		if frappe.db.exists("Leave Allocation",{"employee": employee_id,"docstatus": 1,"from_date": ('<=', current_date),"to_date": ('>=', current_date)}):
			record = frappe.db.sql("""SELECT employee, employee_name, department, leave_type, from_date, to_date, total_leaves_allocated FROM `tabLeave Allocation` WHERE employee=%s and docstatus = 1 and from_date <= %s
						and to_date >= %s""", (employee_id,current_date,current_date), as_dict=True)

			for row in record:
				row["error"] = False
			return record
		else:
			response = [] 
			msg = {
				"error": True,
				"message": "Leaves Not Allocated"
			}
			response.append(msg)
			return response	
	else:
		response = [] 
		msg = {
			"error": True,
			"message": "Employee Not Exist"
		}
		response.append(msg)
		return response

@frappe.whitelist()
def employee_leave_application(args):
	for i in args:
		employee = i.get("employee")
		from_date = i.get("from_date")
		to_date = i.get("to_date")
		leave_type = i.get("leave_type")
		if frappe.db.exists("Leave Allocation",{"employee": employee,"docstatus": 1,"from_date": ('<=', from_date),"to_date": ('>=', to_date)}):
			if from_date and to_date and not (getdate(to_date) < getdate(from_date)):
				if frappe.db.exists("Leave Type",{"name": leave_type}):
					if not frappe.db.exists("Attendance",{"employee": employee,"docstatus": ('<', 2),"attendance_date": ["between", [from_date, to_date]],},):
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

							response = [] 
							msg = {
								"error": False,
								"message": "Leave Application is Applied"
							}
							response.append(msg)
							return response
						else:
							response = [] 
							msg = {
								"error": True,
								"message": "Leave Application already applied between these dates"
							}
							response.append(msg)
							return response
					else:
							response = [] 
							msg = {
								"error": True,
								"message": "Attendance is already marked for this day"
							}
							response.append(msg)
							return response
				else:
					response = [] 
					msg = {
						"error": True,
						"message": "Leave Type: {0} is not allowed".format(leave_type)
					}
					response.append(msg)
					return response					
			else:
				response = [] 
				msg = {
					"error": True,
					"message": "To date cannot be before from date"
				}
				response.append(msg)
				return response
		else:
			response = [] 
			msg = {
				"error": True,
				"message": "Leaves Not Allocated"
			}
			response.append(msg)
			return response

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

		response = [] 
		msg = {
			"error": False,
			"message": "Requisition Request Submitted successfully"
		}
		response.append(msg)
		return response


@frappe.whitelist()
def update_personal_info(args):
	for i in args:
		employee_id = i.get("employee")
		if frappe.db.exists("Employee", {"name": employee_id}):
			doc = frappe.get_doc("Employee", employee_id)
			doc.cell_number = i.get("cell_number")
			doc.personal_email = i.get("personal_email")
			doc.current_address = i.get("current_address")
			doc.current_accommodation_type = i.get("current_address_type")
			doc.permanent_address = i.get("permanent_address")
			doc.permanent_accommodation_type = i.get("permanent_address_type")
			doc.save(ignore_permissions=True)

			response = [] 
			msg = {
				"error": False,
				"message": "Record Updated successfully"
			}
			response.append(msg)
			return response
		else:
			response = [] 
			msg = {
				"error": True,
				"message": "Employee Not Exist"
			}
			response.append(msg)
			return response					


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

				response = [] 
				msg = {
					"error": False,
					"message": "Overtime record entered successfully"
				}
				response.append(msg)
				return response
			else:
				response = [] 
				msg = {
					"error": True,
					"message": "Overtime record already exit of same date and time"
				}
				response.append(msg)
				return response
		else:
			response = [] 
			msg = {
				"error": True,
				"message": "Employee Not Exist"
			}
			response.append(msg)
			return response

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
						response = [] 
						msg = {
							"error": False,
							"message": "Driver CheckIN Record Entered successfully"
						}
						response.append(msg)
						return response
				else:
					response = [] 
					msg = {
						"error": True,
						"message": "First CheckOut and then CheckIn"
					}
					response.append(msg)
					return response
			elif log_type == "OUT":	
				if log_type == "OUT" and last_doc and last_doc.log_type == "IN":
					i['doctype'] = 'Driver CheckIn-Out'
					doc = frappe.get_doc(i)
					doc.save(ignore_permissions=True)
					if doc.name:
						response = [] 
						msg = {
							"error": False,
							"message": "Driver CheckOut Record Entered successfully"
						}
						response.append(msg)
						return response
				else:
					response = [] 
					msg = {
						"error": True,
						"message": "First CheckIn and then CheckOut"
					}
					response.append(msg)
					return response
		elif log_type == "OUT":
			i['doctype'] = 'Driver CheckIn-Out'
			doc = frappe.get_doc(i)
			doc.save(ignore_permissions=True)
			if doc.name:
				response = [] 
				msg = {
					"error": False,
					"message": "Driver CheckOut Record Entered successfully"
				}
				response.append(msg)
				return response
		else:
			response = [] 
			msg = {
				"error": True,
				"message": "First CheckOut and Then CheckIn"
			}
			response.append(msg)
			return response


@frappe.whitelist()
def attendance_list(employee,month_start_date=None,month_end_date=None):
	if not month_start_date and not month_end_date:
		current_date = today()
		start_date = get_first_day(current_date)
		end_date = get_last_day(current_date)

		sql_query = """
					SELECT `name`,`employee`,`employee_name`, `attendance_date`, `status`, `status_by_employee`, `status_by_hr`
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
		
		for row in attendance_records:
			sql_query = """
					SELECT `log_type`,`shift`,`time`, `device_id`, `officein_lat`,`officein_long`,`officein_address`,`officein_comment`
					FROM `tabEmployee Checkin`
					WHERE `date` = %(date)s
					AND `employee` = %(employee)s
					"""

			# Prepare the query parameters
			query_params = {
				'date': row["attendance_date"],
				'employee': row["employee"]
			}

			officein_records = frappe.db.sql(sql_query, query_params, as_dict=True)

			row["officein_out"] = officein_records


	else:
		start_date = month_start_date
		end_date = month_end_date

		sql_query = """
					SELECT `name`,`employee`,`employee_name`, `attendance_date`, `status`, `status_by_employee`, `status_by_hr`
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

		for row in attendance_records:
			sql_query = """
					SELECT `log_type`,`shift`,`time`, `device_id`, `officein_lat`,`officein_long`,`officein_address`,`officein_comment`
					FROM `tabEmployee Checkin`
					WHERE `date` = %(date)s
					AND `employee` = %(employee)s
					"""

			# Prepare the query parameters
			query_params = {
				'date': row["attendance_date"],
				'employee': row["employee"]
			}

			officein_records = frappe.db.sql(sql_query, query_params, as_dict=True)

			row["officein_out"] = officein_records

	if attendance_records:
		for row in attendance_records:
			row["error"] = False			  
		return attendance_records
	else:
		response = [] 
		msg = {
			"error": True,
			"message": "Attendance Records Does not exist"
		}
		response.append(msg)
		return response

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
		for row in overtime_records:
			row["error"] = False			  
		return overtime_records
	else:
		response = [] 
		msg = {
			"error": True,
			"message": "Overtime Records Does not exist"
		}
		response.append(msg)
		return response

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
			rr["error"] = False

		return requisition_records
	else:
		response = [] 
		msg = {
			"error": True,
			"message": "Requisition Records Does not exist"
		}
		response.append(msg)
		return response


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
			sl["error"] = False

		return slip_records
	else:
		response = [] 
		msg = {
			"error": True,
			"message": "Salary Slip Records Does not exist"
		}
		response.append(msg)
		return response


@frappe.whitelist()
def stats(employee,month_start_date=None,month_end_date=None):
	if not month_start_date and not month_end_date:
		current_date = today()
		start_date = get_first_day(current_date)
		end_date = get_last_day(current_date)

		def count_working_days(start_date, end_date):
			total_days = (end_date - start_date).days + 1
			working_days = 0

			for i in range(total_days):
				current_date = start_date + timedelta(days=i)
				if current_date.weekday() != 6:  # 6 represents Sunday (Monday is 0)
					working_days += 1

			return working_days

		total_working_days = count_working_days(start_date, end_date)

		sql_query = """
					SELECT count(name)
					FROM `tabAttendance`
					WHERE `attendance_date` BETWEEN %(start_date)s AND %(end_date)s
					AND `employee` = %(employee)s AND `status` = %(status)s AND docstatus = 1
					"""

		# Prepare the query parameters
		query_pr = {
			'start_date': start_date,
			'end_date': end_date,
			'employee': employee,
			'status': 'Present'
		}

		# Execute the SQL query
		present_days = frappe.db.sql(sql_query, query_pr)

		query_ab = {
			'start_date': start_date,
			'end_date': end_date,
			'employee': employee,
			'status': 'Absent'
		}

		absent_days = frappe.db.sql(sql_query, query_ab)

		query_le = {
			'start_date': start_date,
			'end_date': end_date,
			'employee': employee,
			'status': 'On Leave'
		}

		leave_days = frappe.db.sql(sql_query, query_ab)
	else:
		start_date = datetime.strptime(month_start_date, '%Y-%m-%d').date()
		end_date = datetime.strptime(month_end_date, '%Y-%m-%d').date()

		def count_working_days(start_date, end_date):
			total_days = (end_date - start_date).days + 1
			working_days = 0

			for i in range(total_days):
				current_date = start_date + timedelta(days=i)
				if current_date.weekday() != 6:  # 6 represents Sunday (Monday is 0)
					working_days += 1

			return working_days

		total_working_days = count_working_days(start_date, end_date)

		sql_query = """
					SELECT count(name)
					FROM `tabAttendance`
					WHERE `attendance_date` BETWEEN %(start_date)s AND %(end_date)s
					AND `employee` = %(employee)s AND `status` = %(status)s AND docstatus = 1
					"""

		# Prepare the query parameters
		query_pr = {
			'start_date': start_date,
			'end_date': end_date,
			'employee': employee,
			'status': 'Present'
		}

		# Execute the SQL query
		present_days = frappe.db.sql(sql_query, query_pr)

		query_ab = {
			'start_date': start_date,
			'end_date': end_date,
			'employee': employee,
			'status': 'Absent'
		}

		absent_days = frappe.db.sql(sql_query, query_ab)

		query_le = {
			'start_date': start_date,
			'end_date': end_date,
			'employee': employee,
			'status': 'On Leave'
		}

		leave_days = frappe.db.sql(sql_query, query_ab)

	response = []
	msg = {
		"error": False,
		"total_working_days": total_working_days,
		"present_days": present_days[0][0],
		"absent_days": absent_days[0][0],
		"leave_days": leave_days[0][0]
	}
	response.append(msg)
	return response


@frappe.whitelist()
def send_notification_toall():
	header = {"Accept": "application/json",
			  "Authorization": "Basic MmFkMWNmYWYtMGJjNy00NmQ3LTlkNDItZTgyNTg0MjhjY2Yz",
			  "Content-Type": "application/json"
			}

	payload = {"app_id": "6f3dd902-8546-45ac-922a-0d272d0d575b",
				"included_segments": ["Subscribed Users"],
				#"include_player_ids": players,
				"contents": {"en": "15mins more report to work","es": "Spanish Message",},
				"name": "New",
				"data": {"url": "/home",}
			}
		
	requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))

@frappe.whitelist()
def send_notification_after_eight():
	get_employees = frappe.db.get_list('Employee',
		filters={
			'status': 'Active'
		},
		fields=['name','player_id']
	)
	players = []
	current_date = today()
	for i in get_employees:
		if not frappe.db.exists("Attendance", {"employee": i.name, "attendance_date": current_date}):
			players.append(i.player_id)

	header = {"Accept": "application/json",
			  "Authorization": "Basic MmFkMWNmYWYtMGJjNy00NmQ3LTlkNDItZTgyNTg0MjhjY2Yz",
			  "Content-Type": "application/json"
			}

	payload = {"app_id": "6f3dd902-8546-45ac-922a-0d272d0d575b",
				# "included_segments": ["Subscribed Users"],
				"include_player_ids": players,
				"contents": {"en": "You are late for office IN","es": "Spanish Message",},
				"name": "New",
				"data": {"url": "/home",}
			}
		
	requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))

@frappe.whitelist()
def send_notification_after_eight15():
	get_employees = frappe.db.get_list('Employee',
		filters={
			'status': 'Active'
		},
		fields=['name','player_id']
	)
	players = []
	current_date = today()
	for i in get_employees:
		if not frappe.db.exists("Attendance", {"employee": i.name, "attendance_date": current_date}):
			players.append(i.player_id)
			attendance = frappe.get_doc({
							"doctype": "Attendance",
							"employee": i.employee,
							"attendance_date": current_date,
							"status": "Absent"
						})
			attendance.save(ignore_permissions=True)
			attendance.submit()


	header = {"Accept": "application/json",
			  "Authorization": "Basic MmFkMWNmYWYtMGJjNy00NmQ3LTlkNDItZTgyNTg0MjhjY2Yz",
			  "Content-Type": "application/json"
			}

	payload = {"app_id": "6f3dd902-8546-45ac-922a-0d272d0d575b",
				#"included_segments": ["Subscribed Users"],
				"include_player_ids": players,
				"contents": {"en": "You are absent today","es": "Spanish Message",},
				"name": "New",
				"data": {"url": "/home",}
			}
		
	requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))	

	


@frappe.whitelist()
def update_missing_overtime_amounts():
	current_date = datetime.now()
	current_month_start = current_date.replace(day=1)
	current_month_end = (current_month_start.replace(month=current_month_start.month + 1) - timedelta(days=1)).date()

	# Get Additional Salary records with overtime component and 0 amount for the current month
	missing_overtime_salaries = frappe.get_all(
		"Additional Salary",
		filters={
			"salary_component": "Overtime",
			"amount": 0,
			"payroll_date": [">=", current_month_start],
			"payroll_date": ["<=", current_month_end],
			"docstatus":1
		},
		fields=["name", "employee"]
	)

	for record in missing_overtime_salaries:
		employee = record["employee"]
		record_name = record["name"]

		# Fetch overtime records for the same employee in the current month
		overtime_records = frappe.get_all(
			"Overtime",
			filters={
				"employee": employee,
				"date": [">=", current_month_start],
				"date": ["<=", current_month_end],
				"docstatus":1
			},
			fields=["total_hrs"]
		)
		# Calculate total overtime hours and the corresponding amount
		total_total_hrs = sum([overtime["total_hrs"] for overtime in overtime_records])
		
		# Get daily salary from the latest Salary Structure Assignment
		latest_assignment = frappe.get_all(
			"Salary Structure Assignment",
			filters={"employee": employee, "docstatus": 1},
			order_by="creation DESC",
			limit=1
		)
		
		if latest_assignment:
			daily_salary = frappe.db.get_value("Salary Structure Assignment",
												latest_assignment[0]["name"], "daily_salary")

			# Calculate overtime salary
			overtime_salary = ((daily_salary / 8) * 1.5) * total_total_hrs

			# Update Additional Salary record with the calculated overtime amount
			frappe.db.set_value("Additional Salary", record_name, "amount", overtime_salary)

			# Update the child table in the Additional Salary document
			additional_salary_doc = frappe.get_doc("Additional Salary", record_name)
			overtime_breakup = {
				"basic_per_hour": daily_salary,
				"overtime_hours": total_total_hrs,
				"amount": overtime_salary,
				"overtime_link": record_name,
			}
			additional_salary_doc.set("overtime_breakup", [])
			additional_salary_doc.append("overtime_breakup", overtime_breakup)
			additional_salary_doc.save()
def update_missing_overtime_amounts():
	current_date = datetime.now()
	current_month_start = current_date.replace(day=1)
	current_month_end = (current_month_start.replace(month=current_month_start.month + 1) - timedelta(days=1)).date()

	# Get Additional Salary records with overtime component and 0 amount for the current month
	missing_overtime_salaries = frappe.get_all(
		"Additional Salary",
		filters={
			"salary_component": "Overtime",
			"amount": 0,
			"payroll_date": [">=", current_month_start],
			"payroll_date": ["<=", current_month_end],
				"docstatus":1
		},
		fields=["name", "employee", "company"]
	)

	for record in missing_overtime_salaries:
		employee = record["employee"]
		company = record["company"]
		record_name = record["name"]

		# Fetch overtime records for the same employee in the current month
		overtime_records = frappe.get_all(
			"Overtime",
			filters={
				"employee": employee,
				"date": [">=", current_month_start],
				"date": ["<=", current_month_end],
				"docstatus":1
			},
			fields=["date", "total_hrs"]
		)

		if not overtime_records:
			continue

		# Get daily salary from the latest Salary Structure Assignment
		latest_assignment = frappe.get_all(
			"Salary Structure Assignment",
			filters={"employee": employee, "docstatus": 1},
			order_by="creation DESC",
			limit=1
		)
		
		if latest_assignment:
			daily_salary = frappe.db.get_value("Salary Structure Assignment",
												latest_assignment[0]["name"], "daily_salary")

			# Calculate total overtime hours and the corresponding amount
			total_overtime_hours = sum([overtime["total_hrs"] for overtime in overtime_records])
			overtime_salary = ((daily_salary / 8) * 1.5) * total_overtime_hours

			# Update Additional Salary record with the calculated overtime amount
			frappe.db.set_value("Additional Salary", record_name, "amount", overtime_salary)

			# Update the child table in the Additional Salary document
			additional_salary_doc = frappe.get_doc("Additional Salary", record_name)
			additional_salary_doc.set("overtime_breakup", [])

			for overtime in overtime_records:
				overtime_date = overtime["overtime_date"]
				overtime_hours = overtime["total_hrs"]

				overtime_breakup = {
					"basic_per_hour": daily_salary,
					"overtime_hours": overtime_hours,
					"amount": ((daily_salary / 8) * 1.5) * overtime_hours,
					"overtime_link": overtime_date,  # Change this to the appropriate field
				}
				additional_salary_doc.append("overtime_breakup", overtime_breakup)

			additional_salary_doc.save()


@frappe.whitelist()
def update_status_in_attendance(attendance_id,status_by_employee):
	if frappe.db.exists("Attendance", {"name": attendance_id}):
		attend_doc = frappe.get_doc("Attendance", attendance_id)
		attend_doc.status_by_employee = status_by_employee
		attend_doc.save(ignore_permissions=True)

		response = [] 
		msg = {
			"error": False,
			"message": "Attendance Approved by Employee successfully"
		}
		response.append(msg)
		return response	
	else:
		response = [] 
		msg = {
			"error": True,
			"message": "Attendance Record Not Exist"
		}
		response.append(msg)
		return response
