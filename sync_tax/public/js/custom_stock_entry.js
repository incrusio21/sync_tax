frappe.ui.form.on('Stock Entry', {
	refresh(frm) {
		// your code here
		if (frm.doc.__islocal != 1) {
            frm.set_df_property('tax_status', 'read_only', 1);
            frm.set_df_property('jenis_transaksi', 'read_only', 1);
        }
        frm.set_df_property('tax_status', 'read_only', 1);
	},

	onload: function(frm) {
        if(cur_frm.doc.amended_from){
            frm.set_df_property('jenis_transaksi', 'read_only', 1);
            frm.set_df_property('tax_status', 'read_only', 1);
        }
    },
    // tax_status: function (frm) {
    //     if (frm.doc.__islocal) {
    //         if (frm.doc.tax_status == "Tax") {
    //             frm.set_value('naming_series', 'MAT-STE-P-.YYYY.-');
    //         }
    //         else if (frm.doc.tax_status == "Non Tax") {
    //             frm.set_value('naming_series', 'MAT-STE-NP-.YYYY.-');
    //         }
    //         else {
    //             frm.set_value('naming_series', 'MAT-STE-.YYYY.-');
    //         }
    //     }
    // },
    jenis_transaksi: function(frm){
        if (frm.doc.jenis_transaksi == "PPN"){
            frm.set_value('naming_series', 'MAT-STE-P-.YYYY.-');
            frm.set_value("tax_status","Tax")

        } else if (frm.doc.jenis_transaksi == "Non PPN"){
            frm.set_value("tax_status","Non Tax")
            frm.set_value('naming_series', 'MAT-STE-NP-.YYYY.-');
        } else if (frm.doc.jenis_transaksi == "Stock Awal"){
            frm.set_value("tax_status","Tax")
            frm.set_value('naming_series', 'MAT-STE-.YYYY.-');
        }
        else {
            frm.set_value('naming_series', 'MAT-STE-.YYYY.-');
        }
    }
})