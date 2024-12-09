import frappe


@frappe.whitelist()
def fetch_related_tasks(task_name):

    # Fetch all related tasks, including hierarchical and dependent tasks.

    if not task_name:
        frappe.throw("Task name is required.")

    # Fetch tasks
    hierarchical_tasks = get_hierarchical_tasks(task_name)
    dependent_tasks = get_dependent_tasks(task_name)

    # Combine tasks,Remove duplicates
    all_tasks = hierarchical_tasks + dependent_tasks
    unique_tasks = {task["name"]: task for task in all_tasks}.values()

    

    return list(unique_tasks)


def get_hierarchical_tasks(task_name):
    # Recursively fetch all tasks in the hierarchy starting from the given task, and return them in reverse order.
    tasks = []
    tasks_to_process = [task_name]
    # print("\n\ntasks_to_process: ", tasks_to_process)

    while tasks_to_process:
        current_task = tasks_to_process.pop(0)
        # print("\n\current_task: ", current_task)

        child_tasks = frappe.get_all(
            "Task", filters={"parent_task": current_task}, fields=["name", "subject"]
        )
        tasks.extend(child_tasks)
        tasks_to_process.extend([child["name"] for child in child_tasks])

    # Reverse the order of tasks
    # print("Task : ", tasks)
    return tasks[::-1]


def get_dependent_tasks(task_name):
    # Fetch all dependent tasks starting from the given task and its sub-levels using a while loop.

    dependent_tasks = []

    # Initialize the queue with the starting task
    tasks_to_process = [task_name]
    print("\n\ntasks_to_process: ", tasks_to_process)

    while tasks_to_process:
        # Process the first task in the queue
        current_task = tasks_to_process.pop(0)
        print("\n\current_task: ", current_task)

        # Fetch dependencies for the current task
        dependencies = frappe.get_all(
            "Task Depends On", filters={"parent": current_task}, fields=["task"]
        )

        for dependency in dependencies:
            # Fetch the dependent task document
            task = frappe.get_doc("Task", dependency["task"])

            # Check if the task's parent_task is empty (i.e., the task is not a child task)
            if not task.parent_task:
                # Avoid adding duplicate tasks to the dependent_tasks list
                if not any(d["name"] == task.name for d in dependent_tasks):
                    dependent_tasks.append({"name": task.name, "subject": task.subject})

                # Add this task to the queue for further processing
                tasks_to_process.append(task.name)

    # Reverse the list of dependent tasks to return in reverse order
    return dependent_tasks[::-1]
