from __future__ import unicode_literals
import frappe
import json
import frappe.utils

from datetime import date

from frappe.frappeclient import FrappeClient

@frappe.whitelist()
def repair_gl_sle_entry(doctype, docname):
    docu = frappe.get_doc(doctype, docname)
    frappe.db.sql(""" UPDATE `tabSingles` SET value = 1 WHERE field = "allow_negative_stock" """)
    delete_sl = frappe.db.sql(""" DELETE FROM `tabStock Ledger Entry` WHERE voucher_no = "{}" """.format(docname))
    delete_gl = frappe.db.sql(""" DELETE FROM `tabGL Entry` WHERE voucher_no = "{}" """.format(docname))    

    if docu.doctype in ['Delivery Note', 'Stock Entry', 'Stock Recon','Purchase Receipt']:
        docu.update_stock_ledger()        
    elif docu.doctype in ['Purchase Invoice', 'Sales Invoice']:
        if docu.update_stock:
            docu.update_stock_ledger()              

    if docu.doctype in ['Delivery Note', 'Sales Invoice', 'Payment Entry', 'Purchase Receipt', 'Purchase Invoice', 'Journal Entry', 'Stock Entry', 'Stock Recon']:
        docu.make_gl_entries()

    if docu.doctype in ['Delivery Note', 'Stock Entry', 'Stock Recon','Purchase Receipt']:        
        docu.repost_future_sle_and_gle()
    elif docu.doctype in ['Purchase Invoice', 'Sales Invoice']:
        if docu.update_stock:            
            docu.repost_future_sle_and_gle()                   
    
    frappe.db.sql(""" UPDATE `tabSingles` SET value = 0 WHERE field = "allow_negative_stock" """)
	# print("Membenarkan LEDGER dari {} - DONE ".format(docname))
    frappe.db.commit()

def create_sync_log(self, method):
    if self.doctype == 'Material Request':
        cek_apakah_sumber = frappe.db.sql(""" SELECT * FROM `tabEvent Consumer` """)
        # frappe.msgprint(str(cek_apakah_sumber)+"tes123")
        if len(cek_apakah_sumber) > 0:
            # frappe.msgprint(str(method))
            doc = frappe.new_doc('Sync Log')
            doc.update_type = 'Create'
            doc.doc_type = self.doctype
            doc.docname = self.name
            # self.amended_from = ""
            doc.data = frappe.as_json(self)
            doc.save()
    elif self.tax_status=='Tax':
        cek_apakah_sumber = frappe.db.sql(""" SELECT * FROM `tabEvent Consumer` """)        
        # frappe.msgprint(str(cek_apakah_sumber)+"tes123")
        if len(cek_apakah_sumber) > 0:
            # frappe.msgprint(str(method))
            doc = frappe.new_doc('Sync Log')
            doc.update_type = 'Create'
            doc.doc_type = self.doctype
            doc.docname = self.name
            # self.amended_from = ""
            doc.data = frappe.as_json(self)
            doc.save()

def cancel_sync_log(self, method):
    cek_apakah_sumber = frappe.db.sql(""" SELECT * FROM `tabEvent Consumer` """)
    if self.doctype == 'Material Request':
        if len(cek_apakah_sumber) > 0:            
            doc = frappe.new_doc('Sync Log')
            doc.update_type = 'Cancel'
            doc.doc_type = self.doctype
            doc.docname = self.name
            doc.data = frappe.as_json(self)
            doc.save()
    elif self.tax_status=='Tax':
        if len(cek_apakah_sumber) > 0:            
            doc = frappe.new_doc('Sync Log')
            doc.update_type = 'Cancel'
            doc.doc_type = self.doctype
            doc.docname = self.name
            doc.data = frappe.as_json(self)
            doc.save()

def delete_sync_log(self, method):
    cek_apakah_sumber = frappe.db.sql(""" SELECT * FROM `tabEvent Consumer` """)
    if self.doctype == 'Material Request':                
        if len(cek_apakah_sumber) > 0:            
            doc = frappe.new_doc('Sync Log')
            doc.update_type = 'Delete'
            doc.doc_type = self.doctype
            doc.docname = self.name
            doc.data = frappe.as_json(self)
            doc.save()
    elif self.tax_status=='Tax':
        if len(cek_apakah_sumber) > 0:            
            doc = frappe.new_doc('Sync Log')
            doc.update_type = 'Delete'
            doc.doc_type = self.doctype
            doc.docname = self.name
            doc.data = frappe.as_json(self)
            doc.save()

@frappe.whitelist()
def debug_sync_log(name):
    today = date.today()
    sync_log = frappe.get_doc("Sync Log",name)
    sync_baru = json.loads(sync_log.data)
    sync_baru["sync_pajak_name"] = sync_log.docname
    doc_sync_baru = frappe.get_doc(sync_baru)

    # customer = frappe.db.sql(""" UPDATE `tabCustomer` SET disabled = '0' WHERE NAME = "%s" """ % (doc_sync_baru.customer))

    if doc_sync_baru.doctype in ['Purchase Receipt','Purchase Invoice','Delivery Note','Sales Invoice','Stock Entry','Stock Reconciliation','POS Invoice']:
        if doc_sync_baru.posting_date != today:
            doc_sync_baru.set_posting_time = 1
    if doc_sync_baru.doctype in ['Purchase Order']:
        for i in doc_sync_baru.items:
            if i.material_request:
                i.material_request = ""
                i.material_request_item = ""
    if doc_sync_baru.amended_from:
            doc_sync_baru.amended_from = ""

    if doc_sync_baru.doctype in ['Sales Order']:
        name_biaya_order_item = frappe.db.sql(""" SELECT NAME FROM `tabBiaya Order Item` WHERE parent = '{}' """.format(doc_sync_baru.name))
        if(name_biaya_order_item):
                doc_sync_baru.biaya_order_item = []
        name_sales_order_dp = frappe.db.sql(""" SELECT NAME FROM `tabSales Order DP` WHERE parent = '{}' """.format(doc_sync_baru.name))
        if(name_sales_order_dp):
                doc_sync_baru.dp_table = []

    doc_sync_baru.__islocal = 1
    doc_sync_baru.flags.name_set = 1
    doc_sync_baru.flags.ignore_permissions=True
    doc_sync_baru.submit()
    # customer = frappe.db.sql(""" UPDATE `tabCustomer` SET disabled = '1' WHERE NAME = "%s" """ % (doc_sync_baru.customer))
	# repair_gl_sle_entry(sync_baru['doctype'],sync_baru['name'])

