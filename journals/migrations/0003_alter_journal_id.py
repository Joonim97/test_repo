# Generated by Django 4.2 on 2024-09-26 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journals', '0002_remove_journal_author_remove_journal_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journal',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
