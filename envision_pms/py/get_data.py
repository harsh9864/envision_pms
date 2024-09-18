import frappe


@frappe.whitelist()
def get_customer(sales_order):
    print("\n\n sales_order: ", sales_order)
    sales_order_details = frappe.get_doc("Sales Order", sales_order, "customer")

    print("\n\n Customer", sales_order_details.customer)
    return sales_order_details.customer


@frappe.whitelist()
def get_default_shift_hours():
    try:
        # Fetch man days details
        man_days_details = frappe.get_doc(
            "Define Man Days Price",
            ["from_date", "per_day_hours"],
        )

        if not man_days_details:
            frappe.throw(
                ("Default per day shift hours not found"), title=("Missing Data")
            )

        # Return the fetched details
        return {
            "per_day_hours": man_days_details.per_day_hours,
        }

    except frappe.DoesNotExistError as e:
        frappe.throw(("Document not found: {0}").format(str(e)), title=("Not Found"))
