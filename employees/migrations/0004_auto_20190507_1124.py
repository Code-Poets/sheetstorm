# Generated by Django 2.1.1 on 2019-05-07 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0003_auto_20190423_2020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='description',
            field=models.TextField(max_length=4096),
        ),
    ]