# __version__ = "0.0.1"

def monkey_patch():
    from erpnext.projects.doctype.task.task import Task
    from envision_pms.override.methods.update_time_and_costing import update_time_and_costing

    # Monkey patch Task
    Task.update_time_and_costing = update_time_and_costing


monkey_patch()
