# Generated manually — adds file upload fields to QuizAnswer

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lms', '0005_withdrawal'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizanswer',
            name='file_url',
            field=models.URLField(blank=True, default='', help_text='Uploaded file URL (for essay/short answer submissions)', verbose_name='File URL'),
        ),
        migrations.AddField(
            model_name='quizanswer',
            name='file_name',
            field=models.CharField(blank=True, default='', max_length=500, verbose_name='File Name'),
        ),
    ]