@frappe.whitelist()
def debug_sync_log_master():
    for i in ['32a20592ff','13f395c1f9','539414a72a']:
        sync_log = frappe.get_doc("Sync Log",i)
        sync_baru = json.loads(sync_log.data)
        doc_sync_baru = frappe.get_doc(sync_baru)

        doc_sync_baru.__islocal = 1
        doc_sync_baru.flags.name_set = 1
        doc_sync_baru.flags.ignore_permissions=True
        doc_sync_baru.save()

@frappe.whitelist()
def on_off_disabled_item():
    item_list = ['CNBL-18035', 'CNBL-18044', 'CNBL-18059', 'CNBL-18066', 'CNBL-18067', 'CNBL-18074', 'CNBL-18080', 'CNBL-18083', 'CNBL-18090', 'CNBL-18091', 'CNBL-18092', 'CNBL-18093', 'CNBL-18094', 'CNHR-19018', 'CNHR-19021', 'CNHT-74001', 'CNME-23001', 'CNSE-82029', 'CNSP-03554', 'CNSP-3818', 'CNVC-01506', 'CNYW-00169', 'CNYW-00211', 'CPBC-11501', 'CPBC-11502', 'CPBC-11503', 'CPBC-11504', 'CPBC-11506', 'CPBC-11507', 'CPBC-11508', 'CPBC-11509', 'CPCE-10503', 'CPCE-10505', 'CPCE-10506', 'CPCL-08003', 'CPCL-08011', 'CPCL-08047', 'CPCL-08053', 'CPCL-08071', 'CPCL-08074', 'CPPI-19544', 'CPPI-19547', 'CPPI-19551', 'CPPI-19561', 'CPPI-19562', 'CPPI-19563', 'CPPI-19564', 'CPPK-13502', 'CPSC-05610', 'CPSC-05611', 'CPSC-05612', 'CPSC-05613', 'CPVC-01503', 'CPWJ-00599', 'CPWJ-00601', 'IKGM-00001', 'MNBL-63505', 'MNBL-63507', 'MNFP-58001', 'MNFP-58002', 'MNHR-64002', 'MNHR-64003', 'MNTG-83001', 'MNYW-50019', 'MNYW-50042', 'MNYW-50050', 'MNYW-50058', 'MNYW-50059', 'MNYW-50069', 'MNYW-50074', 'MNYW-50082', 'MNYW-50086', 'MNYW-50101', 'MNYW-50102', 'MNYW-50103', 'MNYW-50118', 'MNYW-50160', 'MPMP-15028', 'MPTS-68014', 'MPTS-68027', 'MPYW-50165', 'NFN-00013', 'NFN-00014', 'SNBJ-11008', 'SNBJ-11011', 'SNBL-18053', 'SNBL-18106', 'SNIC-07507', 'SNIJ-92019', 'SNMU-24005', 'SNWJ-90501', 'SNWJ-90502', 'SNWJ-90503', 'SNWJ-90529', 'SNYW - 00229', 'SNYW-00184', 'SNYW-00222', 'SPAC-46004', 'SPAI-05614', 'SPAS-12042', 'SPAS-12045', 'SPCW-04511', 'SPDP-09510', 'SPSC-05585', 'SPSC-05592', 'SPSC-05598', 'SPSC-05599', 'SPSC-05604', 'SPSC-05618', 'SPSC-05619', 'SPSC-05624', 'SPSC-05631', 'SPST-05017', 'SPST-05018', 'SPTS-05609', 'SPTS-05621', 'SPWJ-00767', 'SPWJ-00768', 'SPWJ-00769', 'SPWJ-00770', 'SPWJ-00771', 'SPWJ-00772', 'SPWJ-00773', 'SPWJ-00775', 'SPYW-00199', 'VINYL FLEXI FRONTLITE CHINA 380 GRAM 3.2 X 70 M MATTE']

    for i in item_list:
        doc = frappe.get_doc('Item', i)
        doc.disabled = 0
        doc.save()

@frappe.whitelist()
def on_off_disabled_supplier():
    listX = ['WS','RO','PT KREASI DASATAMA','MK','KR','KNJ','JF','GMS','EK','DR','DJ','CM','BY','AD','2S']

    for i in listX:
        doc = frappe.get_doc('Supplier', i)
        doc.disabled = 0
        doc.save()

@frappe.whitelist()
def debug_customer():
    # for i in ['CUST-230206-00001','CUST-230204-00001','CUST-230203-00005','CUST-230203-00004','CUST-230203-00003','CUST-230203-00002']:
    # for i in ['LEAD-230203-013','LEAD-230203-012','LEAD-230203-023']:
    for i in ['PROMOTION SOLUTION','GARMEN & KONVEKSI','GENERAL TRADING','METAL WORKING','WOOD WORKING','PENDIDIKAN','LAIN-LAIN']:
        print (i, " START")
        get_doc = frappe.get_doc('Industry Type',i)
        doc_save = frappe.new_doc('Sync Log')
        doc_save.update_type = 'Add'
        doc_save.doc_type = get_doc.doctype
        doc_save.docname = get_doc.name
        doc_save.data = frappe.as_json(get_doc)
        doc_save.save()

@frappe.whitelist()
def debug_master_not_sync():
    for i in ['FJ-P-23-02-00008']:
        print (i, " START")
        get_doc = frappe.get_doc('Sales Invoice',i)
        doc_save = frappe.new_doc('Sync Log')
        doc_save.update_type = 'Add'
        doc_save.doc_type = get_doc.doctype
        doc_save.docname = get_doc.name
        doc_save.data = frappe.as_json(get_doc)
        doc_save.save()

