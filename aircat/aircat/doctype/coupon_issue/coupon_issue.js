// Copyright (c) 2023, Pukat and contributors
// For license information, please see license.txt

frappe.ui.form.on('Coupon Issue', {
	setup: function(frm) {
		frm.set_query("booklet", function(){
		    return {
		        filters: [
		            ["BookLet","status","in", ["Active"]]
		        ]
		    }
		});
		frm.set_query("driver", function(){
		    return {
		        filters: [
		            ["Driver","status","in", ["Active"]]
		        ]
		    }
		});
	}
});
