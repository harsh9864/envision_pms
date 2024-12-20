import frappe 

def update_time_and_costing(self):
        

        tl = frappe.db.sql(
			"""select min(from_time) as start_date, max(to_time) as end_date,
			sum(billing_amount) as total_billing_amount, sum(costing_amount) as total_costing_amount,
			sum(hours) as time from `tabTimesheet Detail` where task = %s and docstatus=1""",
			self.name,
			as_dict=1,
		)[0]
        if self.status == "Open":
            self.status = "Working"
        self.total_costing_amount = tl.total_costing_amount
        self.total_billing_amount = tl.total_billing_amount

        # Fetch timesheet details where 'completed' is checked and docstatus=1
        completed_timesheet_details = frappe.db.sql(
            """
            SELECT 
                COUNT(name) AS completed_count
            FROM `tabTimesheet Detail`
            WHERE task = %s 
            AND docstatus = 1 
            AND completed = 1
            """,
            self.name,
            as_dict=1,
        )[0]

        # Update only if there are completed entries
        if completed_timesheet_details and completed_timesheet_details.completed_count > 0:

            self.actual_time = tl.time
            self.act_start_date = tl.start_date
            self.act_end_date = tl.end_date

            # Set the completion date to the act_end_date
            if self.status != "Completed":
                self.status = "Completed"
                self.completed_on = tl.end_date 

            #  All Frappe-level validations for the Task doctype
            self.validate()  
            self.save()