import logging

logLevel = logging.INFO

# telegram token
api_token = ''

# setting from local file
try:
    from local_settings import *
except ImportError:
    pass
