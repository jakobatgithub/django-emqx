## django_emqx/views.py

import json

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from django.http import JsonResponse
from django.contrib.auth import get_user_model

from .conf import emqx_settings
from .models import EMQXDevice, Message, Notification
from .serializers import EMQXDeviceSerializer, NotificationSerializer
from .mixins import NotificationSenderMixin, ClientEventMixin
from .utils import generate_mqtt_access_token, generate_mqtt_refresh_token
from .signals import emqx_device_connected, new_emqx_device_connected, emqx_device_disconnected


User = get_user_model()


class NotificationViewSet(ViewSet, NotificationSenderMixin):
    """
    A ViewSet for managing user notifications. Allows authenticated users to list and create notifications.
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Retrieve a list of notifications for the authenticated user.

        Args:
            request: The HTTP request object.

        Returns:
            Response: A JSON response containing the list of notifications.
        """
        notifications = Notification.objects.filter(recipient=request.user).select_related("message")
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Create and send notifications to specified users or all users.

        Args:
            request: The HTTP request object containing notification data.

        Returns:
            JsonResponse: A JSON response indicating the success or failure of the operation.
        """
        payload = json.loads(request.body)
        title = payload.get("title")
        body = payload.get("body")
        data = payload.get("data")
        user_ids = payload.get("user_ids", None)
        
        if not title and not body and not data:
            return Response({"error": "Title or body or data are required"}, status=status.HTTP_400_BAD_REQUEST)

        message = Message.objects.create(title=title, body=body, data=data, created_by=request.user)

        if user_ids:
            recipients = User.objects.filter(id__in=user_ids)
        else:
            recipients = User.objects.all()

        self.send_all_notifications(message, recipients)
        return JsonResponse({"message": "Notifications sent successfully"})


class EMQXTokenViewSet(ViewSet):
    """
    A ViewSet for generating MQTT tokens for authenticated users.
    """

    permission_classes = [IsAuthenticated]

    def create(self, request):
        """
        Generate an MQTT token for the authenticated user.

        Args:
            request: The HTTP request object.

        Returns:
            Response: A JSON response containing the MQTT access token and refresh token and user ID.
        """
        user = request.user
        access_token = generate_mqtt_access_token(user)
        refresh_token = generate_mqtt_refresh_token(user)

        return Response({
            "mqtt_access_token": access_token,
            "mqtt_refresh_token": refresh_token,
            "user_id": str(user.id),
        })

    @action(detail=False, methods=["post"])
    def refresh(self, request):
        """
        Use a refresh token to get a new access token.

        Args:
            request: The HTTP request object.

        Returns:
            Response: A JSON response containing the new MQTTm access token.
        """
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Missing refresh token."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            user_id = refresh["user_id"]
            user = User.objects.get(id=user_id)

            access_token = generate_mqtt_access_token(user)
            return Response({"mqtt_access_token": access_token})

        except (TokenError, User.DoesNotExist):
            return Response({"error": "Invalid or expired refresh token."}, status=status.HTTP_401_UNAUTHORIZED)

class EMQXDeviceViewSet(ViewSet, ClientEventMixin):
    """
    A ViewSet for managing EMQX devices and handling client events.
    """

    def get_permissions(self):
        """
        Determine the permissions required for the current action.

        Returns:
            list: A list of permission instances.
        """
        if self.action == 'list':
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = []  # Default or customize as needed
        return [permission() for permission in permission_classes]

    def list(self, request):
        """
        Retrieve a list of all EMQX devices.

        Args:
            request: The HTTP request object.

        Returns:
            Response: A JSON response containing the list of devices.
        """
        devices = EMQXDevice.objects.all()
        serializer = EMQXDeviceSerializer(devices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """
        Handle webhook events for EMQX devices, such as client connections and disconnections.

        Args:
            request: The HTTP request object containing webhook data.

        Returns:
            Response: A JSON response indicating the success or failure of the operation.
        """
        token = request.headers.get("X-Webhook-Token")
        if not token or token != emqx_settings.EMQX_WEBHOOK_SECRET:
            return Response({"error": "Forbidden"}, status=403)

        try:
            body = request.body
            decoded_str = body.decode("utf-8")
            data = json.loads(decoded_str)

            event = data.get("event")
            client_id = data.get("clientid")
            user_id = data.get("user_id")
            ip_address = data.get("ip_address", None)

            if not client_id or not user_id:
                return Response({"error": "Invalid data"}, status=400)

            if user_id == "backend":
                return Response({"status": "success"})

            if event == "client.connected":
                created = self.handle_client_connected(user_id, client_id, ip_address)
                if created:
                    new_emqx_device_connected.send(sender=EMQXDevice, user_id=user_id, client_id=client_id, ip_address=ip_address)    
                else:
                    emqx_device_connected.send(sender=EMQXDevice, user_id=user_id, client_id=client_id, ip_address=ip_address)
            elif event == "client.disconnected":
                updated = self.handle_client_disconnected(user_id, client_id)
                if updated:
                    emqx_device_disconnected.send(sender=EMQXDevice, user_id=user_id, client_id=client_id, ip_address=ip_address)
    
            else:
                return Response({"error": "Unknown event"}, status=400)

            return Response({"status": "success"})

        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON"}, status=400)
