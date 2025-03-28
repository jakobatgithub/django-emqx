from django.test import TestCase
from django.contrib.admin.sites import site
from django_emqx.admin import EMQXDeviceAdmin, MessageAdmin, NotificationAdmin
from django_emqx.models import EMQXDevice, Message, Notification


class AdminSiteTests(TestCase):
    def test_emqx_device_admin_registered(self):
        # Ensure EMQXDeviceAdmin is registered
        self.assertIn(EMQXDevice, site._registry)
        self.assertIsInstance(site._registry[EMQXDevice], EMQXDeviceAdmin)

    def test_message_admin_registered(self):
        # Ensure MessageAdmin is registered
        self.assertIn(Message, site._registry)
        self.assertIsInstance(site._registry[Message], MessageAdmin)

    def test_notification_admin_registered(self):
        # Ensure NotificationAdmin is registered
        self.assertIn(Notification, site._registry)
        self.assertIsInstance(site._registry[Notification], NotificationAdmin)

    def test_emqx_device_admin_configuration(self):
        # Verify EMQXDeviceAdmin configurations
        admin_instance = site._registry[EMQXDevice]
        self.assertEqual(admin_instance.list_display, (
            "client_id",
            "user",
            "active",
            "last_status",
            "ip_address",
            "last_connected_at",
            "created_at",
        ))
        self.assertEqual(admin_instance.list_filter, ("active", "last_status", "created_at"))
        self.assertEqual(admin_instance.search_fields, ("client_id", "user__username", "ip_address"))
        self.assertEqual(admin_instance.readonly_fields, ("created_at", "last_connected_at"))

    def test_message_admin_configuration(self):
        # Verify MessageAdmin configurations
        admin_instance = site._registry[Message]
        self.assertEqual(admin_instance.list_display, (
            "title",
            "topic",
            "created_by",
            "created_at",
        ))
        self.assertEqual(admin_instance.search_fields, ("title", "topic", "body", "created_by__username"))
        self.assertEqual(admin_instance.list_filter, ("created_at",))
        self.assertEqual(admin_instance.readonly_fields, ("created_at",))

    def test_notification_admin_configuration(self):
        # Verify NotificationAdmin configurations
        admin_instance = site._registry[Notification]
        self.assertEqual(admin_instance.list_display, (
            "recipient",
            "message",
            "delivered_at",
            "is_acknowledged",
            "acknowledged_at",
        ))
        self.assertEqual(admin_instance.list_filter, ("is_acknowledged", "delivered_at"))
        self.assertEqual(admin_instance.search_fields, ("recipient__username", "message__title", "message__topic"))
        self.assertEqual(admin_instance.readonly_fields, ("delivered_at", "acknowledged_at"))
