frappe.ui.form.on("Timesheet Detail", {
  //   Change in the sales order
  //   custom_remaining_hrs
  task: function (frm, cdt, cdn) {
    let current_row = locals[cdt][cdn];
    // console.log("current_row", current_row);
    console.log("Task", current_row.task);

    frappe.call({
      method:
        "envision_pms.py.calculate_remaining_hrs.calculate_task_remaining_hrs",
      args: {
        task: current_row.task,
      },
      callback: function (r) {
        if (!r.exc) {
          // Refresh the child table after adding rows
          console.log("Entire",r.message);
          remaining_hrs = r.message.remaining_hrs || 0;
          expected_hrs = r.message.expected_hrs || 0;
          console.log(expected_hrs  );
          // current_row.custom_remaining_hrs = remaining_hrs;
          frappe.model.set_value(
            cdt,
            cdn,
            "custom_remaining_hrs",
            remaining_hrs
          );

          frappe.model.set_value(cdt, cdn, "expected_hours", expected_hrs);
        }
      },
    });
  },

  //   customer: function (frm) {
  //     frm.set_query("custom_sales_orders", function () {
  //       return {
  //         filters: {
  //           customer: frm.doc.customer,
  //         },
  //       };
  //     });
  //   },
});

// function calculate_remaining_hrs(frm,cdt,cdn){
//     current_row = locals[cdt][cdn];

// }
