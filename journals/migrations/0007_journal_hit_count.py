# Generated by Django 4.2 on 2024-09-30 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journals', '0006_alter_journal_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='hit_count',
            field=models.IntegerField(default=0),
        ),
    ]
