#!/usr/bin/env bash
python manage.py loaddata employees/fixtures/task_activities.yaml
python manage.py load_initial_data
