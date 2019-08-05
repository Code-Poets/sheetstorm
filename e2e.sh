#!/bin/bash -e

python manage.py behave --settings=sheetstorm.settings.testing --no-capture
