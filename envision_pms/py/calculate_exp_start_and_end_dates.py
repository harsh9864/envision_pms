import frappe
from .set_sequence_number import get_project_tasks
from datetime import datetime, timedelta


from frappe.utils import add_days

from erpnext import get_default_company

from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday


#  Function to update date if holiday found
@frappe.whitelist()
def update_if_holiday(date, company):
    holiday_list = get_holiday_list(company)
    while is_holiday(holiday_list, date):
        date = add_days(date, 1)
    return date


# Function to get holiday list
@frappe.whitelist()
def get_holiday_list(company=None):
    if not company:
        company = get_default_company() or frappe.get_all("Company")[0].name

    holiday_list = frappe.get_cached_value("Company", company, "default_holiday_list")
    if not holiday_list:
        frappe.throw(
            ("Please set a default Holiday List for Company {0}").format(
                frappe.bold(get_default_company())
            )
        )
    return holiday_list


@frappe.whitelist()
def calculate_exp_start_and_exp_end_date(project, exp_start_date, company):
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

    # Track the end date of the previous task
    prev_task_end_date = update_if_holiday(exp_start_date, company)

    for task_data in sorted_task_list:
        task = frappe.get_doc("Task", task_data.name)
        task.exp_start_date = prev_task_end_date

        # if task.is_group == 1:
        #     # If it's a group task, calculate total expected days for the group (including child tasks)
        #     total_exp_days = totals_exp_days_for_parent_task(task)
        #     task.exp_end_date = add_days(task.exp_start_date, total_exp_days)
        #     task.exp_end_date = update_if_holiday(task.exp_end_date, company)

        #     # Print debugging information
        #     print("\n\n Parent Task End Date:", task.exp_end_date)

        #     # The next task should start the day after this group task's end date
        #     prev_task_end_date = add_days(task.exp_end_date, 1)
        #     print("\n\n Next Task Start Date (After Group Task):", prev_task_end_date)

        # else:
            # If it's not a group task, calculate its end date based on its own exp_days
        task.exp_end_date = add_days(
                task.exp_start_date, task.custom_expected_time_in_days
            )
        task.exp_end_date = update_if_holiday(task.exp_end_date, company)

            # The next task should start the day after this task's end date
        prev_task_end_date = add_days(task.exp_end_date, 1)
        print("\n\n Next Task Start Date (After Non-Group Task):", prev_task_end_date)

        # Make sure to adjust for holidays
        prev_task_end_date = update_if_holiday(prev_task_end_date, company)

        # Save the task with the updated start and end dates
        task.save()
        print("\n Exp Start Date:", task.exp_start_date)
        print("\n Exp End Date:", task.exp_end_date)
        task.reload()

    frappe.msgprint("Tasks expected start and end dates have been calculated successfully.")


@frappe.whitelist()
def totals_exp_days_for_parent_task(task):
    """
    Calculates the total expected time in days for a group task, including all its child tasks.
    """
    # Initialize total expected days with the group's own expected time
    total_exp_days_for_parent_task = task.custom_expected_time_in_days

    # Get child tasks (if any) that depend on this parent task
    child_task_details = frappe.get_all(
        "Task Depends On", filters={"parent": task.name}, fields=["task"]
    )
    print("\nChild Task Details:", child_task_details)

    # If child tasks exist, add their exp_days to the parent task's total exp_days
    if child_task_details:
        for child_task in child_task_details:
            print("\nProcessing Child Task:", child_task["task"])

            # Get the custom_expected_time_in_days of the child task
            child_task_doc = frappe.get_doc("Task", child_task["task"])
            child_exp_days = child_task_doc.custom_expected_time_in_days

            # Add child's expected days to parent's total expected days
            total_exp_days_for_parent_task += child_exp_days
            print(f"\nAdded {child_exp_days} days for child task {child_task['task']}")

    print("\nTotal Expected Days for Parent Task:", total_exp_days_for_parent_task)
    return total_exp_days_for_parent_task

# Backup Code

# @frappe.whitelist()
# def calculate_exp_start_and_exp_end_date(project, exp_start_date):
#     # Convert exp_start_date to datetime if it's a string
#     if isinstance(exp_start_date, str):
#         try:
#             exp_start_date = datetime.strptime(exp_start_date, "%Y-%m-%d").date()
#         except ValueError:
#             frappe.throw(
#                 "Invalid date format. Please use YYYY-MM-DD format for exp_start_date."
#             )

#     # Get and sort project tasks based on the custom sequence number
#     project_task_list = get_project_tasks(project)
#     sorted_task_list = sorted(
#         project_task_list, key=lambda x: x["custom_task_sequence_number"]
#     )

#     # Initialize the variable to track the end date of the previous task
#     prev_task_end_date = exp_start_date

#     for task_data in sorted_task_list:
#         task = frappe.get_doc("Task", task_data.name)

#         # Set the start date for the current task
#         task.exp_start_date = prev_task_end_date

#         # Calculate and set the end date for the current task
#         task.exp_end_date = task.exp_start_date + timedelta(
#             days=task.custom_expected_time_in_days
#         )

#         # Update the end date for the next task to start the day after this task's end date
#         prev_task_end_date = task.exp_end_date + timedelta(days=1)

#         # Save the task with the updated start and end dates
#         task.save()
#         print("\n Exp Start Date : ", task.exp_start_date)
#         print("\n Exp End Date : ", task.exp_end_date)

#     frappe.msgprint("Task start and end dates have been calculated successfully.")
