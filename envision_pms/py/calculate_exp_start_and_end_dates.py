import frappe
from .set_sequence_number import get_project_tasks
from datetime import datetime, timedelta


@frappe.whitelist()
def calculate_exp_start_and_exp_end_date(project, exp_start_date):
    # Convert exp_start_date to datetime if it's a string
    if isinstance(exp_start_date, str):
        try:
            exp_start_date = datetime.strptime(exp_start_date, "%Y-%m-%d").date()
        except ValueError:
            frappe.throw(
                "Invalid date format. Please use YYYY-MM-DD format for exp_start_date."
            )

    # Get and sort project tasks based on the custom sequence number
    project_task_list = get_project_tasks(project)
    sorted_task_list = sorted(
        project_task_list, key=lambda x: x["custom_task_sequence_number"]
    )

    # Initialize the variable to track the end date of the previous task
    prev_task_end_date = exp_start_date

    # Loop through each task in the sorted list
    for task_data in sorted_task_list:
        task = frappe.get_doc("Task", task_data.name)

        # Set the start date for the current task
        task.exp_start_date = prev_task_end_date

        # Calculate and set the end date for the current task
        task.exp_end_date = task.exp_start_date + timedelta(
            days=task.custom_expected_time_in_days
        )

        # Update the end date for the next task to start the day after this task's end date
        prev_task_end_date = task.exp_end_date + timedelta(days=1)

        # Save the task with the updated start and end dates
        task.save()
        print("\n Exp Start Date : ", task.exp_start_date)
        print("\n Exp End Date : ", task.exp_end_date)

    frappe.msgprint("Task start and end dates have been calculated successfully.")
