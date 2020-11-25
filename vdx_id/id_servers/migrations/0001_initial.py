# Generated by Django 2.2.10 on 2020-11-23 15:02

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('id_work_agent', '0001_initial'),
        ('id_platforms', '0002_auto_20201123_1502'),
    ]

    operations = [
        migrations.CreateModel(
            name='ViServerGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(default='')),
                ('scan_definition', django.contrib.postgres.fields.jsonb.JSONField(default=dict, help_text="A JSON object: 'ports':[], 'ranges':[{},]")),
                ('scan_results', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('scan_interval', models.DurationField(default='30:00', help_text='Rescan this network group after this much time')),
                ('server_retire_time', models.DurationField(default='60:00', help_text='Remove any server that has not been detected in this time')),
                ('modified', models.DateTimeField(auto_now=True)),
                ('location', django.contrib.postgres.fields.jsonb.JSONField(default=list)),
                ('associated_agent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='server_groups', to='id_work_agent.ViAgent')),
            ],
        ),
        migrations.CreateModel(
            name='ViPlatformServer',
            fields=[
                ('server_pk', models.AutoField(primary_key=True, serialize=False)),
                ('fqdn', models.CharField(max_length=255)),
                ('active', models.BooleanField(default=True, help_text='Servers detected within SrvGrp.server_retire_time')),
                ('properties', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('human_readable_name', models.CharField(blank=True, max_length=256, null=True)),
                ('hostname', models.CharField(blank=True, max_length=256, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('collection_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('location', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list)),
                ('platform', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='servers', to='id_platforms.ViPlatform')),
                ('server_group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='servers', to='id_servers.ViServerGroup')),
            ],
        ),
    ]