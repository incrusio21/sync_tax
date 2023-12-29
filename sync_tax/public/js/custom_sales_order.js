frappe.ui.form.on('Sales Order', {
	setup(frm){
	},
	refresh(frm) {
		cur_frm.remove_custom_button(__('Update Items'));
		if(frm.doc.docstatus === 1 && frm.doc.status !== 'Closed'){
		}
		if (frm.doc.__islocal != 1) {
            frm.set_df_property('jenis_transaksi', 'read_only', 1);
        }
    },
    onload: function(frm) {
        if(cur_frm.doc.amended_from){
            frm.set_df_property('tax_status', 'read_only', 1);
        }
    },
	jenis_transaksi: function(frm){
	    if (frm.doc.jenis_transaksi == "PPN"){
	        frm.set_value("taxes_and_charges", "PPN 11% - D");
	        frm.set_value("tax_status","Tax")
	        frm.set_value("naming_series","SO-P-.YY.MM.DD.-.#####");

	    } else if (frm.doc.jenis_transaksi == "Non PPN"){
	    	for (var i = frm.doc.taxes.length - 1; i >= 0; i--) {
	    		frappe.model.set_value(cur_frm.doc.taxes[i].doctype,cur_frm.doc.taxes[i].name,"rate",0)
	    	}
	        frm.set_value("taxes_and_charges",null);
	        frm.set_value("taxes",null);
	        frm.refresh_field("taxes");

	        frm.set_value("tax_status","Non Tax")
	        frm.set_value("naming_series","SO-NP-.YY.MM.DD.-.#####");
	    }
	},
});