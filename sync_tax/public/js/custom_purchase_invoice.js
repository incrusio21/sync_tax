frappe.ui.form.on('Purchase Invoice', {
	refresh(frm) {
		// your code here
       if (frm.doc.__islocal != 1) {
            frm.set_df_property('jenis_transaksi', 'read_only', 1);
            frm.set_df_property('tax_status', 'read_only', 1);
        }
        frm.set_df_property('tax_status', 'read_only', 1);
	},
	onload: function(frm) {
        if(cur_frm.doc.amended_from){
            frm.set_df_property('jenis_transaksi', 'read_only', 1);
            frm.set_df_property('tax_status', 'read_only', 1);
        }
    },
    tax_status: function(frm) {
	    if(cur_frm.doc.__islocal){
	        if (frm.doc.tax_status == "Tax") {
                frm.set_value('naming_series', 'ACC-PINV-P-.YYYY.-');
                frm.set_value('jenis_transaksi', 'PPN');
            } 
            else if(frm.doc.tax_status == "Non Tax"){
                frm.set_value('naming_series', 'ACC-PINV-NP-.YYYY.-');
                frm.set_value('jenis_transaksi', 'Non PPN');
            }
            else{
                frm.set_value('naming_series', 'ACC-PINV-NP-.YYYY.-');
                frm.set_value('jenis_transaksi', '');
            }   
	    }
    },
    jenis_transaksi: function(frm) {
        if(cur_frm.doc.jenis_transaksi && cur_frm.doc.__islocal){
            if (cur_frm.doc.jenis_transaksi == 'PPN') {
                console.log("xxx")
                cur_frm.set_value('naming_series', 'ACC-PINV-P-.YYYY.-');
                cur_frm.set_value('tax_status', 'Tax');
                cur_frm.refresh_fields("naming_series")
                cur_frm.refresh_fields("tax_status")
            } 
            else if(cur_frm.doc.jenis_transaksi == 'Non PPN'){
                cur_frm.set_value('naming_series', 'ACC-PINV-NP-.YYYY.-');
                cur_frm.set_value('tax_status', 'Non Tax');
                cur_frm.refresh_fields("naming_series")
                cur_frm.refresh_fields("tax_status")
            }
            else{
                cur_frm.set_value('naming_series', 'ACC-PINV-NP-.YYYY.-');
                cur_frm.set_value('tax_status', '');
                cur_frm.refresh_fields("naming_series")
                cur_frm.refresh_fields("tax_status")
            }   
        }
    },
})