@frappe.whitelist()
def debug_not_sync():
    # ['08a69e0de1', '645a2aa56e', '2555dc202b', '57844e955b', 'a366e43edd', '8faf64f895', 'e3a0b8aa28', 'e5d2ed117f', '807b9134e8', 'c73d1a4df8', '5a733548f0', 'cf22fecc8f', 'cbeb7dda93', '5ba063209b', 'e3f71fb189', '2c35f47cc5', 'ccb59a1be7', '5207401bb7', '2bd2f57a68', '6749b7dd4e', '4e7902812e', '2fd10e5195', '16b715f95b', '9d2e0f02ba', 'e1f6d2de99', '556568d6bf', '049f39f688', 'eda5aaec40', 'c182a67f47', 'cfb08a4b9e', '934eb6340e', '60cc3de21a', '03cd85cabf', '956849bdd9', '43264c16aa', 'cf8d6c40b4', '364edd69f3', '35b3fac117', '6815842d18', '41f74f0ee8', '6e0b9d8d92', 'de735b8a68', '8d9634e467', '4229ef446b', '58c155a97e', '2c2ec72d56', 'd405ed13f4', 'a709b27c49', 'fbe839c4b9', 'd34828f4b1', 'c7350e104c', 'bcff8a6549', '9576f6cc79', '6c9a577998', '04ede50f47', 'b197ea765e', '8eff33c29a', 'c62d28641d', '1b953d92ca', '20d7640e51', '3a1212d8fe', '64e03884eb', '2ffe91487d', '0b137077ef', '1eab6b7645', '0a00de30f3', '6373a23c35', 'a165bb7e2d', '2f40dddb5c', '46c89ddd73', 'e68b430438', 'a1ed74045c', '6c6c281d39', '40eaf1d1ca', 'c5048ee1dd', '7ff0b9d106', '865dceed6a', '7bfd750476', '59f7e43e70', 'bc80b9049f', '39f3f1c0ff', '64604640a3', '81ef1f6ce8', '3045992828', '18f739a145', '4e5caed46a', '58be14a156', 'f2f48a3c74', '386313664b', '57bd89c5ef', '1e14262cc2', '50b9f8ec52', 'bb9a86fdaf', '9da115ea81', '0dffeb6e8f', 'c9e3da08a9', '08e73d11be', '108c0c4f1a', 'adc23e54c5', '1f817e41bf', 'a26aa4ba0c', '54fae1241b', '294d8b3e59', '885c54205a', 'c3bf5dd5d3', '1c7e418e36', '180afd7909', '8cd6dda369', '96824b073d', '5e497966dd', '930123d68b', '4e186d0177', 'e28ff3570b', '0957de3049', '992fcf9b1a', 'a9d64687ee', 'e62f5ed3d3', 'c4d623427a', 'd63bdf9e31', '12000b8917', '7de124a83d', '47fb9c9e6b', '45522f9b1d', '3a15c564e3', '0f79140d78', '0d541a2106', 'e1bd43f6d2', '6b5a82abd8', '148c67fc40', '9cfa477045', '7426a53bd7', 'fee476619b', 'e995812060', '081bf7fcab', '2aad5557d0', '69fe91804a', '35b53176e2', '86b68ed377', '0d0d5b0aef', '727315fee3', '99e6147466', 'feaaa180a5', '3f6381629a', '3edd42f5f4', '35c0286412', '3c7ae2d3be', '5b87503cb0', 'b06e569669', 'd81e6a9186', 'f2aefc2b7a', '072b9c3507', '9ce8cdff5e', '9662069e5d', 'ff8ca8c7b9', 'efe5d37803', '272933c111', 'b15434a261', 'c06bdf01ea', '32a000868a', 'eedcfdfdab', 'ba77c0f9f0', '25667a50b4', '91ef82ad25', '68052f97d0', 'c94fcd769c', '76b1738f7e', '92d866b39a', '9bfd15b1e7', 'b42afa4b6d', 'b73dd3a919', 'ae2cdf8558']
    # '2555dc202b', '57844e955b', 'a366e43edd', '8faf64f895', 'e3a0b8aa28', 
    # 'e5d2ed117f','2555dc202b',         '807b9134e8', 'c73d1a4df8',      '5a733548f0', 'cf22fecc8f', 'cbeb7dda93', '5ba063209b', 'e3f71fb189', '2c35f47cc5', 'ccb59a1be7',       '5207401bb7', 
    # '807b9134e8', 'c73d1a4df8' temp '2bd2f57a68', '6749b7dd4e', '4e7902812e', '2fd10e5195', '16b715f95b', '9d2e0f02ba', 'e1f6d2de99', '556568d6bf', '049f39f688', 'c182a67f47', 'cfb08a4b9e', '03cd85cabf', '43264c16aa', 'cf8d6c40b4', '364edd69f3', '35b3fac117', '6815842d18', '41f74f0ee8', '6e0b9d8d92', 'de735b8a68', '8d9634e467', '4229ef446b', '58c155a97e', '2c2ec72d56', 'd405ed13f4', 'a709b27c49', 'fbe839c4b9', 'd34828f4b1', 'c7350e104c', 'bcff8a6549', '9576f6cc79', '6c9a577998', '04ede50f47', 'b197ea765e', '8eff33c29a', 'c62d28641d', '1b953d92ca', '20d7640e51', '3a1212d8fe', '64e03884eb', '2ffe91487d', '0b137077ef', '1eab6b7645', '0a00de30f3', '6373a23c35', 'a165bb7e2d', '2f40dddb5c', '46c89ddd73', 'e68b430438', 'a1ed74045c', '6c6c281d39', '40eaf1d1ca', 'c5048ee1dd', '7ff0b9d106', '865dceed6a', '7bfd750476', '59f7e43e70', 'bc80b9049f', '39f3f1c0ff', '64604640a3', '81ef1f6ce8', '3045992828', '18f739a145', '4e5caed46a', '58be14a156', 'f2f48a3c74', '386313664b', '57bd89c5ef', '1e14262cc2', '50b9f8ec52', 'bb9a86fdaf', '9da115ea81', '0dffeb6e8f', 'c9e3da08a9', '08e73d11be', '108c0c4f1a', 'adc23e54c5', '1f817e41bf', 'a26aa4ba0c', '54fae1241b', '294d8b3e59', '885c54205a', 'c3bf5dd5d3', '1c7e418e36', '180afd7909', '8cd6dda369', '96824b073d', '5e497966dd', '930123d68b', '4e186d0177', 'e28ff3570b', '0957de3049', '992fcf9b1a', 'a9d64687ee', 'e62f5ed3d3', 'c4d623427a', 'd63bdf9e31', '12000b8917', '47fb9c9e6b', '45522f9b1d', '3a15c564e3', '0f79140d78', '0d541a2106', 'e1bd43f6d2', '6b5a82abd8', '148c67fc40', '9cfa477045', '7426a53bd7', 'fee476619b', 'e995812060', '081bf7fcab', '2aad5557d0', '69fe91804a', '35b53176e2', '86b68ed377', '0d0d5b0aef', '727315fee3', '99e6147466', 'feaaa180a5', '3f6381629a', '3edd42f5f4', '35c0286412', '3c7ae2d3be', '5b87503cb0', 'b06e569669', 'd81e6a9186', 'f2aefc2b7a', '072b9c3507', '9ce8cdff5e', '9662069e5d', 'ff8ca8c7b9', 'efe5d37803', '272933c111', 'b15434a261', 'c06bdf01ea', '32a000868a', 'eedcfdfdab', 'ba77c0f9f0', '25667a50b4', '91ef82ad25', '68052f97d0', 'c94fcd769c', '76b1738f7e', '92d866b39a', '9bfd15b1e7', 'b42afa4b6d', 'b73dd3a919', 'ae2cdf8558'
    # '5207401bb7','807b9134e8', 'c73d1a4df8'

    # SO :'b197ea765e','c62d28641d','7ff0b9d106','54fae1241b','d81e6a9186'
    # PO : 'a366e43edd','2c35f47cc5','556568d6bf','eda5aaec40','c182a67f47','108c0c4f1a','47fb9c9e6b','45522f9b1d','0d541a2106','272933c111','91ef82ad25','68052f97d0'    
    # PREC : '8faf64f895','ccb59a1be7','5207401bb7','4e7902812e','049f39f688','cfb08a4b9e','934eb6340e','6c9a577998','386313664b','adc23e54c5','3a15c564e3','0f79140d78','e1bd43f6d2','9bfd15b1e7','b42afa4b6d'
    # PINV : '865dceed6a','59f7e43e70', 'bc80b9049f','39f3f1c0ff','64604640a3','81ef1f6ce8', '8cd6dda369','96824b073d','9cfa477045','32a000868a','eedcfdfdab'
    # SKIP PINV : '180afd7909' NUNGGU PE ACC-PAY-P-23-01-00120
    # DN : '2bd2f57a68','2fd10e5195','60cc3de21a','03cd85cabf','3045992828','08e73d11be','5e497966dd','6b5a82abd8','b73dd3a919','ae2cdf8558'
    # SINV  : '6749b7dd4e',43264c16aa
    # PE : 'e638ab1581', dfd15d16d3, a4a37ee8a9, '9d2e0f02ba','4e5caed46a','20d7640e51','57bd89c5ef','9662069e5d',
    # PE EROR :   Allocated Amount cannot be greater than outstanding amount.
    # JE : '0b137077ef','1eab6b7645','0a00de30f3','6373a23c35','a165bb7e2d','50b9f8ec52','c9e3da08a9','a9d64687ee','e62f5ed3d3','c94fcd769c','76b1738f7e','92d866b39a'
    # JE EROR : 'c4d623427a' frappe.exceptions.ValidationError: Outstanding for ACC-JV-23-01-00085 cannot be less than zero (-125.000,00)
    # repair_gl_sle_entry('Purchase Receipt','MAT-PRE-P-2023-00048')
    for i in ['c4d623427a']:
        print (i, " START")
        get_doc = frappe.get_doc('Sync Log',i)
        clientroot = FrappeClient("https://deprintz13tax.digitalasiasolusindo.com/","administrator","Rahasiakit@")
        clientdoc = clientroot.get_doc(get_doc.doc_type,get_doc.docname)
        if(clientdoc):
            print ('submit')
            clientroot.submit(clientdoc)
        else:
            print('create')
            clientroot.insert(get_doc)
        # clientroot.insert(get_doc)
        print (i, " DONE")

