
frappe.ui.form.on("Salary Slip", {
    employee: function (frm) {
        if (frm.doc.employee && frm.doc.salary_structure) {
            frappe.call({
                method: "aircat.custompy.salary_slip.get_salary_components",
                args: {
                    "employee": frm.doc.employee,
                    "salary_str": frm.doc.salary_structure,
                    "payment_days": frm.doc.payment_days
                },
                callback: function (r) {
                    if (r.message) {
                        let earnings = r.message[0];
                        let deductions = r.message[1];
                        //console.log(earnings,deductions);
                        //cur_frm.clear_table("earnings");
                        //cur_frm.clear_table("deductions");
                        for (let i = 0; i < earnings.length; i++) {
                            let e_comp = cur_frm.add_child("earnings");
                            e_comp.salary_component = earnings[i].salary_component;
                            e_comp.day_amount = earnings[i].day_amount;
                            e_comp.fixed_amount = earnings[i].fixed_amount;
                            e_comp.amount = earnings[i].amount;
                            cur_frm.refresh_field("earnings");
                        }

                        // for (let i = 0; i < deductions.length; i++){
                        //     let d_comp = cur_frm.add_child("deductions");
                        //         d_comp.salary_component = deductions[i].salary_component;
                        //         d_comp.day_amount = deductions[i].day_amount;
                        //         d_comp.fixed_amount = deductions[i].fixed_amount;
                        //         d_comp.amount = deductions[i].amount;
                        //         cur_frm.refresh_field("deductions");
                        // }

                        // var s_date = cur_frm.doc.start_date;
                        // var e_date = cur_frm.doc.end_date;
                        // frappe.db.get_list('Additional Salary', {
                        //     fields: ['salary_component','amount'],
                        //     filters: [
                        //         ["payroll_date","between",[s_date,e_date]],
                        //         ["employee", "=", cur_frm.doc.employee],
                        //         ["type", "=", "Earning"]]
                        // }).then(records => {
                        //     //console.log(records,records.length);
                        //     if(records.length >=1 ){
                        //         for (let i = 0; i < records.length; i++){
                        //             let e_comp = cur_frm.add_child("earnings");
                        //                 e_comp.salary_component = records[i].salary_component;
                        //                 e_comp.amount = records[i].amount;
                        //                 cur_frm.refresh_field("earnings");
                        //         }
                        //     }
                        // })

                        // frappe.db.get_list('Additional Salary', {
                        //     fields: ['salary_component','amount'],
                        //     filters: [
                        //         ["payroll_date","between",[s_date,e_date]],
                        //         ["employee", "=", cur_frm.doc.employee],
                        //         ["type", "=", "Deduction"]]
                        // }).then(records => {
                        //     //console.log(records,records.length);
                        //     for (let i = 0; i < records.length; i++){
                        //         let d_comp = cur_frm.add_child("deductions");
                        //             d_comp.salary_component = records[i].salary_component;
                        //             d_comp.amount = records[i].amount;
                        //             cur_frm.refresh_field("deductions");
                        //     }
                        // })

                        let gross_pay = 0;
                        let total_ded = 0;
                        if (frm.doc.earnings) {
                            frm.doc.earnings.forEach(function (d) { gross_pay += d.amount; });
                            frm.set_value('gross_pay', gross_pay);   
                        }
                        if (frm.doc.deductions) {
                            frm.doc.deductions.forEach(function (d) { total_ded += d.amount; });
                            frm.set_value('total_deduction', total_ded);            
                        }
        frm.refresh_fields(["gross_pay", "total_deduction"])
                        cur_frm.refresh();
                    }
                }
            })
        }
    },
    start_date: function (frm) {
        if (frm.doc.employee && frm.doc.salary_structure) {
            frappe.call({
                method: "aircat.custompy.salary_slip.get_salary_components",
                args: {
                    "employee": frm.doc.employee,
                    "salary_str": frm.doc.salary_structure,
                    "payment_days": frm.doc.payment_days
                },
                callback: function (r) {
                    if (r.message) {
                        let earnings = r.message[0];
                        let deductions = r.message[1];
                        //console.log(earnings,deductions);
                        //cur_frm.clear_table("earnings");
                        // cur_frm.clear_table("deductions");
                        for (let i = 0; i < earnings.length; i++) {
                            let e_comp = cur_frm.add_child("earnings");
                            e_comp.salary_component = earnings[i].salary_component;
                            e_comp.day_amount = earnings[i].day_amount;
                            e_comp.fixed_amount = earnings[i].fixed_amount;
                            e_comp.amount = earnings[i].amount;
                            cur_frm.refresh_field("earnings");
                        }

                        // for (let i = 0; i < deductions.length; i++){
                        //     let d_comp = cur_frm.add_child("deductions");
                        //         d_comp.salary_component = deductions[i].salary_component;
                        //         d_comp.day_amount = deductions[i].day_amount;
                        //         d_comp.fixed_amount = deductions[i].fixed_amount;
                        //         d_comp.amount = deductions[i].amount;
                        //         cur_frm.refresh_field("deductions");
                        // }

                        // var s_date = cur_frm.doc.start_date;
                        // var e_date = cur_frm.doc.end_date;
                        // frappe.db.get_list('Additional Salary', {
                        //     fields: ['salary_component','amount'],
                        //     filters: [
                        //         ["payroll_date","between",[s_date,e_date]],
                        //         ["employee", "=", cur_frm.doc.employee],
                        //         ["type", "=", "Earning"]]
                        // }).then(records => {
                        //     //console.log(records,records.length);
                        //     if(records.length >=1 ){
                        //         for (let i = 0; i < records.length; i++){
                        //             let e_comp = cur_frm.add_child("earnings");
                        //                 e_comp.salary_component = records[i].salary_component;
                        //                 e_comp.amount = records[i].amount;
                        //                 cur_frm.refresh_field("earnings");
                        //         }
                        //     }
                        // })

                        // frappe.db.get_list('Additional Salary', {
                        //     fields: ['salary_component','amount'],
                        //     filters: [
                        //         ["payroll_date","between",[s_date,e_date]],
                        //         ["employee", "=", cur_frm.doc.employee],
                        //         ["type", "=", "Deduction"]]
                        // }).then(records => {
                        //     //console.log(records,records.length);
                        //     for (let i = 0; i < records.length; i++){
                        //         let d_comp = cur_frm.add_child("deductions");
                        //             d_comp.salary_component = records[i].salary_component;
                        //             d_comp.amount = records[i].amount;
                        //             cur_frm.refresh_field("deductions");
                        //     }
                        // })

                        let gross_pay = 0;
                        let total_ded = 0;
                        frm.doc.earnings.forEach(function (d) { gross_pay += d.amount; });
                        frm.set_value('gross_pay', gross_pay);
                        frm.doc.deductions.forEach(function (d) { total_ded += d.amount; });
                        frm.set_value('total_deduction', total_ded);
                        cur_frm.refresh();
                    }
                }
            })
        }
    },
    end_date: function (frm) {
        if (frm.doc.employee && frm.doc.salary_structure) {
            frappe.call({
                method: "aircat.custompy.salary_slip.get_salary_components",
                args: {
                    "employee": frm.doc.employee,
                    "salary_str": frm.doc.salary_structure,
                    "payment_days": frm.doc.payment_days
                },
                callback: function (r) {
                    if (r.message) {
                        let earnings = r.message[0];
                        let deductions = r.message[1];
                        //console.log(earnings,deductions);
                        //cur_frm.clear_table("earnings");
                        //cur_frm.clear_table("deductions");
                        for (let i = 0; i < earnings.length; i++) {
                            console.log(frm.doc.payment_days);
                            let e_comp = cur_frm.add_child("earnings");
                            e_comp.salary_component = earnings[i].salary_component;
                            e_comp.day_amount = earnings[i].day_amount;
                            e_comp.fixed_amount = earnings[i].fixed_amount;
                            e_comp.payment_days = frm.doc.payment_days;
                            e_comp.amount = earnings[i].amount;
                            cur_frm.refresh_field("earnings");
                        }

                        // for (let i = 0; i < deductions.length; i++){
                        //     let d_comp = cur_frm.add_child("deductions");
                        //         d_comp.salary_component = deductions[i].salary_component;
                        //         d_comp.day_amount = deductions[i].day_amount;
                        //         d_comp.fixed_amount = deductions[i].fixed_amount;
                        //         d_comp.amount = deductions[i].amount;
                        //         cur_frm.refresh_field("deductions");
                        // }

                        // var s_date = cur_frm.doc.start_date;
                        // var e_date = cur_frm.doc.end_date;
                        // frappe.db.get_list('Additional Salary', {
                        //     fields: ['salary_component','amount'],
                        //     filters: [
                        //         ["payroll_date","between",[s_date,e_date]],
                        //         ["employee", "=", cur_frm.doc.employee],
                        //         ["type", "=", "Earning"]]
                        // }).then(records => {
                        //     //console.log(records,records.length);
                        //     if(records.length >=1 ){
                        //         for (let i = 0; i < records.length; i++){
                        //             let e_comp = cur_frm.add_child("earnings");
                        //                 e_comp.salary_component = records[i].salary_component;
                        //                 e_comp.amount = records[i].amount;
                        //                 cur_frm.refresh_field("earnings");
                        //         }
                        //     }
                        // })

                        // frappe.db.get_list('Additional Salary', {
                        //     fields: ['salary_component','amount'],
                        //     filters: [
                        //         ["payroll_date","between",[s_date,e_date]],
                        //         ["employee", "=", cur_frm.doc.employee],
                        //         ["type", "=", "Deduction"]]
                        // }).then(records => {
                        //     //console.log(records,records.length);
                        //     for (let i = 0; i < records.length; i++){
                        //         let d_comp = cur_frm.add_child("deductions");
                        //             d_comp.salary_component = records[i].salary_component;
                        //             d_comp.amount = records[i].amount;
                        //             cur_frm.refresh_field("deductions");
                        //     }
                        // })

                        let gross_pay = 0;
                        let total_ded = 0;
                        frm.doc.earnings.forEach(function (d) { gross_pay += d.amount; });
                        frm.set_value('gross_pay', gross_pay);
                        frm.doc.deductions.forEach(function (d) { total_ded += d.amount; });
                        frm.set_value('total_deduction', total_ded);
                        cur_frm.refresh();
                    }
                }
            })
        }
    },
    refresh: function (frm) {
        //console.log("here");
        let gross_pay = 0;
        let total_ded = 0;
        if (frm.doc.earnings) {
            frm.doc.earnings.forEach(function (d) { gross_pay += d.amount; });
            frm.set_value('gross_pay', gross_pay);   
        }
        if (frm.doc.deductions) {
            frm.doc.deductions.forEach(function (d) { total_ded += d.amount; });
            frm.set_value('total_deduction', total_ded);            
        }
        frm.set_value('net_pay', gross_pay - total_ded);

        frm.refresh_fields(["gross_pay", "total_deduction", "net_pay"])
    }
    // before_save: function(frm){
    //     var ern = cur_frm.doc.earnings;
    //     var s_date = cur_frm.doc.start_date;
    //     var e_date = cur_frm.doc.end_date;
    //     frappe.db.get_list('Additional Salary', {
    //         fields: ['salary_component','amount'],
    //         filters: [
    //             ["payroll_date","between",[s_date,e_date]],
    //             ["employee", "=", cur_frm.doc.employee],
    //             ["type", "=", "Earning"]]
    //     }).then(records => {
    //         //console.log(records,records.length);
    //         if(records.length >=1 ){
    //             for (let i = 0; i < records.length; i++){
    //                 for (let j = 0; j < ern.length; j++){
    //                     if(records[i].salary_component == ern[j].salary_component){
    //                         frm.get_field('earnings').grid.grid_rows[j].remove();
    //                         frm.refresh_field('earnings');
    //                         cur_frm.save();
    //                     }

    //                 }
    //             }
    //             // for (let i = 0; i < records.length; i++){
    //             //     let e_comp = cur_frm.add_child("earnings");
    //             //         e_comp.salary_component = records[i].salary_component;
    //             //         e_comp.amount = records[i].amount;
    //             //         cur_frm.refresh_field("earnings");
    //             // }
    //         }
    //     })
    // }

});

frappe.ui.form.on("Salary Detail", "day_amount", function (frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    // frappe.model.set_value(cdt, cdn, "amount", d.day_amount * frm.doc.payment_days);
    frappe.model.set_value(cdt, cdn, "amount", d.day_amount * d.payment_days);

    cur_frm.refresh()
});

frappe.ui.form.on("Salary Detail", "payment_days", function (frm, cdt, cdn) {
    var d = locals[cdt][cdn];
    // frappe.model.set_value(cdt, cdn, "amount", d.day_amount * frm.doc.payment_days);
    if (!d.fixed_amount) {
        frappe.model.set_value(cdt, cdn, "amount", d.day_amount * d.payment_days);
        cur_frm.refresh()
    }
});
frappe.ui.form.on('Salary Detail', {
    payment_days: function (frm) {
        set_totals(frm);
    }
});