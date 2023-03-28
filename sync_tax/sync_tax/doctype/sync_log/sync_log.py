# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json

from sync_tax.custom.sync import repair_gl_sle_entry

class SyncLog(Document):
	pass
	# def after_insert(self):	
	# 	cek_apakah_tujuan = frappe.db.sql(""" SELECT * FROM `tabEvent Producer` """)
	# 	if len(cek_apakah_tujuan) > 0:
	# 		sync_baru = json.loads(self.data)
	# 		sync_baru["sync_pajak_name"] = self.docname
	# 		doc_sync_baru = frappe.get_doc(sync_baru)
	# 		doc_sync_baru.__islocal = 1
	# 		doc_sync_baru.flags.name_set = 1			
	# 		doc_sync_baru.flags.ignore_permissions=True
	# 		# doc_sync_baru.save()
	# 		doc_sync_baru.submit()

			# if(sync_baru['doctype'] not in ['Sales Order', 'Purchase Order']):
			# 	repair_gl_sle_entry(sync_baru['doctype'],sync_baru['name'])

def after_insert(self, method):	
	cek_apakah_tujuan = frappe.db.sql(""" SELECT * FROM `tabEvent Producer` """)
	if len(cek_apakah_tujuan) > 0:
		if(self.update_type=="Cancel"):
			doc = frappe.get_doc(self.doc_type, self.docname)
			if (doc.docstatus==1):
				doc.cancel()
		elif(self.update_type=="Delete"):
			doc = frappe.get_doc(self.doc_type, self.docname)
			if (doc.docstatus==2 or doc.docstatus==0):
				doc.delete()
		else:
			cek = frappe.db.exists(self.doc_type,self.docname)
			if (cek):
				doccek = frappe.get_doc(self.doc_type,self.docname)
				if(doccek.docstatus==0):
					doccek.delete()
					frappe.db.commit()
					
			sync_baru = json.loads(self.data)
			sync_baru["sync_pajak_name"] = self.docname
			doc_sync_baru = frappe.get_doc(sync_baru)
			doc_sync_baru.__islocal = 1
			# doc_sync_baru.amended_from = ""
			doc_sync_baru.flags.name_set = 1			
			doc_sync_baru.flags.ignore_permissions=True
			# doc_sync_baru.save()
			if(doc_sync_baru.doctype in ['Pricing Rule','Customer', 'Address', 'Contact', 'Pricing Rule','Industry Type']):
				doc_sync_baru.save()
			else:			
				doc_sync_baru.submit()

			if(sync_baru['doctype'] not in ['Sales Order', 'Purchase Order']):
				repair_gl_sle_entry(sync_baru['doctype'],sync_baru['name'])