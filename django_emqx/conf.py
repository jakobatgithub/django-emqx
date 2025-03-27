## django_emqx/conf.py

import os

from django.conf import settings


DEFAULTS = {
    'EMQX_BROKER': "emqx_broker",
    'EMQX_PORT': 8883,
    'EMQX_WEBHOOK_SECRET': os.environ.get("EMQX_WEBHOOK_SECRET"),
    'EMQX_MAX_RETRIES': 10,
    'EMQX_RETRY_DELAY': 3,
    'EMQX_TLS_ENABLED': True,
    'EMQX_TLS_CA_CERTS': None,
}

class EMQXSettings:
    def __getattr__(self, attr):
        if attr not in DEFAULTS:
            raise AttributeError(f"Invalid EMQX setting: '{attr}'")

        return getattr(settings, attr, DEFAULTS[attr])

emqx_settings = EMQXSettings()