from django.test import TestCase
from django_emqx.signals import (
    emqx_device_connected,
    new_emqx_device_connected,
    emqx_device_disconnected,
)
from django.dispatch import Signal

class TestSignals(TestCase):
    def test_emqx_device_connected_signal(self):
        signal_called = False

        def handler(sender, **kwargs):
            nonlocal signal_called
            signal_called = True

        emqx_device_connected.connect(handler)
        emqx_device_connected.send(sender=self.__class__)

        self.assertTrue(signal_called)

    def test_new_emqx_device_connected_signal(self):
        signal_called = False

        def handler(sender, **kwargs):
            nonlocal signal_called
            signal_called = True

        new_emqx_device_connected.connect(handler)
        new_emqx_device_connected.send(sender=self.__class__)

        self.assertTrue(signal_called)

    def test_emqx_device_disconnected_signal(self):
        signal_called = False

        def handler(sender, **kwargs):
            nonlocal signal_called
            signal_called = True

        emqx_device_disconnected.connect(handler)
        emqx_device_disconnected.send(sender=self.__class__)

        self.assertTrue(signal_called)