@frappe.whitelist()
def create_sync_log_new():
    for i in ['59ff2c52e2','08a69e0de1', '645a2aa56e', '2555dc202b', '57844e955b', 'a366e43edd', '8faf64f895', 'e3a0b8aa28', 'e5d2ed117f', '807b9134e8', 'c73d1a4df8', '5a733548f0', 'cf22fecc8f', 'cbeb7dda93', '5ba063209b', 'e3f71fb189', '2c35f47cc5', 'ccb59a1be7', '5207401bb7', '2bd2f57a68', '6749b7dd4e', '4e7902812e', '2fd10e5195', '16b715f95b', '9d2e0f02ba', 'e1f6d2de99', '556568d6bf', '049f39f688', 'eda5aaec40', 'c182a67f47', 'cfb08a4b9e', '934eb6340e', '60cc3de21a', '03cd85cabf', '956849bdd9', '43264c16aa', 'cf8d6c40b4', '364edd69f3', '35b3fac117', '6815842d18', '41f74f0ee8', '6e0b9d8d92', 'de735b8a68', '8d9634e467', '4229ef446b', '58c155a97e', '2c2ec72d56', 'd405ed13f4', 'a709b27c49', 'fbe839c4b9', 'd34828f4b1', 'c7350e104c', 'bcff8a6549', '9576f6cc79', '6c9a577998', '04ede50f47', 'b197ea765e', '8eff33c29a', 'c62d28641d', '1b953d92ca', '20d7640e51', '3a1212d8fe', '64e03884eb', '2ffe91487d', '0b137077ef', '1eab6b7645', '0a00de30f3', '6373a23c35', 'a165bb7e2d', '2f40dddb5c', '46c89ddd73', 'e68b430438', 'a1ed74045c', '6c6c281d39', '40eaf1d1ca', 'c5048ee1dd', '7ff0b9d106', '865dceed6a', '7bfd750476', '59f7e43e70', 'bc80b9049f', '39f3f1c0ff', '64604640a3', '81ef1f6ce8', '3045992828', '18f739a145', '4e5caed46a', '58be14a156', 'f2f48a3c74', '386313664b', '57bd89c5ef', '1e14262cc2', '50b9f8ec52', 'bb9a86fdaf', '9da115ea81', '0dffeb6e8f', 'c9e3da08a9', '08e73d11be', '108c0c4f1a', 'adc23e54c5', '1f817e41bf', 'a26aa4ba0c', '54fae1241b', '294d8b3e59', '885c54205a', 'c3bf5dd5d3', '1c7e418e36', '180afd7909', '8cd6dda369', '96824b073d', '5e497966dd', '930123d68b', '4e186d0177', 'e28ff3570b', '0957de3049', '992fcf9b1a', 'a9d64687ee', 'e62f5ed3d3', 'c4d623427a', 'd63bdf9e31', '12000b8917', '7de124a83d', '47fb9c9e6b', '45522f9b1d', '3a15c564e3', '0f79140d78', '0d541a2106', 'e1bd43f6d2', '6b5a82abd8', '148c67fc40', '9cfa477045', '7426a53bd7', 'fee476619b', 'e995812060', '081bf7fcab', '2aad5557d0', '69fe91804a', '35b53176e2', '86b68ed377', '0d0d5b0aef', '727315fee3', '99e6147466', 'feaaa180a5', '3f6381629a', '3edd42f5f4', '35c0286412', '3c7ae2d3be', '5b87503cb0', 'b06e569669', 'd81e6a9186', 'f2aefc2b7a', '072b9c3507', '9ce8cdff5e', '9662069e5d', 'ff8ca8c7b9', 'efe5d37803', '272933c111', 'b15434a261', 'c06bdf01ea', '32a000868a', 'eedcfdfdab', 'ba77c0f9f0', '25667a50b4', '91ef82ad25', '68052f97d0', 'c94fcd769c', '76b1738f7e', '92d866b39a', '9bfd15b1e7', 'b42afa4b6d', 'b73dd3a919', 'ae2cdf8558']:
        print (i, " START")
        doc = frappe.get_doc('Sync Log',i)
        docSumber = frappe.get_doc(doc.doc_type, doc.docname)
        doc.data = frappe.as_json(docSumber)
        doc.save()

