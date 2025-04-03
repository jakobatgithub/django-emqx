## django_emqx/conf.py

from django.conf import settings

"""
Configuration defaults for django-emqx integration.

This module defines default configuration values for connecting to an EMQX broker
and provides a dynamic settings loader that allows overriding these defaults
via Django's `settings.py`.

Settings:
    EMQX_BROKER (str): Hostname of the EMQX broker. Default is "emqx-broker".
    EMQX_PORT (int): Port to connect to the EMQX broker. Default is 1883 (typically for MQTT).
        Other default ports are:
          - 8083 for websockets
          - 8883 for secure MQTT
          - 8084 for secure websockets
    EMQX_WEBHOOK_SECRET (str): Shared secret used for verifying EMQX webhook signatures.
        Defaults to Django's SECRET_KEY.
    EMQX_NODE_COOKIE (str): Secret token used for EMQX node communication (if needed).
        Defaults to Django's SECRET_KEY.
    EMQX_MAX_RETRIES (int): Maximum number of retry attempts for starting up 'MQTTClient'.
        Default is 10.
    EMQX_RETRY_DELAY (int): Delay in seconds between retry attempts for starting up 'MQTTClient'.
        Default is 3 seconds.
    EMQX_TLS_ENABLED (bool): Whether TLS is enabled for the EMQX connection. Default is False.
    EMQX_TLS_CA_CERTS (str or None): Path to the CA certificates file for TLS verification.
        Default is None (no verification).

To override any of these settings, define them in your Django project's `settings.py`.
Access settings via `emqx_settings.<SETTING_NAME>`.
"""


DEFAULTS = {
    'EMQX_BROKER': "emqx-broker",
    'EMQX_PORT': 1883,
    'EMQX_WEBHOOK_SECRET': settings.SECRET_KEY,
    'EMQX_NODE_COOKIE': settings.SECRET_KEY,
    'EMQX_MAX_RETRIES': 10,
    'EMQX_RETRY_DELAY': 3,
    'EMQX_TLS_ENABLED': False,
    'EMQX_TLS_CA_CERTS': None,
}

class EMQXSettings:
    def __getattr__(self, attr):
        if attr not in DEFAULTS:
            raise AttributeError(f"Invalid EMQX setting: '{attr}'")

        return getattr(settings, attr, DEFAULTS[attr])

emqx_settings = EMQXSettings()