# Generated by Django 2.2.27 on 2022-03-18 12:09

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('yearbook', '0009_auto_20220318_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaserecapp',
            name='purchased_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]