@frappe.whitelist()
def sync_jenis_transaksi_ppn_to_tax_server():
    # print ('Pricing Rule =========================>')
    # doc = frappe.db.sql_list(""" SELECT NAME FROM `tabPricing Rule`""")
    # for i in doc:
    #     print (i, " START")
    #     get_doc = frappe.get_doc('Pricing Rule',i)
    #     doc_save = frappe.new_doc('Sync Log')
    #     doc_save.update_type = 'Create'
    #     doc_save.doc_type = get_doc.doctype
    #     doc_save.docname = get_doc.name
    #     doc_save.data = frappe.as_json(get_doc)
    #     doc_save.save()

    # doc = frappe.db.sql(""" SELECT NAME,docname FROM `tabSync Log` WHERE doc_type = 'Sales Order' ORDER BY docname ASC """)
    # # doc_item_disabled = frappe.db.sql_list(""" SELECT NAME FROM `tabItem` WHERE disabled = 1""")
    # for i in doc:
    #     cek = frappe.db.exists("Sales Order",i[1])
    #     if (not cek):
    #         print (i[0], i[1], " START")
    #         debug_sync_log(i[0])


    # print ('SO =========================>')
    # doc = frappe.db.sql_list(""" SELECT NAME FROM `tabSales Order` WHERE jenis_transaksi = 'PPN' AND docstatus = 1 ORDER BY NAME ASC """)
    # for i in doc:
    #     print (i, " START")
    #     get_doc = frappe.get_doc('Sales Order',i)
    #     doc_save = frappe.new_doc('Sync Log')
    #     doc_save.update_type = 'Create'
    #     doc_save.doc_type = get_doc.doctype
    #     doc_save.docname = get_doc.name
    #     doc_save.data = frappe.as_json(get_doc)
    #     doc_save.save()

    # doc = frappe.db.sql(""" SELECT NAME,docname FROM `tabSync Log` WHERE doc_type = 'Sales Order' ORDER BY docname ASC """)
    # # doc_item_disabled = frappe.db.sql_list(""" SELECT NAME FROM `tabItem` WHERE disabled = 1""")
    # for i in doc:
    #     cek = frappe.db.exists("Sales Order",i[1])
    #     if (not cek):
    #         print (i[0], i[1], " START")
    #         debug_sync_log(i[0])

    print ('PO =========================>')
    doc = frappe.db.sql_list(""" SELECT NAME FROM `tabPurchase Order` WHERE jenis_transaksi = 'PPN' AND docstatus = 1 ORDER BY NAME ASC """)
    for i in doc:
        print (i, " START")
        get_doc = frappe.get_doc('Purchase Order',i)
        doc_save = frappe.new_doc('Sync Log')
        doc_save.update_type = 'Create'
        doc_save.doc_type = get_doc.doctype
        doc_save.docname = get_doc.name
        doc_save.data = frappe.as_json(get_doc)
        doc_save.save()

