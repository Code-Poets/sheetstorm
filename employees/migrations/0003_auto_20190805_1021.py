# Generated by Django 2.2.3 on 2019-08-05 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('managers', '0002_auto_20190730_1515'),
        ('employees', '0002_auto_20190730_1515'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskactivitytype',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='taskactivitytype',
            name='projects',
            field=models.ManyToManyField(related_name='project_activities', to='managers.Project'),
        ),
    ]