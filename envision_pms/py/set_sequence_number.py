import frappe
from .get_data import get_default_shift_hours


# set sequence number to every task of the project
@frappe.whitelist()
def set_sequence_number_to_tasks(current_task, project):
    try:

        # Fetch project tasks and template tasks
        project_task_list = get_project_tasks(project)
        template_task_list = get_template_tasks(project)
        current_task_details = frappe.get_doc(
            "Task", current_task, "custom_task_sequence_number", as_dict=True
        )

        # Assign sequence numbers to the project tasks
        sorted_project_task_list = assign_custom_task_sequence(
            project_task_list, template_task_list
        )

        # Update the custom_task_sequence_number in the database
        update_task_sequence(sorted_project_task_list, template_task_list)

        print(
            "\nProject Task List with updated Sequence Numbers:",
            project_task_list,
        )

        # task.reload()

        sorted(project_task_list, key=lambda x: x["custom_task_sequence_number"])
        # print("Current task sequence number", current_task["custom_task_sequence_number"])

    except Exception as e:
        frappe.throw(f"An error occurred: {str(e)}")


@frappe.whitelist()
def get_project_tasks(project):

    # Fetch project tasks.
    project_task_list = frappe.get_all(
        "Task",
        filters={"project": project},
        fields=[
            "name",
            "subject",
            "custom_task_sequence_number",
            "custom_expected_time_in_days",
            "exp_start_date",
            "exp_end_date",
        ],
    )
    if not project_task_list:
        frappe.throw(f"No tasks found for project: {project}")
    return project_task_list


@frappe.whitelist()
def get_template_tasks(project):

    # Fetch template name for the project.
    project_template = frappe.get_value("Project", project, "project_template")
    if not project_template:
        frappe.throw(f"No project template found for project: {project}")
        return "No project template found"

    template_task_list = frappe.get_all(
        "Project Template Task",
        filters={"parent": project_template},
        fields=["subject", "idx", "task"],
    )
    if not template_task_list:
        frappe.throw(f"No tasks found in project template : {project_template}")

    # Sort the template task list by idx
    return sorted(template_task_list, key=lambda x: x["idx"])


@frappe.whitelist()
def assign_custom_task_sequence(project_task_list, template_task_list):

    # Assign sequence numbers to project tasks based on matching subjects in template tasks.
    subject_to_idx_map = {task["subject"]: task["idx"] for task in template_task_list}
    print("\n\ntemplate_task_list:", template_task_list)

    # Assign sequence numbers and return sorted project task list
    for task in project_task_list:
        task["custom_task_sequence_number"] = subject_to_idx_map.get(task["subject"], 0)

    return sorted(project_task_list, key=lambda x: x["custom_task_sequence_number"])


@frappe.whitelist()
def update_task_sequence(project_task_list, template_task_list):

    # Update the custom_task_sequence_number in the Task doctype for each task.
    try:
        for task_data in project_task_list:
            # Fetch the Task document using get_doc
            task = frappe.get_doc("Task", task_data["name"])
            # print(task.name)

            # Set the custom_task_sequence_number using the value from project_task_list
            task.custom_task_sequence_number = task_data["custom_task_sequence_number"]
            task.save()
            print("custom_task_sequence_number : ", task.custom_task_sequence_number)
            # task.reload()

        # Commit all changes after the loop completes
        frappe.db.commit()

        # update the estimated time in days
        # update_estimated_time_in_days(template_task_list, project_task_list)
        # print("project_task_list", project_task_list)

    except Exception as e:
        frappe.throw(f"An error occurred while updating task sequence: {str(e)}")


# @frappe.whitelist()
# def update_estimated_time_in_days(template_task_list, project_task_list):
#     try:
#         # Get per_day_hours
#         per_day_hours_dict = get_default_shift_hours()

#         # Check if per_day_hours_dict is valid, set per_day_hours to 8
#         if per_day_hours_dict and "per_day_hours" in per_day_hours_dict:
#             per_day_hours = per_day_hours_dict["per_day_hours"]
#         else:
#             per_day_hours = 8

#         print("\n\n\n\n Per day hours: ", per_day_hours)

#         # Iterate through the template task list
#         for template_task in template_task_list:
#             template_idx = template_task["idx"]
#             template_task_id = template_task["task"]

#             # Fetch days
#             custom_expected_time_in_days = frappe.get_value(
#                 "Task", template_task_id, "custom_expected_time_in_days"
#             )

#             print("Template task days value: ", custom_expected_time_in_days)

#             # Find the corresponding project task with the matching custom_task_sequence_number (idx)
#             for project_task in project_task_list:
#                 if project_task["custom_task_sequence_number"] == template_idx:
#                     # Get the project task document
#                     project_task_doc = frappe.get_doc("Task", project_task["name"])

#                     # Update the project task's custom_expected_time_in_days
#                     project_task_doc.custom_expected_time_in_days = (
#                         custom_expected_time_in_days
#                     )

#                     # Calculate and update the expected time in hours
#                     project_task_doc.expected_time = (
#                         per_day_hours * custom_expected_time_in_days
#                     )

#                     # Save the document after updating both fields
#                     project_task_doc.save()

#                     print(
#                         f"Updated project task {project_task['name']} with custom_expected_time_in_days: {custom_expected_time_in_days} and expected_time: {project_task_doc.expected_time}"
#                     )

#         # Commit the database changes
#         frappe.db.commit()

#     except Exception as e:
#         frappe.throw(f"An error occurred while updating task sequence: {str(e)}")
