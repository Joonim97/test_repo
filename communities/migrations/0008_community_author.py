# Generated by Django 4.2 on 2024-10-02 05:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('communities', '0007_alter_community_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='communities_author', to=settings.AUTH_USER_MODEL),
        ),
    ]