# Generated by Django 4.2 on 2024-09-28 18:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('journals', '0002_remove_journal_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='my_journals', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
