import os

from django.core.management.base import BaseCommand
from django.conf import settings
from django_emqx.conf import emqx_settings
from django.urls import reverse

from importlib import resources
from jinja2 import Environment, BaseLoader


def load_template_from_package():
    # Path: django_emqx/templates/emqx/emqx.conf.j2
    with resources.files('django_emqx.templates.emqx').joinpath('emqx.conf.j2').open('r') as f:
        template_str = f.read()

    env = Environment(loader=BaseLoader())
    template = env.from_string(template_str)
    return template


class Command(BaseCommand):
    help = 'Generate EMQX config from Django settings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            help='Path to save the generated emqx.conf file',
            default=os.path.join(settings.BASE_DIR, 'config', 'generated', 'emqx.conf'),
        )

    def handle(self, *args, **options):
        output_path = options['output']

        template = load_template_from_package()
        if hasattr(settings, 'BASE_URL') and settings.BASE_URL:
            DEVICE_WEBHOOK_URL = f"{settings.BASE_URL}{reverse('devices-list')}"
        else:
            DEVICE_WEBHOOK_URL = f"http://localhost:8000{reverse('devices-list')}"
    
        config = template.render({
            'EMQX_NODE_COOKIE': emqx_settings.EMQX_NODE_COOKIE,
            'EMQX_WEBHOOK_SECRET': emqx_settings.EMQX_WEBHOOK_SECRET,
            'SIMPLE_JWT_SIGNING_KEY': settings.SIMPLE_JWT['SIGNING_KEY'],
            'EMQX_TLS_CA_CERTS': emqx_settings.EMQX_TLS_CA_CERTS,
            'DEVICE_WEBHOOK_URL': DEVICE_WEBHOOK_URL,
        })

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(config)

        self.stdout.write(self.style.SUCCESS(f"Generated EMQX config at {output_path}"))
