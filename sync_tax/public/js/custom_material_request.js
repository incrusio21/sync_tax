frappe.ui.form.on('Material Request', {
   refresh(frm) {
      // your code here
      if (frm.doc.__islocal != 1) {
            frm.set_df_property('tax_status', 'read_only', 1);
        }
   },
   onload: function(frm) {
        if(cur_frm.doc.amended_from){
            frm.set_df_property('tax_status', 'read_only', 1);
        }
    },
   tax_status: function (frm) {
        if (frm.doc.__islocal) {
            if (frm.doc.tax_status == "Tax") {
                frm.set_value('naming_series', 'MAT-MR-P-.YYYY.-');
            }
            else if (frm.doc.tax_status == "Non Tax") {
                frm.set_value('naming_series', 'MAT-MR-NP-.YYYY.-');
            }
            else {
                frm.set_value('naming_series', 'MAT-MR-.YYYY.-');
            }
        }
    }
})