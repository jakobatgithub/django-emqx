__author__ = "Jakob"
__email__ = "jakob@physik.tu-berlin.de"
__version__ = "0.1.0"


_mqtt_client = None

def get_mqtt_client():
    global _mqtt_client
    if _mqtt_client is None:
        from .conf import emqx_settings
        from .mqtt import MQTTClient
        _mqtt_client = MQTTClient(broker=emqx_settings.EMQX_BROKER, port=emqx_settings.EMQX_PORT)
    return _mqtt_client