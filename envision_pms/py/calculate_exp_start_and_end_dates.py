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


# @frappe.whitelist()
# def calculate_exp_start_and_exp_end_date(project, exp_start_date, company):
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

#     # Track the end date of the previous task
#     prev_task_end_date = update_if_holiday(exp_start_date, company)

#     for task_data in sorted_task_list:
#         task = frappe.get_doc("Task", task_data.name)
#         task.exp_start_date = prev_task_end_date

#         if task.is_group == 1:
#             # If it's a group task, calculate total expected days for the group (including child tasks)
#             total_exp_days = totals_exp_days_for_parent_task(task)
#             task.exp_end_date = add_days(task.exp_start_date, total_exp_days)
#             task.exp_end_date = update_if_holiday(task.exp_end_date, company)

#             # Print debugging information
#             print("\n\n Parent Task End Date:", task.exp_end_date)

#             # print("\n\n Parent Task End Date:", task.exp_end_date)

#             # The next task should start the day after this group task's end date
#             # prev_task_end_date = add_days(task.exp_end_date, 1)
#             prev_task_end_date =task.exp_start_date
#             print("\n\n Next Task Start Date (After Group Task):", prev_task_end_date)

#         # elif task.parent_task:e

#         else:
#             # If it's not a group task, calculate its end date based on its own exp_days
#             task.exp_end_date = add_days(
#                     task.exp_start_date, task.custom_expected_time_in_days
#                 )
#             task.exp_end_date = update_if_holiday(task.exp_end_date, company)
#             print(
#                 "\n\n Task exp end date  (After Non-Group Task):",
#                 task.exp_end_date,
#                 task.custom_expected_time_in_days,
#             )

#             # The next task should start the day after this task's end date
#             prev_task_end_date = add_days(task.exp_end_date, 1)
#             print("\n\n Next Task Start Date (After Non-Group Task):", prev_task_end_date)

#             # Make sure to adjust for holidays
#             prev_task_end_date = update_if_holiday(prev_task_end_date, company)

#         # Save the task with the updated start and end dates
#         task.save()
#         # print("\n Exp Start Date:", task.exp_start_date)
#         # print("\n Exp End Date:", task.exp_end_date)
#         task.reload()

#     frappe.msgprint("Tasks expected start and end dates have been calculated successfully.")


# @frappe.whitelist()
# def totals_exp_days_for_parent_task(task):
#     """
#     Calculates the total expected time in days for a group task, including all its child tasks.
#     """
#     # Initialize total expected days with the group's own expected time
#     total_exp_days_for_parent_task = 0

#     # Get child tasks (if any) that depend on this parent task
#     child_task_details = frappe.get_all(
#         "Task Depends On", filters={"parent": task.name}, fields=["task"]
#     )


#     # If child tasks exist, add their exp_days to the parent task's total exp_days
#     if child_task_details:
#         for child_task in child_task_details:


#             # Get the custom_expected_time_in_days of the child task
#             child_task_doc = frappe.get_doc("Task", child_task["task"])
#             child_exp_days = child_task_doc.custom_expected_time_in_days

#             # Add child's expected days to parent's total expected days
#             total_exp_days_for_parent_task += child_exp_days


#     return total_exp_days_for_parent_task

# # Backup Code

# # @frappe.whitelist()
# # def calculate_exp_start_and_exp_end_date(project, exp_start_date):
# #     # Convert exp_start_date to datetime if it's a string
# #     if isinstance(exp_start_date, str):
# #         try:
# #             exp_start_date = datetime.strptime(exp_start_date, "%Y-%m-%d").date()
# #         except ValueError:
# #             frappe.throw(
# #                 "Invalid date format. Please use YYYY-MM-DD format for exp_start_date."
# #             )

# #     # Get and sort project tasks based on the custom sequence number
# #     project_task_list = get_project_tasks(project)
# #     sorted_task_list = sorted(
# #         project_task_list, key=lambda x: x["custom_task_sequence_number"]
# #     )

# #     # Initialize the variable to track the end date of the previous task
# #     prev_task_end_date = exp_start_date

# #     for task_data in sorted_task_list:
# #         task = frappe.get_doc("Task", task_data.name)

# #         # Set the start date for the current task
# #         task.exp_start_date = prev_task_end_date

