# Generated by Django 2.2.27 on 2022-03-10 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yearbook', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaserecapp',
            name='card_number',
            field=models.CharField(default=123, max_length=16),
            preserve_default=False,
        ),
    ]