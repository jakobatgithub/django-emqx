## django_emqx/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class EMQXDevice(models.Model):
    """
    Represents an EMQX MQTT device associated with a user.

    Fields:
        id (AutoField): Primary key for the device.
        client_id (CharField): Unique identifier for the MQTT client.
        active (BooleanField): Indicates whether the device is active.
        user (ForeignKey): Reference to the user owning the device.
        last_connected_at (DateTimeField): Timestamp of the last successful connection.
        last_status (CharField): Last known status of the device (e.g., online, offline, error).
        subscribed_topics (TextField): Comma-separated list of topics the device subscribes to.
        ip_address (GenericIPAddressField): Last known IP address of the device.
        created_at (DateTimeField): Timestamp when the device was created.
    """
    id = models.AutoField(
        verbose_name="ID",
        primary_key=True,
        auto_created=True,
    )
    client_id = models.CharField(
        verbose_name="EMQX Client ID",
        max_length=255,
        unique=True,
        help_text="Unique identifier for the EMQX client"
    )
    active = models.BooleanField(
        verbose_name="Is active",
        default=True,
        help_text="Indicates whether the device is active"
    )
    user = models.ForeignKey(
        get_user_model(),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="emqx_devices",
    )
    last_connected_at = models.DateTimeField(
        verbose_name="Last connected at",
        null=True,
        blank=True,
        help_text="Timestamp of the last successful connection"
    )
    last_status = models.CharField(
        verbose_name="Last known status",
        max_length=20,
        choices=[("online", "Online"), ("offline", "Offline"), ("error", "Error")],
        default="offline",
        help_text="Last known status of the device"
    )
    subscribed_topics = models.TextField(
        verbose_name="Subscribed Topics",
        blank=True,
        help_text="Comma-separated list of topics the device subscribes to"
    )
    ip_address = models.GenericIPAddressField(
        verbose_name="Last known IP address",
        blank=True,
        null=True,
        help_text="Last known IP address of the device"
    )
    created_at = models.DateTimeField(
        verbose_name="Creation date", auto_now_add=True, null=True
    )

    def __str__(self):
        return f"{self.client_id} ({'Active' if self.active else 'Inactive'}) - {self.ip_address or 'No IP'}"


class BaseMessage(models.Model):
    """
    Abstract base model for messages.

    Fields:
        - topic: Optional MQTT topic the message is published to.
        - title: Optional title for display purposes.
        - body: Optional body text.
        - data: Optional payload (structured JSON).
        - created_at: Timestamp when the message was created.
        - created_by: Optional user who created the message.
    """
    topic = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Optional MQTT topic to publish this message to. Leave blank for non-MQTT messages."
    )

    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Optional short title for the message, suitable for UI display."
    )

    body = models.TextField(
        null=True,
        blank=True,
        help_text="Optional longer body content of the message."
    )

    data = models.JSONField(
        null=True,
        blank=True,
        help_text="Optional structured payload (e.g., for app actions or push notifications)."
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the message was created."
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        null=True,
        blank=True,
        help_text="Optional user who created or sent the message."
    )

    class Meta:
        abstract = True

    def __str__(self):
        if self.title:
            return self.title
        elif self.topic:
            return f"Message to topic '{self.topic}'"
        elif self.body:
            return self.body[:50] + ('...' if len(self.body) > 50 else '')
        return f"Untitled message (ID: {self.id})"


class BaseNotification(models.Model):
    """
    Abstract base model for notifications.

    Fields:
        - message: The related message for the notification.
        - recipient: The user who is the recipient of the notification.
        - delivered_at: Timestamp when the notification was delivered.
        - acknowledged_at: Timestamp when the user acknowledged the notification.
        - is_acknowledged: Boolean flag indicating if the notification was acknowledged.
    """
    message = models.ForeignKey(
        'django_emqx.Message',
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="The message this notification is based on."
    )

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="The user who should receive this notification."
    )

    delivered_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the notification was created or delivered."
    )

    acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the user acknowledged or read the notification."
    )

    is_acknowledged = models.BooleanField(
        default=False,
        help_text="Indicates whether the user has acknowledged the notification."
    )

    class Meta:
        abstract = True

    def acknowledge(self):
        """Helper method to acknowledge the notification."""
        self.is_acknowledged = True
        self.acknowledged_at = timezone.now()
        self.save()

    def __str__(self):
        msg_label = getattr(self.message, 'title', None) or getattr(self.message, 'topic', None) or f"Message {self.message_id}"
        return f"Notification for {self.recipient.username} → {msg_label}"        


# Concrete Django versions of the models
class Message(BaseMessage):
    """
    Concrete implementation of BaseMessage.
    """
    class Meta:
        abstract = False

class Notification(BaseNotification):
    """
    Concrete implementation of BaseNotification.
    """
    class Meta:
        abstract = False
