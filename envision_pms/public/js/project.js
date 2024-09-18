frappe.ui.form.on("Project", {
  refresh: function (frm) {
    // frappe.msgprint("JS working ");
  },

  //   Change in the sales order
  custom_sales_orders: function (frm) {
    console.log("length", frm.doc.custom_sales_orders.length);

    if (frm.doc.custom_sales_orders.length === 1) {
      frappe.call({
        method: "envision_pms.py.get_data.get_customer",
        args: {
          sales_order: frm.doc.custom_sales_orders[0]["sales_order"],
        },
        callback: function (r) {
          if (!r.exc) {
            frm.set_value("customer", r.message);
            // Refresh the child table after adding rows
            frm.refresh_field("customer");
          }
        },
      });
    }
  },

  customer: function (frm) {
    frm.set_query("custom_sales_orders", function () {
      return {
        filters: {
          customer: frm.doc.customer,
        },
      };
    });
  },
});
