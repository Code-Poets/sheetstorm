try:
    # local_settings.py is required by the application to work but is not provided by default
    # to minimize the risk of someone accidentally running a production site with development settings.
    # You need to choose one of the templates (production or development) and rename it to local_settings.py
    # or create your own personalized local_settings.py
    from .local_settings import *
except ImportError as exception:
    # This condition is not foolproof but should reduce the number of cases where we catch unrelated ImportErrors
    if 'local_settings' in str(exception):
        raise ImportError("Failed to import 'local_settings' module. Use a production or development template to create one.")
    else:
        raise

assert 'ENVIRONMENT' in vars(), 'A valid local_settings module should set up ENVIRONMENT setting'
