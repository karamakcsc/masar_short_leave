# Copyright (c) 2024, KCSC and contributors
# For license information, please see license.txt

import frappe
from frappe import _

Filters = frappe._dict


def execute(filters: Filters = None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_columns(filters: Filters) -> list[dict]:
	column =  [
		{"label": _("Employee"),"fieldname": "employee","fieldtype": "Link","options": "Employee","width": 240},
		{"label": _("Employee Name"),"fieldname": "employee_name","fieldtype": "Data" , "width": 240},
  		{"label": _("Company"),"fieldname": "company","fieldtype": "Link","options": "Company","width": 150,}
	]
	if filters.get("group_by"):
		if filters.get("group_by") == 'Transaction':
			column.extend([
				{"label": _("From Date"),"fieldname": "from_date","fieldtype": "Date","width": 120,},
				{"label": _("To Date"),"fieldname": "to_date","fieldtype": "Date","width": 120,},
       			{"label": _("Leave Type"),"fieldname": "leave_type","fieldtype": "Link","options": "Leave Type","width": 150},
				{"label": _("Transaction Type"),"fieldname": "transaction_type","fieldtype": "Link","options": "DocType","width": 130},
				{"label": _("Transaction Name"),"fieldname": "leave_name","fieldtype": "Dynamic Link","options": "transaction_type","width": 180},
			])
		column.extend([
      			{"label": _("Total Leave Days"),"fieldname": "total_leave_days","fieldtype": "Float","width": 150},
       			{"label": _("Short Leave Duration"),"fieldname": "short_leave_duration","fieldtype": "Duration","width": 150}
        	])
	return column

def get_data(filters: Filters) -> list[dict]:
    (
        short_emp, 
     	la_trans, 
      	short_trans,
       	group_by_trans, 
        la_cond_trnas,
        la_emp
    ) = '', '', '' , '' , '' , ''
    conditions = ["docstatus = 1 AND status = 'Approved'"]
    if filters.get('from_date') and filters.get('to_date'):
        conditions.append(f"posting_date >= '{filters.get('from_date')}' AND posting_date <= '{filters.get('to_date')}'")
    if filters.get('employee'):
        conditions.append(f"employee = '{filters.get('employee')}'")
    if filters.get('department'):
        conditions.append(f"department = '{filters.get('department')}'")
    if filters.get('leave_type'):
        conditions.append(f"leave_type = '{filters.get('leave_type')}'")
    if filters.get('company'):
        conditions.append(f"company = '{filters.get('company')}'")
    cond = " AND ".join(conditions)
    if filters.get("group_by"):
        if filters.get("group_by") == 'Employee':
            la_emp =  """
				, SUM(tla.total_leave_days) * -1  AS total_leave_days , 
    			0 AS short_leave_duration
            """
            short_emp = """
            	, 0 AS total_leave_days,
				(SUM(leave_duration) - (COALESCE((
        										SELECT SUM(tla2.total_leave_days)
												FROM `tabLeave Application` tla2
												WHERE tla2.employee = tesla.employee AND tla2.custom_esla_ref IS NOT NULL
    				) , 0)*3600*(
					SELECT 
     					ts.value 
     				FROM 
         				tabSingles ts 
             		WHERE 
               			ts.doctype = 'HR Settings' 
                  		AND ts.field = 'standard_working_hours'
                    )) ) * -1
                    AS short_leave_duration
             """
        elif filters.get("group_by") == 'Transaction':
            short_trans = """
            	,leave_date AS from_date, leave_date AS to_date
                , leave_type, 'Employee Short Leave Application' AS transaction_type, name AS leave_name, NULL AS total_leave_days, SUM(leave_duration) *-1 AS short_leave_duration
            		"""
            la_trans = """ 
                ,from_date, to_date, leave_type, 'Leave Application' AS transaction_type,name AS leave_name, SUM(total_leave_days) * -1 AS total_leave_days, NULL AS short_leave_duration
            			"""
            group_by_trans = ", name "
            la_cond_trnas = " AND custom_esla_ref IS NULL"
    
    la_query = f"""
        SELECT 
            employee, 
            employee_name, 
            company
            {la_trans} {la_emp}
        FROM 
            `tabLeave Application` tla
        WHERE 
            {cond} {la_cond_trnas}
        GROUP BY 
            employee {group_by_trans}  
    """
    short_query = f"""
        SELECT 
            employee, 
            employee_name, 
            company AS company
            {short_trans}  {short_emp}
        FROM 
            `tabEmployee Short Leave Application` tesla
        WHERE 
            {cond}   
        GROUP BY 
           employee {group_by_trans}
        ORDER BY 
            employee
    """
    full = la_query + " UNION " + short_query    
    if filters.get('transaction_type'):
        if filters.get('transaction_type') == "Leave Application":
            return frappe.db.sql(la_query)
        elif filters.get('transaction_type') == "Employee Short Leave Application":
            return frappe.db.sql(short_query)
        else: 
            return frappe.db.sql(full)
    return frappe.db.sql(full)