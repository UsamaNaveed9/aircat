// Copyright (c) 2023, Pukat and contributors
// For license information, please see license.txt

frappe.ui.form.on('Coupon Invoiced', {
	setup: function(frm) {
		frm.set_query("booklet", function(){
		    return {
		        filters: [
		            ["BookLet","status","in", ["Active"]]
		        ]
		    }
		});
		frm.fields_dict['coupon_issues'].grid.get_field("coupon_issue").get_query = function(doc, cdt, cdn) {
			return {
				filters: [
					['Coupon Issue', 'booklet', 'in', frm.doc.booklet],
				]
			}
		}
	}
});
