frappe.ui.form.on("Project Template Task", {
  custom_fetch_all_related_tasks: function (frm, cdt, cdn) {
    let current_row = locals[cdt][cdn];

    // Check if task is selected
    if (!current_row.task) {
      frappe.msgprint(("Please select a task to fetch related tasks."));
      return;
    }
    if (current_row.custom_fetch_all_related_tasks == true) {
      // Make the call to fetch related tasks
      frappe.call({
        method: "envision_pms.py.get_related_tasks.fetch_related_tasks", 
        args: {
          task_name: current_row.task,
        },
        callback: function (response) {
          try {
            if (response.message && response.message.length > 0) {
              // Check if the response contains tasks
              response.message.forEach((task) => {
                // Check if the task already exists in the "tasks" child table
                const existing_task = frm.doc.tasks.find(
                  (t) => t.task === task.name
                );

                if (!existing_task) {
                  // Find the index of the current row
                  const current_row_idx = current_row.idx;
                  // console.log("current_row_idx,", current_row_idx);

                  // Add the new row just after the current row
                  let new_row = frm.add_child(
                    "tasks",
                    undefined,
                    current_row_idx + 1
                  );

                  // Set values for the new task row
                  frappe.model.set_value(
                    new_row.doctype,
                    new_row.name,
                    "task",
                    task.name
                  );
                  frappe.model.set_value(
                    new_row.doctype,
                    new_row.name,
                    "subject",
                    task.subject
                  );
                } else {
                  // If task is already present, show a message
                  frappe.msgprint(
                    (
                      "Task: " +
                        task.name +
                        " is already present in the task table."
                    )
                  );
                }
              });
              frm.refresh_field("tasks");
            } else {
              frappe.msgprint(
                ("No related tasks found for the selected task.")
              );
            }
          } catch (err) {
            // Catch and handle any error during the callback
            frappe.msgprint(
              ("An error occurred while processing the related tasks.")
            );
            console.error("Error during related tasks processing: ", err);
          }
        },
        error: function (err) {
          // Catch and handle any error during the API call
          frappe.msgprint(
            ("An error occurred while fetching related tasks.")
          );
          console.error("Error fetching related tasks: ", err);
        },
        // Show loading indicator while the request is being processed
        freeze: true,
        freeze_message: ("Fetching related tasks..."),
      });
    }
  },
});
