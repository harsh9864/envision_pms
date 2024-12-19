import frappe


@frappe.whitelist()
# Calculate the remaining hours for a given task based on its expected time and actual logged time.
def calculate_task_remaining_hrs(task):
    # Fetch task details
    task_details = frappe.db.get_value(
        "Task", task, [ "expected_time"], as_dict=True
    )

    if not task_details:
        frappe.throw(f"Task not found: {task}")

    # Fetch the total actual time logged for the task
    task_actual_time = frappe.db.sql(
        """
        SELECT SUM(hours) AS total_logged_hours
        FROM `tabTimesheet Detail`
        WHERE task = %s AND docstatus = 1
        """,
        task,
        as_dict=True,
    )[0]

    # Handle cases where no time logs exist
    total_logged_hours = task_actual_time.total_logged_hours or 0

    # Calculate remaining hours
    remaining_hrs = (task_details.expected_time or 0) - total_logged_hours
    if remaining_hrs < 0:
        remaining_hrs = 0

    return {
        "remaining_hrs": remaining_hrs,
        "expected_hrs": task_details.expected_time or 0,
    }
