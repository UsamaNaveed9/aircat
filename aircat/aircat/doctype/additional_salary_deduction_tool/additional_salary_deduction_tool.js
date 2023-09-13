// Copyright (c) 2023, Pukat and contributors
// For license information, please see license.txt

frappe.ui.form.on('Additional Salary Deduction Tool', {
	refresh: function (frm) {
		frm.set_query("salary_component", "additional_salry", function (frm, cdt, cdn) {
			return {
				filters: {
					"type": "Deduction",
					"disabled": 0
				}
			};
		})		
	},
	onload: function (frm) {
		frm.set_query("salary_component", "additional_salry", function (frm, cdt, cdn) {
			return {
				filters: {
					"type": "Deduction",
					"disabled": 0
				}
			};
		})
	}
});
