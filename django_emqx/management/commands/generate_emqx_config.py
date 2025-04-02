import os

from django.core.management.base import BaseCommand, CommandError
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
        parser.add_argument(
            '--base-url',
            type=str,
            help='Base URL to use for webhook endpoints. Defaults to http://localhost:8000.',
            default='http://localhost:8000/',
        )
        parser.add_argument(
            '--enable-tls',
            action='store_true',
            help='Enable TLS configuration. Requires --keyfile and --certfile.',
        )
        parser.add_argument(
            '--keyfile',
            type=str,
            help='Path to TLS key file to include in the config.',
        )
        parser.add_argument(
            '--certfile',
            type=str,
            help='Path to TLS certificate file to include in the config.',
        )

    def handle(self, *args, **options):
        output_path = options['output']
        base_url = options['base_url']

        enable_tls = options['enable_tls']
        keyfile = options.get('keyfile')
        certfile = options.get('certfile')

        if enable_tls and (not keyfile or not certfile):
            raise CommandError("TLS is enabled, but --keyfile and --certfile must be provided.")

        # Ensure no trailing slash
        base_url = base_url.rstrip('/')
        device_webhook_url = f"{base_url}{reverse('devices-list')}"

        template = load_template_from_package()
    
        config = template.render({
            'EMQX_NODE_COOKIE': emqx_settings.EMQX_NODE_COOKIE,
            'EMQX_WEBHOOK_SECRET': emqx_settings.EMQX_WEBHOOK_SECRET,
            'SIMPLE_JWT_SIGNING_KEY': settings.SIMPLE_JWT['SIGNING_KEY'],
            'EMQX_TLS_CA_CERTS': emqx_settings.EMQX_TLS_CA_CERTS,
            'DEVICE_WEBHOOK_URL': device_webhook_url,
            'ENABLE_TLS': enable_tls,
            'TLS_KEYFILE': keyfile,
            'TLS_CERTFILE': certfile,
        })

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(config)

        self.stdout.write(self.style.SUCCESS(f"Generated EMQX config at {output_path}"))
