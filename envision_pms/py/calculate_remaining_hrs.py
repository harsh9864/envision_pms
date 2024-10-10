import frappe


@frappe.whitelist()
def calculate_task_remaining_hrs(task):
    task_details = frappe.get_doc(
        "Task", task, ["actual_time", "expected_time"], as_dict=True
    )
    if not task_details:
        frappe.throw(f"Task not found {task}")

    remaining_hrs = task_details.expected_time - task_details.actual_time

    if remaining_hrs < 0:
        remaining_hrs = 0
    return {
        "remaining_hrs": remaining_hrs,
        "expected_hrs": task_details.expected_time,
    }
