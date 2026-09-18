from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("finance", "0001_initial")]

    operations = [
        migrations.RenameIndex(
            model_name="invoice",
            old_name="finance_inv_workspa_0f5b31_idx",
            new_name="finance_inv_workspa_036ee2_idx",
        ),
        migrations.RenameIndex(
            model_name="invoice",
            old_name="finance_inv_workspa_24d5cc_idx",
            new_name="finance_inv_workspa_4a477e_idx",
        ),
        migrations.RenameIndex(
            model_name="payment",
            old_name="finance_pay_workspa_9c2f60_idx",
            new_name="finance_pay_workspa_cba339_idx",
        ),
        migrations.RenameIndex(
            model_name="revenueevent",
            old_name="finance_rev_workspa_8f0f90_idx",
            new_name="finance_rev_workspa_d17cdc_idx",
        ),
        migrations.RenameIndex(
            model_name="revenueevent",
            old_name="finance_rev_workspa_ef5a5f_idx",
            new_name="finance_rev_workspa_5100fe_idx",
        ),
    ]
