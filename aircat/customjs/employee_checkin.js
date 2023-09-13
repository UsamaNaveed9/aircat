
frappe.ui.form.on("Employee Checkin", {
    refresh: function(frm) {
		if(frm.doc.log_type === 'IN' && !(frm.doc.attendance)) {
			frm.add_custom_button(__('Mark Attendance'), () => {
				frappe.call({
                    method: "aircat.custompy.employee_checkin.mark_attendance",
                    args: {
                        	"employee": frm.doc.employee,
    						"date": frm.doc.date,
                            "time": frm.doc.time,
                            "checkin_doc": frm.doc.name
              		},
        			freeze: true,
            		freeze_message: "Processing",
                    callback: function() {
                        frappe.msgprint('Attendance Marked Successfully');
                    }
                });
			});
		}
	},
});