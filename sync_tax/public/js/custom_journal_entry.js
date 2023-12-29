frappe.ui.form.on('Journal Entry', {
    refresh(frm) {
        // if (!cur_frm.doc.finance_book) {
        //     let date = new Date();
        //         let year = date.getFullYear();
        //         console.log(cur_frm.doc.company)
        //         cur_frm.add_fetch('company','default_finance_book','finance_book')
        //    // cur_frm.set_value("finance_book", year)
        // }
        if (frm.doc.__islocal != 1) {
            console.log('test');
            frm.set_df_property('tax_status', 'read_only', 1);
        }
    },
    onload: function (frm) {
        if (cur_frm.doc.amended_from) {
            frm.set_df_property('tax_status', 'read_only', 1);
        }
    },
    tax_status: function (frm) {
        if (frm.doc.__islocal) {
            if (frm.doc.tax_status == "Tax") {
                frm.set_value('naming_series', 'ACC-JV-P-.YY.-.MM.-.#####');
            }
            else if (frm.doc.tax_status == "Non Tax") {
                frm.set_value('naming_series', 'ACC-JV-N-.YY.-.MM.-.#####');
            }
            else {
                frm.set_value('naming_series', 'ACC-JV-.YY.-.MM.-.#####');
            }
        }
    }
})