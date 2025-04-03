## django_emqx/conf.py

from django.conf import settings


DEFAULTS = {
    'EMQX_BROKER': "emqx-broker",
    'EMQX_PORT': 8883,
    'EMQX_WEBHOOK_SECRET': settings.SECRET_KEY,
    'EMQX_NODE_COOKIE': settings.SECRET_KEY,
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