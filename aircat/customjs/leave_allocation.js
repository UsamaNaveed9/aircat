cur_frm.add_fetch('employee', 'employee_name', 'employee_name');

frappe.ui.form.on("Leave Allocation", {
	onload: function(frm) {
		// Ignore cancellation of doctype on cancel all.
        console.log("Override");
		frm.ignore_doctypes_on_cancel_all = ["Leave Ledger Entry"];

		if (!frm.doc.from_date) frm.set_value("from_date", frappe.datetime.get_today());

		frm.set_query("employee", function() {
			return {
				query: "erpnext.controllers.queries.employee_query"
			};
		});
		frm.set_query("leave_type", function() {
			return {
				filters: {
					// is_lwp: 0
				}
			};
		});
	},

});
