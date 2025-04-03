import unittest
from unittest.mock import patch, MagicMock
from django_emqx.mqtt import MQTTClient


class TestMQTTClient(unittest.TestCase):

    @patch('django_emqx.mqtt.mqtt.Client')
    @patch('django_emqx.mqtt.generate_backend_mqtt_token')
    def test_initialization_and_connection(self, mock_generate_token, mock_mqtt_client):
        mock_generate_token.return_value = "mock_token"
        mock_client_instance = MagicMock()
        mock_mqtt_client.return_value = mock_client_instance

        MQTTClient(broker="test_broker", port=1883, keepalive=60)

        mock_generate_token.assert_called_once()
        mock_mqtt_client.assert_called_once()
        mock_client_instance.username_pw_set.assert_called_with(username='backend', password="mock_token")
        mock_client_instance.connect.assert_called_with("test_broker", 1883, 60)
        mock_client_instance.loop_start.assert_called_once()

    @patch('django_emqx.mqtt.mqtt.Client')
    def test_publish(self, mock_mqtt_client):
        mock_client_instance = MagicMock()
        mock_mqtt_client.return_value = mock_client_instance

        client = MQTTClient(broker="test_broker")
        client.publish(topic="test/topic", payload="test_message", qos=1)

        mock_client_instance.publish.assert_called_with("test/topic", "test_message", 1)

    @patch('django_emqx.mqtt.mqtt.Client')
    def test_disconnect(self, mock_mqtt_client):
        mock_client_instance = MagicMock()
        mock_mqtt_client.return_value = mock_client_instance

        client = MQTTClient(broker="test_broker")
        client.disconnect()

        mock_client_instance.loop_stop.assert_called_once()
        mock_client_instance.disconnect.assert_called_once()

    @patch('django_emqx.mqtt.mqtt.Client')
    @patch('builtins.print')
    def test_on_connect(self, mock_print, mock_mqtt_client):
        mock_client_instance = MagicMock()
        mock_mqtt_client.return_value = mock_client_instance

        client = MQTTClient(broker="test_broker")
        client.on_connect(mock_client_instance, None, None, 0)

        # Verify successful connection message was printed
        mock_print.assert_any_call("✅ MQTT connected successfully")

    @patch('django_emqx.mqtt.mqtt.Client')
    def test_on_disconnect(self, mock_mqtt_client):
        mock_client_instance = MagicMock()
        mock_mqtt_client.return_value = mock_client_instance

        client = MQTTClient(broker="test_broker")
        client.on_disconnect(mock_client_instance, None, 0)

        # Verify reconnection attempt
        mock_client_instance.reconnect.assert_called_once()
