// Copyright (c) 2024, KCSC and contributors
// For license information, please see license.txt

frappe.query_reports["Short Leave Ledger"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.defaults.get_default("year_start_date"),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.defaults.get_default("year_end_date"),
		},
		{
			fieldname: "leave_type",
			label: __("Leave Type"),
			fieldtype: "Link",
			options: "Leave Type",
		},
		{
			fieldname: "employee",
			label: __("Employee"),
			fieldtype: "Link",
			options: "Employee",
		},
		{
			label: __("Company"),
			fieldname: "company",
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "department",
			label: __("Department"),
			fieldtype: "Link",
			options: "Department",
		},
		{
			fieldname: "transaction_type",
			label: __("Transaction Type"),
			fieldtype: "Select",
			options: [ "" , "Leave Application", "Employee Short Leave Application"],
		},
		{
			fieldname: "group_by",
			label: __("Group By"),
			fieldtype: "Select",
			options: ["Employee", "Transaction"],
			default: "Transaction"
		}
	],
	formatter: (value, row, column, data, default_formatter) => {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "total_leave_days") {
			if (data?.total_leave_days < 0) value = `<span style='color:red!important'>${value}</span>`;
			else value = `<span style='color:green!important'>${value}</span>`;
		}
		if (column.fieldname === "short_leave_duration") {
			if (data?.short_leave_duration < 0) value = `<span style='color:red!important'>${value}</span>`;
			else value = `<span style='color:green!important'>${value}</span>`;
		}
		return value;
	},
};
