## tests/test_models.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from django_emqx.models import EMQXDevice, Message, UserNotification

User = get_user_model()


class EMQXDeviceModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.device = EMQXDevice.objects.create(
            client_id="test_client_id",
            user=self.user,
            active=True,
            last_status="online",
            ip_address="127.0.0.1",
        )

    def test_device_creation(self):
        self.assertEqual(self.device.client_id, "test_client_id")
        self.assertEqual(self.device.user, self.user)
        self.assertTrue(self.device.active)
        self.assertEqual(self.device.last_status, "online")
        self.assertEqual(self.device.ip_address, "127.0.0.1")

    def test_device_str_representation(self):
        self.assertEqual(
            str(self.device),
            "test_client_id (Active) - 127.0.0.1"
        )

class BaseMessageModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.message = Message.objects.create(
            title="Test Title",
            body="Test Body",
            created_by=self.user,
        )

    def test_message_creation(self):
        self.assertEqual(self.message.title, "Test Title")
        self.assertEqual(self.message.body, "Test Body")
        self.assertEqual(self.message.created_by, self.user)
        self.assertIsNotNone(self.message.created_at)

class BaseNotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.message = Message.objects.create(
            title="Test Title",
            body="Test Body",
            created_by=self.user,
        )
        self.notification = UserNotification.objects.create(
            message=self.message,
            recipient=self.user,
            delivered_at=now(),
        )

    def test_notification_creation(self):
        self.assertEqual(self.notification.message, self.message)
        self.assertEqual(self.notification.recipient, self.user)
        self.assertIsNotNone(self.notification.delivered_at)

class MessageModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.message = Message.objects.create(
            title="Test Title",
            body="Test Body",
            created_by=self.user,
        )

    def test_message_fields(self):
        self.assertEqual(self.message.title, "Test Title")
        self.assertEqual(self.message.body, "Test Body")
        self.assertEqual(self.message.created_by, self.user)
        self.assertIsNotNone(self.message.created_at)

class UserNotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.message = Message.objects.create(
            title="Test Title",
            body="Test Body",
            created_by=self.user,
        )
        self.notification = UserNotification.objects.create(
            message=self.message,
            recipient=self.user,
            delivered_at=now(),
        )

    def test_user_notification_fields(self):
        self.assertEqual(self.notification.message, self.message)
        self.assertEqual(self.notification.recipient, self.user)
        self.assertIsNotNone(self.notification.delivered_at)