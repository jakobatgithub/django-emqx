import os

from django.core.management.base import BaseCommand
from django.conf import settings
from django_emqx.conf import emqx_settings

from jinja2 import Environment, FileSystemLoader


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

        # Template location within the app
        template_dir = os.path.join(os.path.dirname(__file__), '../../../templates/emqx')
        template_dir = os.path.abspath(template_dir)

        # Render the template
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template("emqx.conf.j2")

        config = template.render({
            'EMQX_NODE_COOKIE': emqx_settings.EMQX_NODE_COOKIE,
            'EMQX_WEBHOOK_SECRET': emqx_settings.EMQX_WEBHOOK_SECRET,
            'SIMPLE_JWT_SIGNING_KEY': settings.SIMPLE_JWT['SIGNING_KEY'],
        })

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(config)

        self.stdout.write(self.style.SUCCESS(f"Generated EMQX config at {output_path}"))
