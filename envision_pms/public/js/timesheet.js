frappe.ui.form.on("Timesheet Detail", {
  task: function (frm, cdt, cdn) {
    let current_row = locals[cdt][cdn];
    console.log("Task", current_row.task);
    if (current_row.task) {
      calculate_remaining_hrs(cdt, cdn, current_row.task);
    }
  },

  time_logs_add: function (frm, cdt, cdn) {
    let current_row = locals[cdt][cdn];
    console.log("Task", current_row.task);
    if (current_row.task) {
      calculate_remaining_hrs(cdt, cdn, current_row.task);
    }
  },
});

// Function to calculate remaining hours
function calculate_remaining_hrs(cdt, cdn, task) {
  frappe.call({
    method:
      "envision_pms.py.calculate_remaining_hrs.calculate_task_remaining_hrs",
    args: {
      task: task,
    },
    callback: function (r) {
      if (!r.exc) {
        console.log("Entire", r.message);
        let remaining_hrs = r.message.remaining_hrs || 0;
        let expected_hrs = r.message.expected_hrs || 0;
        frappe.model.set_value(cdt, cdn, "custom_remaining_hrs", remaining_hrs);
        frappe.model.set_value(cdt, cdn, "expected_hours", expected_hrs);
      }
    },
  });
}
