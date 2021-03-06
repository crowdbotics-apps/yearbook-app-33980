# Generated by Django 2.2.27 on 2022-04-06 13:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('yearbook', '0015_auto_20220406_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='yearbook.Room'),
        ),
        migrations.AlterField(
            model_name='room',
            name='participants',
            field=models.ManyToManyField(related_name='chats', to=settings.AUTH_USER_MODEL),
        ),
    ]
