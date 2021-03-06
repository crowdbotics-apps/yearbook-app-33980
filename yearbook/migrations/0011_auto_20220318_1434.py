# Generated by Django 2.2.27 on 2022-03-18 14:34

from django.db import migrations, models
import yearbook.models


class Migration(migrations.Migration):

    dependencies = [
        ('yearbook', '0010_purchaserecapp_purchased_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='highschoolid',
            name='code',
            field=models.CharField(default=yearbook.models.code_generator, max_length=16),
        ),
        migrations.AlterField(
            model_name='highschoolid',
            name='status',
            field=models.CharField(default='pending', max_length=16),
        ),
    ]
