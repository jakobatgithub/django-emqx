from django.contrib import admin
from .models import EMQXDevice, Message, Notification


@admin.register(EMQXDevice)
class EMQXDeviceAdmin(admin.ModelAdmin):
    list_display = (
        "client_id",
        "user",
        "active",
        "last_status",
        "ip_address",
        "last_connected_at",
        "created_at",
    )
    list_filter = ("active", "last_status", "created_at")
    search_fields = ("client_id", "user__username", "ip_address")
    readonly_fields = ("created_at", "last_connected_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "topic",
        "created_by",
        "created_at",
    )
    search_fields = ("title", "topic", "body", "created_by__username")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "recipient",
        "message",
        "delivered_at",
        "is_acknowledged",
        "acknowledged_at",
    )
    list_filter = ("is_acknowledged", "delivered_at")
    search_fields = ("recipient__username", "message__title", "message__topic")
    readonly_fields = ("delivered_at", "acknowledged_at")
