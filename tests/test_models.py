## tests/test_models.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from django_emqx.models import EMQXDevice, Message, Notification

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

    def test_device_last_connected_at(self):
        self.device.last_connected_at = now()
        self.device.save()
        self.assertIsNotNone(self.device.last_connected_at)

    def test_device_subscribed_topics(self):
        self.device.subscribed_topics = "topic1,topic2"
        self.device.save()
        self.assertEqual(self.device.subscribed_topics, "topic1,topic2")

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

    def test_message_str_representation(self):
        self.assertEqual(str(self.message), "Test Title")
        self.message.title = None
        self.message.topic = "test/topic"
        self.message.save()
        self.assertEqual(str(self.message), "Message to topic 'test/topic'")
        self.message.topic = None
        self.message.body = "Short body text"
        self.message.save()
        self.assertEqual(str(self.message), "Short body text")

class BaseNotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.message = Message.objects.create(
            title="Test Title",
            body="Test Body",
            created_by=self.user,
        )
        self.notification = Notification.objects.create(
            message=self.message,
            recipient=self.user,
            delivered_at=now(),
        )

    def test_notification_creation(self):
        self.assertEqual(self.notification.message, self.message)
        self.assertEqual(self.notification.recipient, self.user)
        self.assertIsNotNone(self.notification.delivered_at)

    def test_notification_acknowledge(self):
        self.assertFalse(self.notification.is_acknowledged)
        self.assertIsNone(self.notification.acknowledged_at)
        self.notification.acknowledge()
        self.assertTrue(self.notification.is_acknowledged)
        self.assertIsNotNone(self.notification.acknowledged_at)

    def test_notification_str_representation(self):
        self.assertEqual(
            str(self.notification),
            f"Notification for {self.user.username} → Test Title"
        )
        self.notification.message.title = None
        self.notification.message.topic = "test/topic"
        self.notification.message.save()
        self.assertEqual(
            str(self.notification),
            f"Notification for {self.user.username} → test/topic"
        )

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
        self.notification = Notification.objects.create(
            message=self.message,
            recipient=self.user,
            delivered_at=now(),
        )

    def test_user_notification_fields(self):
        self.assertEqual(self.notification.message, self.message)
        self.assertEqual(self.notification.recipient, self.user)
        self.assertIsNotNone(self.notification.delivered_at)