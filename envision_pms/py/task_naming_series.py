import frappe



# Create Task id tased on the parent child relation
@frappe.whitelist()
def generate_task_id(doc, event):
    # print("Called \n\n")
    if doc.is_new():
        parent_prefix = "TS"

        if doc.parent_task:
            # Generate a child task ID
            doc.name = generate_child_task_id(doc.parent_task)



def generate_child_task_id(parent_task_id):

    child_prefix = parent_task_id + "-"
    last_child_id = frappe.db.sql(
        """
        SELECT MAX(CAST(REPLACE(name, %s, '') AS UNSIGNED))
        FROM `tabTask`
        WHERE name LIKE %s
        """,
        (child_prefix, child_prefix + "%"),
    )

    # Calculate the next child task ID
    if last_child_id and last_child_id[0][0]:
        next_child_id = int(last_child_id[0][0]) + 1
    else:
        next_child_id = 1

    # Create new child task ID
    new_child_task_id = f"{child_prefix}{next_child_id:02d}"

    #  generated unique child ID
    while frappe.db.exists("Task", new_child_task_id):
        next_child_id += 1
        new_child_task_id = f"{child_prefix}{next_child_id:02d}"

    return new_child_task_id


# Create parent task id
def generate_parent_task_id(doc, parent_prefix):

    last_parent_id = frappe.db.sql(
        """
        SELECT MAX(CAST(REPLACE(name, %s, '') AS UNSIGNED))
        FROM `tabTask`
        WHERE name LIKE %s
        AND parent_task IS NULL
        """,
        (parent_prefix, parent_prefix + "%"),
    )

    # Calculate the next task ID
    if last_parent_id and last_parent_id[0][0]:
        next_parent_id = int(last_parent_id[0][0]) + 1
    else:
        next_parent_id = 1

    # Create new task ID
    new_task_id = f"{parent_prefix}{next_parent_id:06d}"

    # Check new task id already crteated or not
    while frappe.db.exists("Task", new_task_id):
        next_parent_id += 1
        new_task_id = f"{parent_prefix}{next_parent_id:06d}"
    return new_task_id




@frappe.whitelist()
def rename_task_id(task_name, event=None):
    set_task_allow_rename(True)
    task_doc = frappe.get_doc("Task", task_name)

    if not task_doc:
        frappe.throw(f"Task '{task_name}' does not exist.")

    if task_doc.parent_task:
        # Use the parent's ID for the new ID
        parent_task_id = task_doc.parent_task
        new_task_id = generate_child_task_id(parent_task_id)
       
        frappe.rename_doc(
            "Task",
            task_doc.name,
            new_task_id,
            merge=False,
        )


@frappe.whitelist()
def set_task_allow_rename(value):
    
    property_setter = frappe.db.get_value(
        "Property Setter", {"doc_type": "Task", "property": "allow_rename"}, "value"
    ) 

    # Convert value to string format ("1" for True, "0" for False)
    new_value = str(int(value))

    # If Property Setter doesn't exist, create a new Property setter
    if not property_setter:
        frappe.get_doc(
            {
                "doctype": "Property Setter",
                "doc_type": "Task",
                "property": "allow_rename",
                "property_type": "Check",
                "value": new_value,  
                "doctype_or_field": "DocType",
            }
        ).insert()

    # If Property Setter exists, update the value only if it's different
    elif property_setter != new_value:
        property_setter_doc = frappe.get_doc(
            "Property Setter", {"doc_type": "Task", "property": "allow_rename"}
        )
        property_setter_doc.value = new_value
        property_setter_doc.save()
