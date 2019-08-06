#!/bin/bash -e

coverage run --source='.' --rcfile=coverage-config manage.py behave --settings=sheetstorm.settings.testing --no-capture
coverage report
rm .coverage
