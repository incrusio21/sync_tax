from . import __version__ as app_version

app_name = "sync_tax"
app_title = "Sync Tax"
app_publisher = "DAS"
app_description = "Sync Tax deprint"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "das@gmail.com"
app_license = "MIT"

fixtures = [
	{"dt":"Client Script",
	"filters": [["name", "in", ["Journal Entry-Client","Purchase Invoice-Form","Stock Entry-Form","Material Request-Form"]]]
	},
	{"dt":"Custom Field",
	"filters": [["name", "in", ["Material Request-tax_status","Material Request-sync_pajak_name"]]]
	},
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/sync_tax/css/sync_tax.css"
# app_include_js = "/assets/sync_tax/js/sync_tax.js"

# include js, css files in header of web template
# web_include_css = "/assets/sync_tax/css/sync_tax.css"
# web_include_js = "/assets/sync_tax/js/sync_tax.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "sync_tax/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
"Purchase Order" : "public/js/custom_purchase_order.js",
"Material Request": "public/js/custom_material_request.js",
"Sales Order": "public/js/custom_sales_order.js",
"Delivery Note": "public/js/custom_delivery_note.js",
"Stock Entry": "public/js/custom_stock_entry.js",
"Purchase Receipt": "public/js/custom_purchase_receipt.js",
"Purchase Invoice": "public/js/custom_purchase_invoice.js",
"Sales Invoice": "public/js/custom_sales_invoice.js",
"Payment Entry": "public/js/custom_payment_entry.js",
"Journal Entry": "public/js/custom_journal_entry.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "sync_tax.install.before_install"
# after_install = "sync_tax.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "sync_tax.uninstall.before_uninstall"
# after_uninstall = "sync_tax.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sync_tax.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	# "*": {
	# 	"on_update": "method",
	# 	"on_cancel": "method",
	# 	"on_trash": "method"
	# }
	"Sync Log" :{
		"after_insert": "sync_tax.sync_tax.doctype.sync_log.sync_log.after_insert"
	}, 
	("Sales Order",'Purchase Order','Delivery Note', 'Stock Entry','Purchase Receipt', 'Purchase Invoice', 'Sales Invoice', 'Payment Entry', 'Journal Entry', 'Stock Reconciliation', 'Material Request'): {
		"on_submit": "sync_tax.custom.sync.create_sync_log",
		"validate": ["sync_tax.custom.sync.cek_status_pajak"],
		"autoname": "sync_tax.custom.sync.cek_tax_status",
		"on_cancel": "sync_tax.custom.sync.cancel_sync_log",
		"on_trash": "sync_tax.custom.sync.delete_sync_log",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"sync_tax.tasks.all"
#	],
#	"daily": [
#		"sync_tax.tasks.daily"
#	],
#	"hourly": [
#		"sync_tax.tasks.hourly"
#	],
#	"weekly": [
#		"sync_tax.tasks.weekly"
#	]
#	"monthly": [
#		"sync_tax.tasks.monthly"
#	]
# }

# Testing
# -------

# before_tests = "sync_tax.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "sync_tax.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "sync_tax.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"sync_tax.auth.validate"
# ]