@frappe.whitelist()
def cancel_delete_non_tax():
    # # on account setting, Delete Accounting and Stock Ledger Entries on deletion of Transaction, Accounts Frozen Till Date = NULL
    # print ('PE =========================>')
    # doc = frappe.db.sql_list(""" SELECT NAME FROM `tabPayment Entry` WHERE jenis_transaksi = 'Non PPN' AND amended_from IS NOT NULL ORDER BY NAME DESC """)
    # temp_list_error = []
    # for i in doc:
    #     try:
    #         print (i, " START")
    #         doc = frappe.get_doc('Payment Entry',i)
    #         doc_edit = 0
    #         if(doc.party_type=='Customer'):
    #             customer = frappe.db.sql(""" SELECT NAME, disabled FROM `tabCustomer` WHERE NAME = "%s" """ % (doc.party))
    #             if(customer[0][1]==1):
    #                 customer = frappe.db.sql(""" UPDATE `tabCustomer` SET disabled = '0' WHERE NAME = "%s" """ % (doc.party))
    #                 doc_edit = 1
    #         if(doc.docstatus==1):
    #             doc.cancel()

    #         if(doc.docstatus==0):
    #             doc.delete()
    #         # doc.delete()
    #         if(doc_edit==1):
    #             customer = frappe.db.sql(""" UPDATE `tabCustomer` SET disabled = '1' WHERE NAME = "%s" """ % (doc.party))
    #         frappe.db.commit()
    #         print (i, " DONE")
    #     except Exception as e:
    #         temp_list_error.append([doc.name,e])

    # doc = frappe.db.sql_list(""" SELECT NAME FROM `tabPayment Entry` WHERE jenis_transaksi = 'Non PPN' AND amended_from IS NULL ORDER BY NAME DESC """)
    # for i in doc:
    #     try:
    #         print (i, " START")
    #         doc = frappe.get_doc('Payment Entry',i)
    #         doc_edit = 0
    #         if(doc.party_type=='Customer'):
    #             customer = frappe.db.sql(""" SELECT NAME, disabled FROM `tabCustomer` WHERE NAME = "%s" """ % (doc.party))
    #             if(customer[0][1]==1):
    #                 customer = frappe.db.sql(""" UPDATE `tabCustomer` SET disabled = '0' WHERE NAME = "%s" """ % (doc.party))
    #                 doc_edit = 1
    #         if(doc.docstatus==1):
    #             doc.cancel()

    #         if(doc.docstatus==0):
    #             doc.delete()
    #         # doc.delete()
    #         if(doc_edit==1):
    #             customer = frappe.db.sql(""" UPDATE `tabCustomer` SET disabled = '1' WHERE NAME = '{}' """.format(doc.party))
    #         frappe.db.commit()
    #         print (i, " DONE")
    #     except Exception as e:
    #         temp_list_error.append([doc.name,e])
    # print (temp_list_error)

    # print ('sinv =========================>')
    # doc_so_close = frappe.db.sql_list(""" SELECT NAME FROM `tabSales Order` WHERE status = 'Closed' ORDER BY NAME DESC""")
    # update_so_close = frappe.db.sql(""" UPDATE `tabSales Order` SET status = 'To Deliver' WHERE NAME IN {} """.format(tuple(doc_so_close)))
    # doc = frappe.db.sql_list(""" SELECT NAME FROM `tabSales Invoice` WHERE jenis_transaksi = 'Non PPN' ORDER BY NAME DESC""")
    # temp_list_error = []
    # for i in doc:
    #     try:
    #         doc = frappe.get_doc('Sales Invoice',i)
    #         doc_edit = 0
    #         customer = frappe.db.sql(""" SELECT NAME, disabled FROM `tabCustomer` WHERE NAME = "%s" """ % (doc.customer))
    #         if(customer[0][1]==1):
    #             customer = frappe.db.sql(""" UPDATE `tabCustomer` SET disabled = '0' WHERE NAME = "%s" """ % (doc.customer))
    #             doc_edit = 1

    #         if(doc.docstatus==1):
    #             doc.cancel()

    #         if(doc.docstatus==0):
    #             doc.delete()
    #         # doc.delete()
    #         if(doc_edit==1):
    #             customer = frappe.db.sql(""" UPDATE `tabCustomer` SET disabled = '1' WHERE NAME = '{}' """.format(doc.customer))
    #         frappe.db.commit()
    #         print (i, " DONE")
    #     except Exception as e:
    #         temp_list_error.append([doc.name,e])
    # update_so_close = frappe.db.sql(""" UPDATE `tabSales Order` SET status = 'Closed' WHERE NAME IN {} """.format(tuple(doc_so_close)))
    # print (temp_list_error)

    # # dn perlu stock setting allow negative stock
    # print ('dn =========================>')
    # doc_so_close = frappe.db.sql_list(""" SELECT NAME FROM `tabSales Order` WHERE status = 'Closed' ORDER BY NAME DESC""")
    # update_so_close = frappe.db.sql(""" UPDATE `tabSales Order` SET status = 'To Deliver' WHERE NAME IN {} """.format(tuple(doc_so_close)))

    # doc = frappe.db.sql_list(""" SELECT NAME FROM `tabDelivery Note` WHERE jenis_transaksi = 'Non PPN' ORDER BY NAME DESC""")
    # temp_list_error = []
    # for i in doc:
    #     try:
    #         doc = frappe.get_doc('Delivery Note',i)
    #         if(doc.docstatus==1):
    #             doc.cancel()

    #         if(doc.docstatus==0):
    #             doc.delete()
    #         # doc.delete()
    #         frappe.db.commit()
    #         print (i, " DONE")
    #     except Exception as e:
    #         temp_list_error.append([doc.name,e])
    # update_so_close = frappe.db.sql(""" UPDATE `tabSales Order` SET status = 'Closed' WHERE NAME IN {} """.format(tuple(doc_so_close)))
    # print (temp_list_error)

    # print ('pinv =========================>')
    # doc_so_close = frappe.db.sql_list(""" SELECT NAME FROM `tabSales Order` WHERE status = 'Closed' ORDER BY NAME DESC""")
    # update_so_close = frappe.db.sql(""" UPDATE `tabSales Order` SET status = 'To Deliver' WHERE NAME IN {} """.format(tuple(doc_so_close)))
    # doc = frappe.db.sql_list(""" SELECT NAME FROM `tabPurchase Invoice` WHERE jenis_transaksi = 'Non PPN' ORDER BY NAME DESC""")
    # temp_list_error = []
    # # doc = ['ACC-PINV-NP-2021-00318', 'ACC-PINV-NP-2021-00196']
    # for i in doc:
    #     try:
    #         doc = frappe.get_doc('Purchase Invoice',i)
    #         if(doc.status=="Close"):
    #             doc.status = "To Deliver"

    #         if(doc.docstatus==1):
    #             doc.cancel()

    #         if(doc.docstatus==0 and doc.docstatus==2):
    #             doc.delete()
    #         # doc.delete()
    #         frappe.db.commit()
    #         print (i, " DONE")
    #     except Exception as e:
    #         temp_list_error.append([doc.name,e])
    # update_so_close = frappe.db.sql(""" UPDATE `tabPurchase Order` SET status = 'Closed' WHERE NAME IN {} """.format(tuple(doc_so_close)))
    # print (temp_list_error)

    # print ('prec =========================>')
    # doc_po_close = frappe.db.sql_list(""" SELECT NAME FROM `tabPurchase Order` WHERE status = 'Closed' ORDER BY NAME DESC""")
    # update_po_close = frappe.db.sql(""" UPDATE `tabPurchase Order` SET status = 'To Deliver' WHERE NAME IN {} """.format(tuple(doc_po_close)))
    # # doc_po_close2 = frappe.db.sql_list(""" SELECT NAME FROM `tabPurchase Order` WHERE status = 'On Hold' ORDER BY NAME DESC""")
    # # update_po_close2 = frappe.db.sql(""" UPDATE `tabPurchase Order` SET status = 'To Deliver' WHERE NAME IN {} """.format(tuple(doc_po_close2)))
    # doc = frappe.db.sql_list(""" SELECT NAME FROM `tabPurchase Receipt` WHERE jenis_transaksi = 'Non PPN' ORDER BY NAME DESC""")
    # # doc = ['MAT-PRE-NP-2021-00083']
    # temp_list_error = []
    # for i in doc:
    #     try:
    #         doc = frappe.get_doc('Purchase Receipt',i)
    #         if(doc.status=="Close"):
    #             doc.status = "To Deliver"

    #         if(doc.docstatus==1):
    #             doc.cancel()

    #         if(doc.docstatus==0 and doc.docstatus==2):
    #             doc.delete()
    #         # doc.delete()
    #         frappe.db.commit()
    #         print (i, " DONE")
    #     except Exception as e:
    #         temp_list_error.append([doc.name,e])
    # update_po_close = frappe.db.sql(""" UPDATE `tabPurchase Order` SET status = 'Closed' WHERE NAME IN {} """.format(tuple(doc_po_close)))
    # # update_po_close2 = frappe.db.sql(""" UPDATE `tabPurchase Order` SET status = 'On Hold' WHERE NAME IN {} """.format(tuple(doc_po_close2)))
    # print (temp_list_error)

    # print ('po =========================>')
    # doc = frappe.db.sql_list(""" SELECT NAME FROM `tabPurchase Order` WHERE jenis_transaksi = 'Non PPN' ORDER BY NAME DESC""")
    # # doc = ['PUR-ORD-NP-2021-00889-1','PUR-ORD-NP-2021-00888-1','PUR-ORD-NP-2021-00064-1']
    # doc_mr_close = frappe.db.sql_list(""" SELECT NAME FROM `tabMaterial Request` WHERE status = 'Stopped' ORDER BY NAME DESC""")
    # update_mr_close = frappe.db.sql(""" UPDATE `tabPurchase Order` SET status = 'Partially Ordered' WHERE NAME IN {} """.format(tuple(doc_mr_close)))
    # # doc = ['PUR-ORD-NP-2021-01327','PUR-ORD-NP-2021-01197','PUR-ORD-NP-2021-00925','PUR-ORD-NP-2021-00889-1','PUR-ORD-NP-2021-00888-1','PUR-ORD-NP-2021-00064-1']
    # temp_list_error = []
    # for i in doc:
    #     try:
    #         doc = frappe.get_doc('Purchase Order',i)
    #         # if(doc.status=="Close"):
    #         #     doc.status = "To Deliver"

    #         if(doc.docstatus==1):
    #             doc.cancel()

    #         if(doc.docstatus==0 and doc.docstatus==2):
    #             doc.delete()
    #         # doc.delete()
    #         frappe.db.commit()
    #         print (i, " DONE")
    #     except Exception as e:
    #         temp_list_error.append([doc.name,e])
    # print (temp_list_error)
    # update_mr_close = frappe.db.sql(""" UPDATE `tabPurchase Order` SET status = 'Stopped' WHERE NAME IN {} """.format(tuple(doc_mr_close)))

    # print ('so ==========================>')
    # doc_so = frappe.db.sql_list(""" SELECT NAME FROM `tabSales Order` WHERE jenis_transaksi = 'Non PPN' ORDER BY NAME DESC""")
    # temp_list_error = []
    # for i in doc_so:
    #     try:
    #         doc = frappe.get_doc('Sales Order',i)
    #         if(doc.status=="Close"):
    #             doc.status = "To Deliver"

    #         if(doc.docstatus==1):
    #             doc.cancel()

    #         if(doc.docstatus==0 and doc.docstatus==2):
    #             doc.delete()
    #         # doc.delete()
    #         frappe.db.commit()
    #         print (i, " DONE")
    #     except Exception as e:
    #         temp_list_error.append([doc.name,e])
    # print (temp_list_error)
    pass

