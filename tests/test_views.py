## tests/test_views.py

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from unittest.mock import patch, MagicMock

from django_emqx import utils
from django_emqx.models import EMQXDevice, Message, Notification
from django_emqx.signals import emqx_device_connected, new_emqx_device_connected, emqx_device_disconnected
from django.dispatch import Signal
from django.test import override_settings
from contextlib import contextmanager

User = get_user_model()


class NotificationViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)
        self.message = Message.objects.create(title="Test Title", body="Test Body", created_by=self.user)
        self.notification = Notification.objects.create(message=self.message, recipient=self.user)

    @patch("django_emqx.mixins.send_mqtt_message")
    def test_create_notification(self, mock_send_mqtt_message):
        if utils.firebase_installed:
            with patch("django_emqx.mixins.FCMDevice.objects.filter") as mock_fcm_filter:
                mock_devices = MagicMock()
                mock_fcm_filter.return_value = mock_devices

                url = reverse("notifications-list")
                data = {"title": "Test Title", "body": "Test Body"}
                response = self.client.post(url, data, format="json")

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.json(), {"message": "Notifications sent successfully"})

                mock_devices.send_message.assert_called_once()
        else:
            url = reverse("notifications-list")
            data = {"title": "Test Title", "body": "Test Body"}
            response = self.client.post(url, data, format="json")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.json(), {"message": "Notifications sent successfully"})

        mock_send_mqtt_message.assert_called_once()

    def test_create_notification_missing_fields(self):
        url = reverse("notifications-list")
        data = {}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Title or body or data are required"})

    def test_list_notifications(self):
        url = reverse("notifications-list")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["title"], "Test Title")
        self.assertEqual(response.json()[0]["body"], "Test Body")


class EMQXTokenViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)

    def test_generate_mqtt_token(self):
        url = reverse("token-list")
        response = self.client.post(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("mqtt_access_token", response.json())
        self.assertIn("mqtt_refresh_token", response.json())
        self.assertIn("user_id", response.json())

    def test_refresh_token(self):
        # First: get refresh token via create()
        url = reverse("token-list")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refresh_token = response.json().get("mqtt_refresh_token")
        self.assertIsNotNone(refresh_token)

        # Then: refresh access token using it
        refresh_url = reverse("token-refresh")  # /mqtt-token/refresh/
        refresh_response = self.client.post(refresh_url, {"refresh": refresh_token}, format="json")

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("mqtt_access_token", refresh_response.json())

class EMQXDeviceViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)
        self.device = EMQXDevice.objects.create(
            client_id="test_client_id",
            user=self.user,
            active=True,
            last_status="online",
        )

    def test_list_devices(self):
        url = reverse("devices-list")  # Updated to match the new basename
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["client_id"], "test_client_id")

    @patch("django_emqx.views.EMQXDeviceViewSet.handle_client_connected")
    def test_webhook_client_connected(self, mock_handle_client_connected):
        url = reverse("devices-list")  # Updated to match the new basename
        data = {
            "event": "client.connected",
            "clientid": "test_client_id",
            "user_id": str(self.user.id),
            "ip_address": "127.0.0.1",
        }
        headers = {"HTTP_X-Webhook-Token": "your_webhook_secret"}
        with self.settings(EMQX_WEBHOOK_SECRET = "your_webhook_secret"):
            response = self.client.post(url, data, format="json", **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "success"})
        mock_handle_client_connected.assert_called_once_with(
            str(self.user.id), "test_client_id", "127.0.0.1"
        )

    def test_webhook_invalid_token(self):
        url = reverse("devices-list")  # Updated to match the new basename
        data = {"event": "client.connected"}
        headers = {"HTTP_X-Webhook-Token": "invalid_token"}
        with self.settings(EMQX_WEBHOOK_SECRET = "your_webhook_secret"):
            response = self.client.post(url, data, format="json", **headers)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json(), {"error": "Forbidden"})

    def test_webhook_invalid_json(self):
        url = reverse("devices-list")  # Updated to match the new basename
        headers = {"HTTP_X-Webhook-Token": "your_webhook_secret"}
        with self.settings(EMQX_WEBHOOK_SECRET = "your_webhook_secret"):
            response = self.client.post(url, "invalid_json", content_type="application/json", **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Invalid JSON"})

    def test_list_devices_unauthenticated(self):
        self.client.force_authenticate(user=None)  # Remove authentication
        url = reverse("devices-list")
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_webhook_missing_fields(self):
        url = reverse("devices-list")
        data = {
            "event": "client.connected",
            "user_id": str(self.user.id),  # missing 'clientid'
        }
        headers = {"HTTP_X-Webhook-Token": "your_webhook_secret"}
        with self.settings(EMQX_WEBHOOK_SECRET = "your_webhook_secret"):
            response = self.client.post(url, data, format="json", **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Invalid data"})

    def test_webhook_unknown_event(self):
        url = reverse("devices-list")
        data = {
            "event": "client.unknown",
            "clientid": "test_client_id",
            "user_id": str(self.user.id),
        }
        headers = {"HTTP_X-Webhook-Token": "your_webhook_secret"}
        with self.settings(EMQX_WEBHOOK_SECRET = "your_webhook_secret"):
            response = self.client.post(url, data, format="json", **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"error": "Unknown event"})

    def test_webhook_backend_user(self):
        url = reverse("devices-list")
        data = {
            "event": "client.connected",
            "clientid": "test_client_id",
            "user_id": "backend",
        }
        headers = {"HTTP_X-Webhook-Token": "your_webhook_secret"}
        with self.settings(EMQX_WEBHOOK_SECRET = "your_webhook_secret"):
            response = self.client.post(url, data, format="json", **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "success"})

    @patch("django_emqx.views.EMQXDeviceViewSet.handle_client_connected")
    def test_signal_emqx_device_connected(self, mock_handle_client_connected):
        mock_handle_client_connected.side_effect = lambda user_id, client_id, ip_address: emqx_device_connected.send(
            sender=EMQXDevice, user_id=user_id, client_id=client_id, ip_address=ip_address
        )
        url = reverse("devices-list")
        data = {
            "event": "client.connected",
            "clientid": "test_client_id",
            "user_id": str(self.user.id),
            "ip_address": "127.0.0.1",
        }
        headers = {"HTTP_X-Webhook-Token": "your_webhook_secret"}
        with override_settings(EMQX_WEBHOOK_SECRET="your_webhook_secret"):
            with self.assertSignalSent(emqx_device_connected) as handler:
                response = self.client.post(url, data, format="json", **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "success"})
        self.assertEqual(handler.signal_args[1]["user_id"], str(self.user.id))  # Verify signal arguments
        self.assertEqual(handler.signal_args[1]["client_id"], "test_client_id")

    @patch("django_emqx.views.EMQXDeviceViewSet.handle_client_connected", return_value=True)
    def test_signal_new_emqx_device_connected(self, mock_handle_client_connected):
        url = reverse("devices-list")
        data = {
            "event": "client.connected",
            "clientid": "new_test_client_id",
            "user_id": str(self.user.id),
            "ip_address": "127.0.0.1",
        }
        headers = {"HTTP_X-Webhook-Token": "your_webhook_secret"}
        with override_settings(EMQX_WEBHOOK_SECRET="your_webhook_secret"):
            with self.assertSignalSent(new_emqx_device_connected):
                response = self.client.post(url, data, format="json", **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "success"})

    @patch("django_emqx.views.EMQXDeviceViewSet.handle_client_disconnected")
    def test_signal_emqx_device_disconnected(self, mock_handle_client_disconnected):
        url = reverse("devices-list")
        data = {
            "event": "client.disconnected",
            "clientid": "test_client_id",
            "user_id": str(self.user.id),
        }
        headers = {"HTTP_X-Webhook-Token": "your_webhook_secret"}
        with override_settings(EMQX_WEBHOOK_SECRET="your_webhook_secret"):
            with self.assertSignalSent(emqx_device_disconnected):
                response = self.client.post(url, data, format="json", **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "success"})

    @contextmanager
    def assertSignalSent(self, signal: Signal):
        """
        Helper method to assert that a signal is sent during a test.
        """
        class SignalHandler:
            def __init__(self):
                self.called = False
                self.signal_args = None

            def handler(self, *args, **kwargs):
                self.called = True
                self.signal_args = (args, kwargs)

        handler = SignalHandler()
        signal.connect(handler.handler, weak=False)  # Ensure strong reference to avoid disconnection
        try:
            yield handler
        finally:
            signal.disconnect(handler.handler)
        self.assertTrue(handler.called, f"Signal {signal} was not sent.")
        print(f"Signal {signal} sent with args: {handler.signal_args}")  # Debugging output
