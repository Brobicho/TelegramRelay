from decouple import config

"""
This file is used to load environment variables from .env
"""

API_ID = config('API_ID')
API_HASH = config('API_HASH')
SESSION_NAME = config('SESSION_NAME', default='session')
RELAY_CONFIG_PATH = config('RELAY_CONFIG_PATH', default='relay_config.json')