@frappe.whitelist()
def delete_cancel_doc():
    # on account setting, Delete Accounting and Stock Ledger Entries on deletion of Transaction, Accounts Frozen Till Date = NULL, perlu stock setting allow negative stock
    print ("Sales Order")
    temp_list_error = []
    doc = frappe.db.sql_list(""" SELECT NAME FROM `tabSales Order` WHERE jenis_transaksi = 'Non PPN' AND docstatus = 2 ORDER BY NAME DESC""")       
    for i in doc:
        print (i, " Start")
        try:
            doc = frappe.get_doc('Sales Order',i)
            doc.delete()
            frappe.db.commit()
            print (i, " DONE")
        except Exception as e:
            print (i, " ERROR")
            temp_list_error.append([doc.name,e])
    print (temp_list_error)

@frappe.whitelist()
def delete_cancel_doc_je_ste():
    print ("Journal Entry")
    temp_list_error = []
    doc = frappe.db.sql_list(""" SELECT NAME FROM `tabJournal Entry` WHERE tax_status = "Non Tax" ORDER BY NAME DESC""")
    doc=['ACC-JV-23-01-00343']
    for i in doc:
        print (i, " Start")
        try:
            doc = frappe.get_doc('Journal Entry',i)
            if(doc.docstatus==1):
                doc.cancel()
            doc.delete()
            frappe.db.commit()
            print (i, " DONE")
        except Exception as e:
            print (i, " ERROR")
            temp_list_error.append([doc.name,e])
    print (temp_list_error)

    # print ("Stock Entry")
    # temp_list_error = []
    # doc = frappe.db.sql_list(""" SELECT NAME FROM `tabStock Entry` WHERE tax_status = "Non Tax" OR jenis_transaksi = "Non PPN" ORDER BY NAME DESC""")
    # for i in doc:
    #     print (i, " Start")
    #     try:
    #         doc = frappe.get_doc('Stock Entry',i)
    #         if(doc.docstatus==1):
    #             doc.cancel()
    #         doc.delete()
    #         frappe.db.commit()
    #         print (i, " DONE")
    #     except Exception as e:
    #         print (i, " ERROR")
    #         temp_list_error.append([doc.name,e])
    # print (temp_list_error)

@frappe.whitelist()
def test_connection():
    print("https://deprintz13.digitalasiasolusindo.com/")
    clientroot = FrappeClient("https://deprintz13.digitalasiasolusindo.com/","administrator","Rahasiakit@")
    print(clientroot)

@frappe.whitelist()
def change_industry_in_lead():
    # Pakai LIST diexcel
    import pandas as pd

    df = pd.read_excel(r'/home/frappe/frappe-bench/apps/sync_tax/sync_tax/custom/lead_deprintz_update-Copy.xls')
    data_list = df.values.tolist()
    for i in data_list:        
        print (i[0], i[1], " Start")
        doc = frappe.get_doc('Lead', i[0])
        doc.industry = i[1]
        doc.db_update()
        print (i[0], i[1], " DONE")
        frappe.db.commit()
        # break   

@frappe.whitelist()
def rename_customer():
    # Pakai LIST diexcel
    import pandas as pd

    df = pd.read_excel(r'/home/frappe/frappe-bench/apps/sync_tax/sync_tax/custom/Update deprintz.xls')
    data_list = df.values.tolist()
    for i in data_list:        
        print (i[0], i[1], " Start")
        frappe.rename_doc('Customer', i[0], i[1])
        print (i[0], i[1], " DONE")
        frappe.db.commit()
        # break         

    # list_sc = frappe.db.sql(""" SELECT NAME,serial_customer FROM `tabCustomer` WHERE serial_customer != NAME LIMIT 1000 """, as_dict=1)
    # list_sc = []
    # for i in list_sc:
    #     print (i[0], i[1], " Start")
    #     frappe.rename_doc('Customer', i[0], i[1])
    #     print (i[0], i[1], " DONE")

