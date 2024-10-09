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
          

          // Execute callback once data is fetched
          if (callback) callback();
        }
      },
    });
  } else {
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
  return days * per_day_hour; 
}

frappe.ui.form.on("Task", {
  custom_expected_time_in_days: function (frm) {
    get_default_per_hour(function () {
      try {
        let days = frm.doc.custom_expected_time_in_days || 0;

        // Use per_day_hour in conversion
        let hours = convert_days_into_hours(days);

        frm.set_value("expected_time", Math.round(hours));
      } catch (error) {
        console.error(`Error updating ${day_field} to ${hour_field}:`, error);
      }
    });
  },

  onload_post_render: function (frm) {
    if (frm.doc.custom_task_sequence_number === 0) {
      if (frm.doc.template_task) {
        frappe.call({
          method:
            "envision_pms.py.set_sequence_number.set_sequence_number_to_tasks",
          args: {
            current_task: frm.doc.name,
            project: frm.doc.project,
          },
          callback: function (r) {
            // cur_frm.reload_doc();
            if (!r.exc) {
              frm.reload_doc();
            
            } // End of callback if condition
          }, // End of callback function
        }); // End frappe call
      }
    } // end if condition for sequence number !==0
  },

  //  Event when exp start date change   
  exp_start_date: function (frm) {
    // Check Task is templet task or not 
    if (frm.doc.template_task) {
      // Check template task sequence no
      if (frm.doc.custom_task_sequence_number === 1) {
        // confirmation message to auto calculate exp start and end dates
        frappe.confirm(
          "Are you want to calculate expected start and end dates for other template tasks ?",
          function () {
            frappe.call({
              method:
                "envision_pms.py.calculate_exp_start_and_end_dates.calculate_exp_start_and_exp_end_date",
              args: {
                project: frm.doc.project,
                //  sequence_number: frm.doc.custom_task_sequence_number,
                exp_start_date: frm.doc.exp_start_date,
                company: frm.doc.company,
                // exp_start_date: frm.doc.exp_start_date,
              },
              callback: function (r) {
                if (!r.exc) {
                  // Reload the current form 
                  cur_frm.reload_doc();

                } // End of callback if condition
              }, // End of callback  function
            }); // End of frappe call
          }
        ); // End of confirmation message and function
      } // End of if condition ( template task sequence no)

      // else if (
      //   frm.doc.custom_task_sequence_number > 1 &&
      //   (!frm.doc.exp_end_date ||
      //     frm.doc.exp_end_date == "" ||
      //     frm.doc.exp_end_date == undefined ||
      //     frm.doc.exp_end_date == null)
      // ) {
      //   console.log("Not in the first Template Task");
      //   frappe.msgprint(
      //     "Action required: Please go to the first template task to proceed with setting expected start and end dates."
      //   );
      // }
    }  // End of if condition is task is template task or not 
  }, // End of exp_start_date event
}); // End Frappe.form.ui