# #         # Calculate and set the end date for the current task
# #         task.exp_end_date = task.exp_start_date + timedelta(
# #             days=task.custom_expected_time_in_days
# #         )

# #         # Update the end date for the next task to start the day after this task's end date
# #         prev_task_end_date = task.exp_end_date + timedelta(days=1)

# #         # Save the task with the updated start and end dates
# #         task.save()
# #         print("\n Exp Start Date : ", task.exp_start_date)
# #         print("\n Exp End Date : ", task.exp_end_date)

# #     frappe.msgprint("Task start and end dates have been calculated successfully.")


@frappe.whitelist()
def calculate_exp_start_and_exp_end_date(project, exp_start_date, company):
    # Convert exp_start_date to datetime if it's a string
    if isinstance(exp_start_date, str):
        try:
            exp_start_date = datetime.strptime(exp_start_date, "%Y-%m-%d").date()
        except ValueError:
            frappe.throw("Invalid date format. Please use YYYY-MM-DD format.")

    # Get and sort project tasks based on the custom sequence number
    project_task_list = get_project_tasks(project)
    sorted_task_list = sorted(
        project_task_list, key=lambda x: x["custom_task_sequence_number"]
    )

    processed_tasks = set()  # Keep track of tasks already processed
    prev_task_end_date = update_if_holiday(exp_start_date, company)

    for task_data in sorted_task_list:
        if task_data.name in processed_tasks:
            # Skip tasks already processed as child tasks
            continue

        task = frappe.get_doc("Task", task_data.name)
        task.exp_start_date = prev_task_end_date

        if task.is_group == 1:
            # Calculate all child tasks before proceeding with the parent task
            last_child_end_date = calculate_child_tasks(task, company)
            task.exp_end_date = last_child_end_date  # Parent task's end date becomes the last child's end date
            task.exp_end_date = update_if_holiday(task.exp_end_date, company)

            # Print debugging information
            print("\n\nParent Task End Date:", task.exp_end_date)
        else:
            # Non-group task: Calculate its end date based on custom expected time
            task.exp_end_date = add_days(
                task.exp_start_date, task.custom_expected_time_in_days - 1
            )
            task.exp_end_date = update_if_holiday(task.exp_end_date, company)

            print("\n\nTask End Date (Non-Group Task):", task.exp_end_date)

        # Save the task with the updated dates
        task.save(ignore_permissions=True)
        task.reload()

        # Update previous task's end date to move to the next task
        prev_task_end_date = add_days(task.exp_end_date, 1)
        prev_task_end_date = update_if_holiday(prev_task_end_date, company)

    frappe.msgprint(
        "Tasks' expected start and end dates have been calculated successfully."
    )


@frappe.whitelist()
def calculate_child_tasks(parent_task, company):
    """Calculate the start and end dates for all child tasks of a parent task."""
    child_tasks = frappe.get_all(
        "Task Depends On", filters={"parent": parent_task.name}, fields=["task"]
    )

    prev_child_end_date = (
        parent_task.exp_start_date
    )  # Start with the parent's start date
    last_child_end_date = parent_task.exp_start_date  # Track the last child's end date

    for idx, child_task_data in enumerate(child_tasks):
        child_task = frappe.get_doc("Task", child_task_data["task"])

        if idx == 0:
            # First child starts on the parent's start date
            child_task.exp_start_date = parent_task.exp_start_date
        else:
            # Subsequent child tasks start after the previous one ends
            child_task.exp_start_date = add_days(prev_child_end_date, 1)

        # Adjust start date for holidays
        child_task.exp_start_date = update_if_holiday(
            child_task.exp_start_date, company
        )

        # Calculate end date based on the child's expected time
        child_task.exp_end_date = add_days(
            child_task.exp_start_date, child_task.custom_expected_time_in_days - 1
        )
        child_task.exp_end_date = update_if_holiday(child_task.exp_end_date, company)

        # Save the child task with the updated dates
        child_task.save(ignore_permissions=True)
        child_task.reload()

        # Update the previous child task's end date
        prev_child_end_date = child_task.exp_end_date
        last_child_end_date = child_task.exp_end_date  # Track the last child's end date

    return last_child_end_date  # Return the last child's end date for the parent task
