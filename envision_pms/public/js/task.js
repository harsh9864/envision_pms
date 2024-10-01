// Global variable to store per_day_hour
let per_day_hour = null;

// Function to get default per hour once and store in the global variable
function get_default_per_hour(callback) {
  if (per_day_hour === null) {
    frappe.call({
      method: "envision_pms.py.get_data.get_default_shift_hours",
      callback: function (r) {
        if (!r.exc) {
          // Store the result in the global variable
          per_day_hour = r.message.per_day_hours;
          //  console.log("Fetched and stored Per Day Hour:", per_day_hour);

          // Execute callback once data is fetched
          if (callback) callback();
        }
      },
    });
  } else {
    //  console.log("Using cached Per Day Hour:", per_day_hour);

    // Execute callback immediately if data is already fetched
    if (callback) callback();
  }
}

// Convert days into hours using per_day_hour
function convert_days_into_hours(days) {
  // Ensure that per_day_hour is available before using it
  if (per_day_hour === null) {
    // Return a default value or an error if per_day_hour is not yet fetched
    console.error("Per Day Hour not available. Fetching now...");

    // Default 8 hr,if per_day_hour is not available
    return days * 8;
  }
  // console.log("per_day_hour", per_day_hour);
  return days * per_day_hour; // Use fetched per_day_hour value
}

frappe.ui.form.on("Task", {
  //   refresh: function (frm) {
  //     frappe.msgprint("JS working ");
  //   },

  custom_expected_time_in_days: function (frm) {
    get_default_per_hour(function () {
      try {
        //  let current_row = locals[cdt][cdn];
        console.log("function call");

        let days = frm.doc.custom_expected_time_in_days || 0;

        // Use per_day_hour in conversion
        let hours = convert_days_into_hours(days);
        // console.log("Hours", hours);

        frm.set_value("expected_time", Math.round(hours));
      } catch (error) {
        console.error(`Error updating ${day_field} to ${hour_field}:`, error);
      }
    });
  },

  onload_post_render: function (frm) {
    console.log("onload_post_render event call");

    if (frm.doc.custom_task_sequence_number === 0) {
      console.log("Frappe called in side if ");
      if (frm.doc.template_task) {
        console.log("Frappe called ");

        frappe.call({
          method:
            "envision_pms.py.set_sequence_number.set_sequence_number_to_tasks",
          args: {
            current_task: frm.doc.name,
            project: frm.doc.project,

            // exp_start_date: frm.doc.exp_start_date,
          },
          callback: function (r) {
            if (!r.exc) {
              frm.refresh();
              console.log(
                " IF Sequene number set ",
                frm.doc.custom_task_sequence_number
              );

              // frappe.msgprint("Sequene number set");
            } // End of callback if condition
          }, // End of callback function
        }); // End frappe call
      }
    } // end if condition for sequence number !==0
    else {
      console.log(
        " Else Sequene number already set ",
        frm.doc.custom_task_sequence_number
      );
    }

    frm.refresh();
    console.log("Sequence number ", frm.doc.custom_task_sequence_number);
  },

  exp_start_date: function (frm) {
    if (frm.doc.template_task) {
      console.log("Template task if call");
      if (frm.doc.custom_task_sequence_number === 1) {
        frappe.call({
          method:
            "envision_pms.py.calculate_exp_start_and_end_dates.calculate_exp_start_and_exp_end_date",
          args: {
            // current_task: frm.doc.name,
            project: frm.doc.project,
            //  sequence_number: frm.doc.custom_task_sequence_number,
            exp_start_date: frm.doc.exp_start_date,
            company: frm.doc.company,
            // exp_start_date: frm.doc.exp_start_date,
          },
          callback: function (r) {
            if (!r.exc) {
              console.log("date updated ");
            }
          },
        });
      } else {
        console.log("Not in the first Template first Task");
        frappe.msgprint("Go to the first Template task");
      }
    }
  }, // End of exp_start_date event
}); // End Frappe.form.ui
