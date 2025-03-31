import unittest
from unittest.mock import patch, MagicMock
from django_emqx.utils import (
    generate_backend_mqtt_token,
    generate_mqtt_access_token,
    send_mqtt_message,
    send_firebase_notification,
    send_firebase_data_message,
    generate_django_secret_key,
    generate_signing_key,
)


class TestUtils(unittest.TestCase):

    @patch("django_emqx.utils.AccessToken")
    def test_generate_backend_mqtt_token(self, MockAccessToken):
        mock_token = MagicMock()
        MockAccessToken.return_value = mock_token

        # Simulate setting attributes on the token
        def setitem_side_effect(key, value):
            mock_token.__dict__[key] = value

        mock_token.__setitem__.side_effect = setitem_side_effect

        generate_backend_mqtt_token()
        self.assertTrue(MockAccessToken.called)
        self.assertEqual(mock_token.__dict__["username"], "backend")
        self.assertIn("acl", mock_token.__dict__)

    @patch("django_emqx.utils.AccessToken.for_user")
    def test_generate_mqtt_token(self, mock_for_user):
        mock_user = MagicMock(id=123)
        mock_token = MagicMock()
        mock_for_user.return_value = mock_token

        # Simulate setting attributes on the token
        def setitem_side_effect(key, value):
            mock_token.__dict__[key] = value

        mock_token.__setitem__.side_effect = setitem_side_effect

        generate_mqtt_access_token(mock_user)
        self.assertTrue(mock_for_user.called)
        self.assertEqual(mock_token.__dict__["username"], "123")
        self.assertIn("acl", mock_token.__dict__)

    @patch("django_emqx.utils.json.dumps")
    @patch("django_emqx.utils.get_mqtt_client")
    def test_send_mqtt_message(self, mock_get_mqtt_client, mock_json_dumps):
        mqtt_client = MagicMock()
        mock_get_mqtt_client.return_value = mqtt_client
        mock_recipient = MagicMock(id=123)
        mock_json_dumps.return_value = '{"msg_id": "1", "title": "Test", "body": "Message", "data": "Data"}'
        message = MagicMock()
        send_mqtt_message(mock_recipient, message)
        mqtt_client.publish.assert_called_with("user/123/", '{"msg_id": "1", "title": "Test", "body": "Message", "data": "Data"}', qos = 1)

    @patch("django_emqx.utils.messaging.send")
    def test_send_firebase_notification(self, mock_send):
        mock_send.return_value = "Success"
        token = "test_token"
        title = "Test Title"
        body = "Test Body"

        response = send_firebase_notification(token, title, body)
        self.assertTrue(mock_send.called)
        self.assertEqual(response, "Success")

    @patch("django_emqx.utils.messaging.send")
    def test_send_firebase_data_message(self, mock_send):
        mock_send.return_value = "Success"
        token = "test_token"
        msg_id = "1"
        title = "Test Title"
        body = "Test Body"

        response = send_firebase_data_message(token, msg_id, title, body)
        self.assertTrue(mock_send.called)
        self.assertEqual(response, "Success")

    def test_generate_django_secret_key(self):
        secret_key = generate_django_secret_key()
        self.assertEqual(len(secret_key), 50)
        self.assertTrue(all(c.isalnum() or c in "!@#$%^&*(-_=+)" for c in secret_key))

    def test_generate_signing_key(self):
        signing_key = generate_signing_key()
        self.assertEqual(len(signing_key), 64)  # 32 bytes in hex = 64 characters
        self.assertTrue(all(c in "0123456789abcdef" for c in signing_key))