@frappe.whitelist()
def change_territory_customer():
    list_sc = []        
    for i in list_sc:
        print (i[0],' start')
        #Customer 
        doc = frappe.get_doc('Customer',{'name': i[0]})
        if doc:
            frappe.msgprint("masuk customer")
            doc.territory = i[1]
            doc.db_update()
            frappe.msgprint(i[0]+ "berhasil di rubah")
                        
        if(doc.lead_name):
            # Lead
            doc_lead = frappe.db.sql(""" SELECT * from `tabLead` where name='{0}' """.format(doc.lead_name),as_dict=1)        
            if doc_lead:
                frappe.msgprint("masuk lead")
                for w in doc_lead:
                     if i[1] != w['territory']:
                        get_doc = frappe.get_doc('Lead',{'name': w['name']})
                        get_doc.territory = i[1]
                        get_doc.db_update()
                        frappe.msgprint(w['name']+ "berhasil di rubah")

            # Quotation        
            doc_quotation = frappe.db.sql(""" SELECT * from `tabQuotation` where party_name='{0}' """.format(doc.lead_name),as_dict=1)        
            if doc_quotation:
                frappe.msgprint("masuk Quotation")
                for w in doc_quotation:
                     if i[1] != w['territory']:
                        get_doc = frappe.get_doc('Quotation',{'name': w['name']})
                        get_doc.territory = i[1]
                        get_doc.db_update()
                        frappe.msgprint(w['name']+ "berhasil di rubah")     
            
        # Delivery Note
        doc_dn = frappe.db.sql(""" SELECT * from `tabDelivery Note` where customer='{0}' """.format(i[0]),as_dict=1)        
        if doc_dn:
            frappe.msgprint("masuk DN")
            for w in doc_dn:
                 if i[1] != w['territory']:
                    get_doc = frappe.get_doc('Delivery Note',{'name': w['name']})
                    get_doc.territory = i[1]
                    get_doc.db_update()
                    frappe.msgprint(w['name']+ "berhasil di rubah")        

        # Sales Order
        doc_so = frappe.db.sql(""" SELECT * from `tabSales Order` where customer='{0}' """.format(i[0]),as_dict=1)        
        if doc_so:
            frappe.msgprint("masuk SO")
            for w in doc_so:
                 if i[1] != w['territory']:
                    get_doc = frappe.get_doc('Sales Order',{'name': w['name']})
                    get_doc.territory = i[1]
                    get_doc.db_update()
                    frappe.msgprint(w['name']+ "berhasil di rubah")

        # Sales Invoice
        doc_sinv = frappe.db.sql(""" SELECT * from `tabSales Invoice` where customer='{0}' """.format(i[0]),as_dict=1)        
        if doc_sinv:
            frappe.msgprint("masuk SINV")
            for w in doc_sinv:
                 if i[1] != w['territory']:
                    get_doc = frappe.get_doc('Sales Invoice',{'name': w['name']})
                    get_doc.territory = i[1]
                    get_doc.db_update()
                    frappe.msgprint(w['name']+ "berhasil di rubah")    

        # print (i[0], i[1], " Start")
        # doc = frappe.get_doc('Customer', i[0])
        # doc.territory = i[1]
        # doc.save()
        # frappe.db.commit()
        # print (i[0], i[1], " DONE")

        print (i[0],' DONE')

@frappe.whitelist()
def create_event_producer():
    # doc = frappe.new_doc('Event Producer')
    # doc.producer_url = 'https://deprintz13.digitalasiasolusindo.com'
    # doc.api_key = 'a7d83b324c108b9'
    # doc.api_secret = '99d5a85cdec2349'
    # doc.user = 'sync@gmail.com'
    # row = doc.append('producer_doctypes')
    # row.ref_doctype = "Item"
    # row.status = "Pending"
    # row.use_same_name = 1
    # doc.flags.ignore_permission = True
    # doc.save()
    # frappe.db.commit()

    doc = frappe.get_doc('Event Producer', 'https://deprintz13.digitalasiasolusindo.com')
    # listDoctype = ['Item Price', 'Contact', 'Sales Person', 'Product Bundle', 'Item Group', 'Price List', 'Mode of Payment', 'Customer', 'Purchase Taxes and Charges Template', 'Item Category', 'File', 'Shipping Rule', 'UOM', 'Account', 'Terms and Conditions', 'Lead Source', 'Project', 'Territory', 'POS Profile', 'Sales Taxes and Charges Template', 'Serial No', 'Letter Head', 'Asset Category', 'Supplier', 'Sales Partner', 'Process Deferred Accounting', 'Print Heading', 'Supplier Quotation', 'Supplier Group', 'Sales Partner', 'Coupon Code', 'Tax Withholding Category', 'Brand', 'Driver', 'Lead', 'Sync Log', 'Company', 'Customer Group', 'Tax Category', 'Payment Terms Template', 'Campaign', 'Finance Book', 'Employee', 'Cost Center', 'Bank Account', 'Journal Entry Template', 'Currency', 'Warehouse', 'Address', 'Tax Category', 'Pricing Rule', 'Loyalty Program']
    listDoctype = ['Industry Type']
    for i in listDoctype:
        row = doc.append('producer_doctypes')
        row.ref_doctype = i
        row.status = "Pending"
        row.use_same_name = 1
    doc.flags.ignore_permission = True
    doc.save()
    frappe.db.commit()

@frappe.whitelist()
def create_event_consumer():
    # bench --site deprintz13.digitalasiasolusindo.com console
    # doc = frappe.get_doc('Event Consumer', 'https://deprintz13tax.digitalasiasolusindo.com')
    # doc.consumer_doctypes[0].status  = 'Approved'
    # doc.flags.ignore_permission = True
    # doc.save()
    # frappe.db.commit()

    doc = frappe.get_doc('Event Consumer', 'https://deprintz13tax.digitalasiasolusindo.com')
    for i in doc.consumer_doctypes:
        if(i.status=="Pending"):
            i.status = 'Approved'
        # i.status = 'Approved'
    doc.flags.ignore_permission = True
    doc.save()
    frappe.db.commit()


@frappe.whitelist()
def repair_stock_ledger():   
    from erpnext.stock.stock_ledger import update_entries_after  
    frappe.db.sql(""" UPDATE `tabSingles` SET value = 1 WHERE field = "allow_negative_stock" """)
    
    listDoc = frappe.db.sql(""" SELECT NAME,voucher_type,voucher_no FROM `tabStock Ledger Entry` WHERE voucher_type IN ('Sales Invoice', 'Purchase Invoice') """)
    for i in listDoc:        
        docu = frappe.get_doc(i[1],i[2])
        if not docu.update_stock:
            frappe.db.sql(""" DELETE FROM `tabStock Ledger Entry` WHERE voucher_no = "{}" """.format(i[2]))
            for row in docu.items:
                update_entries_after({
                "item_code": row.item_code,
                "warehouse": row.warehouse,
                "posting_date": docu.posting_date,
                "posting_time": docu.posting_time
            })

    frappe.db.sql(""" UPDATE `tabSingles` SET value = 0 WHERE field = "allow_negative_stock" """)
    