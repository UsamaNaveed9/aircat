
frappe.ui.form.on("Salary Slip", {
    employee: function(frm){
        if(frm.doc.employee && frm.doc.salary_structure){
            frappe.call({
                method: "aircat.custompy.salary_slip.get_salary_components",
                args: {
                    "employee": frm.doc.employee,
                    "salary_str": frm.doc.salary_structure,
                    "payment_days": frm.doc.payment_days
                },
                callback: function(r) {
                    if(r.message) {
                        let earnings = r.message[0];
                        let deductions = r.message[1];
                        //console.log(earnings,deductions);
                        cur_frm.clear_table("earnings");
                        cur_frm.clear_table("deductions");
                        for (let i = 0; i < earnings.length; i++){
                            let e_comp = cur_frm.add_child("earnings");
                                e_comp.salary_component = earnings[i].salary_component;
                                e_comp.day_amount = earnings[i].day_amount;
                                e_comp.fixed_amount = earnings[i].fixed_amount;
                                e_comp.amount = earnings[i].amount;
                                cur_frm.refresh_field("earnings");
                        }

                        for (let i = 0; i < deductions.length; i++){
                            let d_comp = cur_frm.add_child("deductions");
                                d_comp.salary_component = deductions[i].salary_component;
                                d_comp.day_amount = deductions[i].day_amount;
                                d_comp.fixed_amount = deductions[i].fixed_amount;
                                d_comp.amount = deductions[i].amount;
                                cur_frm.refresh_field("deductions");
                        }

                        cur_frm.refresh();
                        cur_frm.save();
                    }
                }
            })
        }
    },
    start_date: function(frm){
        if(frm.doc.employee && frm.doc.salary_structure){
            frappe.call({
                method: "aircat.custompy.salary_slip.get_salary_components",
                args: {
                    "employee": frm.doc.employee,
                    "salary_str": frm.doc.salary_structure,
                    "payment_days": frm.doc.payment_days
                },
                callback: function(r) {
                    if(r.message) {
                        let earnings = r.message[0];
                        let deductions = r.message[1];
                        console.log(earnings,deductions);
                        cur_frm.clear_table("earnings");
                        cur_frm.clear_table("deductions");
                        for (let i = 0; i < earnings.length; i++){
                            let e_comp = cur_frm.add_child("earnings");
                                e_comp.salary_component = earnings[i].salary_component;
                                e_comp.day_amount = earnings[i].day_amount;
                                e_comp.fixed_amount = earnings[i].fixed_amount;
                                e_comp.amount = earnings[i].amount;
                                cur_frm.refresh_field("earnings");
                        }

                        for (let i = 0; i < deductions.length; i++){
                            let d_comp = cur_frm.add_child("deductions");
                                d_comp.salary_component = deductions[i].salary_component;
                                d_comp.day_amount = deductions[i].day_amount;
                                d_comp.fixed_amount = deductions[i].fixed_amount;
                                d_comp.amount = deductions[i].amount;
                                cur_frm.refresh_field("deductions");
                        }

                        cur_frm.refresh();
                    }
                }
            })
        }
    },
    end_date: function(frm){
        if(frm.doc.employee && frm.doc.salary_structure){
            frappe.call({
                method: "aircat.custompy.salary_slip.get_salary_components",
                args: {
                    "employee": frm.doc.employee,
                    "salary_str": frm.doc.salary_structure,
                    "payment_days": frm.doc.payment_days
                },
                callback: function(r) {
                    if(r.message) {
                        let earnings = r.message[0];
                        let deductions = r.message[1];
                        console.log(earnings,deductions);
                        cur_frm.clear_table("earnings");
                        cur_frm.clear_table("deductions");
                        for (let i = 0; i < earnings.length; i++){
                            let e_comp = cur_frm.add_child("earnings");
                                e_comp.salary_component = earnings[i].salary_component;
                                e_comp.day_amount = earnings[i].day_amount;
                                e_comp.fixed_amount = earnings[i].fixed_amount;
                                e_comp.amount = earnings[i].amount;
                                cur_frm.refresh_field("earnings");
                        }

                        for (let i = 0; i < deductions.length; i++){
                            let d_comp = cur_frm.add_child("deductions");
                                d_comp.salary_component = deductions[i].salary_component;
                                d_comp.day_amount = deductions[i].day_amount;
                                d_comp.fixed_amount = deductions[i].fixed_amount;
                                d_comp.amount = deductions[i].amount;
                                cur_frm.refresh_field("deductions");
                        }

                        cur_frm.refresh();
                    }
                }
            })
        }
    },

});

frappe.ui.form.on("Salary Detail", "day_amount", function(frm, cdt, cdn) {
	var d = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "amount", d.day_amount * frm.doc.payment_days);

    cur_frm.refresh()  
});