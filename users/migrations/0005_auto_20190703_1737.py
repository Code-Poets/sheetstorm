# Generated by Django 2.2.2 on 2019-07-03 17:37

from django.db import migrations, models
import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20190701_0653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=30, validators=[users.validators.UserNameValidatior()], verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=30, validators=[users.validators.UserNameValidatior()], verbose_name='last name'),
        ),
    ]
