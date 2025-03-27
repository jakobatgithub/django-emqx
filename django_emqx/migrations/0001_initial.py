# Generated by Django 5.1.6 on 2025-03-26 11:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EMQXDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_id', models.CharField(help_text='Unique identifier for the MQTT client', max_length=255, unique=True, verbose_name='MQTT Client ID')),
                ('active', models.BooleanField(default=True, help_text='Indicates whether the device is active', verbose_name='Is active')),
                ('last_connected_at', models.DateTimeField(blank=True, help_text='Timestamp of the last successful connection', null=True, verbose_name='Last connected at')),
                ('last_status', models.CharField(choices=[('online', 'Online'), ('offline', 'Offline'), ('error', 'Error')], default='offline', help_text='Last known status of the device', max_length=20, verbose_name='Last known status')),
                ('subscribed_topics', models.TextField(blank=True, help_text='Comma-separated list of topics the device subscribes to', verbose_name='Subscribed Topics')),
                ('ip_address', models.GenericIPAddressField(blank=True, help_text='Last known IP address of the device', null=True, verbose_name='Last known IP address')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Creation date')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mqtt_devices', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivered_at', models.DateTimeField(auto_now_add=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='django_emqx.message')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
