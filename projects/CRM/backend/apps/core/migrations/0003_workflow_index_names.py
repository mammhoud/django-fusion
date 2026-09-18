from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_workflows"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="workflowdefinition",
            old_name="core_workfl_workspa_05ed9a_idx",
            new_name="core_workfl_workspa_39689e_idx",
        ),
        migrations.RenameIndex(
            model_name="workflowrun",
            old_name="core_workfl_workspa_1c5c99_idx",
            new_name="core_workfl_workspa_647489_idx",
        ),
        migrations.RenameIndex(
            model_name="workflowrun",
            old_name="core_workfl_definit_4b3d1c_idx",
            new_name="core_workfl_definit_2484c9_idx",
        ),
    ]
