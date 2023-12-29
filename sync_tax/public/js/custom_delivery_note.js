frappe.ui.form.on('Delivery Note', {
	setup(frm){
	},
	refresh(frm) {
		cur_frm.remove_custom_button(__('Update Items'));
		if(frm.doc.docstatus === 1 && frm.doc.status !== 'Closed'){
		}
		if (frm.doc.__islocal != 1) {
            frm.set_df_property('jenis_transaksi', 'read_only', 1);
            frm.set_df_property('tax_status', 'read_only', 1);
        }
    },
    onload: function(frm) {
        if(cur_frm.doc.amended_from){
            frm.set_df_property('jenis_transaksi', 'read_only', 1);
            frm.set_df_property('tax_status', 'read_only', 1);
        }
    },
	jenis_transaksi: function(frm){
	    if (frm.doc.jenis_transaksi == "PPN"){
	        frm.set_value("naming_series","SO-P-.YY.MM.DD.-.#####");
	        frm.set_value("tax_status","Tax")

	    } else if (frm.doc.jenis_transaksi == "Non PPN"){
	        frm.set_value("tax_status","Non Tax")
	        frm.set_value("naming_series","SO-NP-.YY.MM.DD.-.#####");
	    }
	},
});