// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Short Leave Application", {
	employee: function(frm){
        if (frm.doc.employee){
        frm.set_query("shift_assignment", function () {
            return {
                filters: {
                    employee: frm.doc.employee,
                    status: 'Active'
                    },
                };
            });
        }
    }, 
    shift_start:function(frm){
        GetStartEndShift(frm);
    },
    end_shift:function(frm){
        GetStartEndShift(frm);
    },
    in_shift:function(frm){
        GetStartEndShift(frm);
    }, 
    leave_duration:function(frm){
        CalculateDuration(frm);
    },
    onload: function(frm) {
        DocFilters(frm);
	},
    refresh: function(frm){
        DocFilters(frm);
    },
});
function GetStartEndShift(frm){
    frappe.call({
        doc:frm.doc,
        method:'get_start_end_shift',
        callback: function(r) {
            frm.doc.to_time=r.message.to_time;
            frm.doc.from_time = r.message.from_time;
            refresh_field("from_time");
            refresh_field("to_time");
        }
    });
}
function CalculateDuration(frm){
    frappe.call({
        doc:frm.doc,
        method:'calculate_durations',
        callback: function(r) {
            if (r.message.from_time) {
                frm.doc.from_time = r.message.from_time;
                refresh_field("from_time");
            }
            if (r.message.to_time) {
                frm.doc.to_time = r.message.to_time;
                refresh_field("to_time");
            }
        }
    })
}
function  DocFilters(frm){
    frm.set_query("salary_component", function () {
        return {
            filters: {
                type: 'Deduction'
            },
        };
    });
}