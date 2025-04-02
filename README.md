# Django EMQX

A Django app for integrating MQTT communication with EMQX, featuring secure topic-based access control, JWT authentication, TLS encryption, and optional Firebase Cloud Messaging support. See [notification_test](https://github.com/jakobatgithub/notification_test) for a Demo how to use this Django app.

## Features

This project incorporates several security and efficiency measures to ensure seamless and secure communication between the backend and frontend.

- **Topic-based Access Control:**
    Each frontend user is restricted to a single dedicated MQTT topic for subscriptions, ensuring isolation between users. The backend, however, has the necessary permissions to publish messages to all topics, enabling efficient and controlled message distribution.

- **JWT-based Authentication & Authorization:**
    JSON Web Tokens (JWT) are used for authenticating MQTT clients at EMQX and to enforce access and control lists (ACLs). This ensures that each client has restricted access based on predefined permissions, preventing unauthorized subscriptions or publications. For JWT we use `rest_framework_simplejwt`. Settings for JWT authentication are controlled by the settings for JWT (i.e., `SIMPLE_JWT` in `settings.py`).

- **Secure MQTT Communication with TLS:**
    To protect data transmission, the connection between the frontend and the EMQX broker is secured using Transport Layer Security (TLS). This encryption prevents eavesdropping and tampering, ensuring a confidential and secure communication channel.

- **Automated Device Registration via Secure Webhooks:**
    A webhook secured with JWT authentication is used to register MQTT devices with the backend.

- **Integration with Firebase Cloud Messaging (FCM):**
    Notifications are also sent via Firebase in case it is installed.

## Installation

Basic install:

```bash
pip install django-emqx
```
If you want FCM (Firebase Cloud Messaging) support:

```bash
pip install django-emqx[fcm]
```

## Project Structure

  - **django_emqx/**: Django app for handling notifications.
    -- **management/**: Provides `generate_emqx_config.py` for generating an `emqx.conf` file from settings.
    - **migrations/**: Database migrations for the notifications app.
    - **templates/**: Provides a Jinja template to generate an `emqx.conf` file from settings with the management command `python manage.py generate_emqx_config`.
    - **__init__.py**: Provides a global (app-wide) instance of `MQTTClient`.
    - **conf.py**: Defines the default settings.
    - **models.py**: Contains the data models for `EMQXDevice`, `Message`, and `UserNotification`.
    - **mixins.py**: Provides mixins for the views.
    - **mqtt.py**: Provides `MQTTClient` which connects the backend to the EMQX server.
    - **serializers.py**: Serilizers for the `EMQXDevice` and `UserNotification` models.
    - **signals.py**: Defines signals which are sent when an EMQX device connects or disconnects.
    - **urls.py**: URL routing for the Django app.
    - **utils.py**: Utility functions for generating JWT tokens, sending notifications, and generating keys.
    - **views.py**: Django views for handling HTTP requests.
  - **tests/**: Contains unit tests for views and models.
  - **README.md**: Project documentation and setup instructions.

## License

This project is licensed under the [MIT License](./LICENSE).  
Feel free to use, modify, and distribute — just keep the original license and credit.
