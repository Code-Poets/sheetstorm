# Generated by Django 2.1.8 on 2019-05-30 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0003_auto_20190530_1210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='description',
            field=models.TextField(max_length=4096),
        ),
    ]