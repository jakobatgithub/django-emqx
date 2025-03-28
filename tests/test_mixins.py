## tests/test_mixins.py

from django.test import TestCase
from django.contrib.auth import get_user_model

from unittest.mock import patch, MagicMock

from django_emqx import utils
from django_emqx.models import EMQXDevice, Message
from django_emqx.mixins import NotificationSenderMixin, ClientEventMixin

User = get_user_model()


class NotificationSenderMixinTests(TestCase):
    def setUp(self):
        self.mixin = NotificationSenderMixin()
        self.user = User.objects.create_user(username="tester", password="test")
        self.message = Message.objects.create(title="Hello", body="World")

    @patch("django_emqx.mixins.send_mqtt_message")
    def test_send_all_notifications(self, mock_send_mqtt):
        if utils.firebase_installed:
            with patch("django_emqx.mixins.FCMDevice.objects.filter") as mock_fcm_filter:
                mock_devices = MagicMock()
                mock_fcm_filter.return_value = mock_devices

                self.mixin.send_all_notifications(
                    message=self.message,
                    recipients=[self.user]
                )
                mock_devices.send_message.assert_called_once()
        else:
            self.mixin.send_all_notifications(
                message=self.message,
                recipients=[self.user]
            )

        mock_send_mqtt.assert_called_once_with(self.user, msg_id=self.message.id, title="Hello", body="World", data=None)


class ClientEventMixinTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="test")
        self.mixin = ClientEventMixin()

    def test_handle_client_connected_creates_device(self):
        device_id = "device123"
        ip = "192.168.0.1"

        self.mixin.handle_client_connected(user_id=self.user.id, device_id=device_id, ip_address=ip)

        device = EMQXDevice.objects.get(client_id=device_id)
        self.assertEqual(device.user, self.user)
        self.assertTrue(device.active)
        self.assertEqual(device.last_status, "online")
        self.assertEqual(device.ip_address, ip)
        self.assertIsNotNone(device.last_connected_at)

    def test_handle_client_connected_updates_existing_device(self):
        device = EMQXDevice.objects.create(
            client_id="existing_device",
            user=self.user,
            active=False,
            last_status="offline",
        )

        self.mixin.handle_client_connected(user_id=self.user.id, device_id="existing_device", ip_address="1.2.3.4")

        device.refresh_from_db()
        self.assertTrue(device.active)
        self.assertEqual(device.last_status, "online")
        self.assertEqual(device.ip_address, "1.2.3.4")

    def test_handle_client_disconnected_updates_device(self):
        device = EMQXDevice.objects.create(
            client_id="device456",
            user=self.user,
            active=True,
            last_status="online",
        )

        self.mixin.handle_client_disconnected(user_id=self.user.id, device_id="device456")

        device.refresh_from_db()
        self.assertFalse(device.active)
        self.assertEqual(device.last_status, "offline")

    def test_handle_client_connected_ignores_missing_user(self):
        # No exception should be raised
        self.mixin.handle_client_connected(user_id=9999, device_id="no-user-device")

        self.assertFalse(EMQXDevice.objects.filter(client_id="no-user-device").exists())

    def test_handle_client_disconnected_ignores_missing_user(self):
        # No exception should be raised
        self.mixin.handle_client_disconnected(user_id=9999, device_id="no-user-device")

        self.assertEqual(EMQXDevice.objects.count(), 0)
