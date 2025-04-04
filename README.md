# Django EMQX

**Django EMQX** is a Django app that enables secure, scalable, and efficient MQTT communication with an [EMQX](https://www.emqx.io/) broker. It offers topic-level access control, JWT-based client authentication, TLS encryption, and optional Firebase Cloud Messaging (FCM) support.

📦 See the [notification_test](https://github.com/jakobatgithub/notification_test) repo for a working demo.


## 📦 Installation

Install the core package:
```bash
pip install "django-emqx @ git+ssh://git@github.com/jakobatgithub/django-emqx.git@main"
```
Install with Firebase support:
```bash
pip install "django-emqx[fcm] @ git+ssh://git@github.com/jakobatgithub/django-emqx.git@main"
```

Full install with packages for development and testing:
```bash
pip install "django-emqx[fcm,test,dev] @ git+ssh://git@github.com/jakobatgithub/django-emqx.git@main"
```


## 🚀 Features

### 🔒 Topic-Based Access Control
- Each frontend user is assigned a dedicated MQTT topic for subscriptions.
- Backend retains full publish access to all topics to enable centralized control.

### 🔐 JWT Authentication & Authorization
- MQTT clients authenticate via [JSON Web Tokens (JWT)](https://jwt.io/).
- Uses [`rest_framework_simplejwt`](https://github.com/jazzband/django-rest-framework-simplejwt) for issuing and verifying JWTs.
- MQTT Access Control Lists (ACLs) are enforced based on token claims.
- All JWT settings can be managed via the `SIMPLE_JWT` configuration in `settings.py`.

### 📡 TLS-Encrypted MQTT Communication
- Secures the MQTT connection between clients and EMQX using TLS.
- Prevents eavesdropping and ensures message integrity.

### 🔁 Secure Webhook-Based Device Registration
- Devices are registered through a dedicated webhook.
- Webhook access is secured using a webhook secret.
- Signals are provided for `emqx_device_connected`, `new_emqx_device_connected`, and  `emqx_device_disconnected`

### 🔔 Optional Firebase Cloud Messaging (FCM) Support
- Enables push notifications via Firebase if installed.



## 🧭 Project Structure

```text
django_emqx/
├── management/                 # Admin commands (e.g., generate_emqx_config)
│   └── generate_emqx_config.py # Management comamnd for generating an emqx.conf file from a template.
├── migrations/                 # Database migrations
├── templates/                  
│   └── emqx.conf.j2            # Jinja2 template for EMQX config generation
├── __init__.py                 # Initializes global MQTTClient instance
├── admin.py                    # Registers the models at the admin interface
├── conf.py                     # Default configuration values
├── models.py                   # EMQXDevice, Message, and Notification models
├── mixins.py                   # Reusable view logic
├── mqtt.py                     # MQTTClient logic to connect backend to EMQX
├── serializers.py              # Serializers for EMQXDevice and Notification models
├── signals.py                  # Device connection/disconnection signals
├── urls.py                     # App URL routes
├── utils.py                    # Helpers for JWT generation, FCM, secret key generation
├── views.py                    # API views for registration and messaging
tests/                          # Unit tests for views and models
README.md                       # Project overview and usage guide
```

## Testing

For testing, install with testing packages and run tests with `pytest` and `coverage` support:
```bash
pip install "django-emqx[test] @ git+ssh://git@github.com/jakobatgithub/django-emqx.git@main"
pytest --cov=django_emqx
```

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

> Feel free to use, modify, and distribute — just retain the original license and give credit where it's due.
