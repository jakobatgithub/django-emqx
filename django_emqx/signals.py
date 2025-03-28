## django_emqx/signals.py

from django.dispatch import Signal

emqx_device_connected = Signal()
new_emqx_device_connected = Signal()
emqx_device_disconnected = Signal()