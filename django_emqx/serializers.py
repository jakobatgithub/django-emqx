## django_emqx/serializers.py

from rest_framework import serializers

from .models import EMQXDevice, Notification

class EMQXDeviceSerializer(serializers.ModelSerializer):
    """
    Serializer for the EMQXDevice model. Converts model instances into JSON format
    and validates incoming data for creating or updating EMQXDevice objects.
    """
    class Meta:
        model = EMQXDevice
        fields = ['id', 'user', 'client_id', 'active', 'last_status', 'last_connected_at']


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.
    Flattens message fields (title and body) and supports acknowledgement.
    """
    title = serializers.CharField(source='message.title', read_only=True, required=False)
    body = serializers.CharField(source='message.body', read_only=True, required=False)

    class Meta:
        model = Notification
        fields = [
            'id',
            'title',
            'body',
            'recipient',
            'delivered_at',
            'acknowledged_at',
            'is_acknowledged',
        ]
        read_only_fields = ['title', 'body', 'delivered_at', 'acknowledged_at', 'is_acknowledged']

    def update(self, instance, validated_data):
        if self.context['request'].data.get('acknowledge'):
            instance.acknowledge()
        return super().update(instance, validated_data)

