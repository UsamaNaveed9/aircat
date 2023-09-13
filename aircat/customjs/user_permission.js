frappe.ui.form.on("User Permission", {
    for_value: function (frm) {
        if (frm.doc.allow == 'Employee') {
            frappe.call({
                method: "frappe.client.get_value",  // Frappe method to get value
                args: {
                    doctype: "Employee",  // The document type you're querying
                    filters: {
                        name: frm.doc.for_value
                    },
                    fieldname: "employee_name"  // Field you want to retrieve
                },
                callback: function(response) {
                    if (response.message) {
                        let employeeName = response.message.employee_name;
                        console.log(employeeName);
                        frm.set_value('employee_name', employeeName);
                    }
                }
            });
        }
    }
});
