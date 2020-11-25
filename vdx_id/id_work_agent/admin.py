from django.contrib import admin
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget

from id_servers.models import ViServerGroup
from .models import (
    ViAgent, ViAgentPlatformInterface,
    ViAccountTemplate,
    ViAgentWorkOrder)


class ViAgentPlatformInterfaceInline(admin.StackedInline):
    model = ViAgentPlatformInterface
    max_num = 0


class ViServerGroupInline(admin.TabularInline):
    model = ViServerGroup
    max_num = 0
    readonly_fields = ('title', 'description', 'scan_definition')
    can_delete = False
    exclude = ['scan_results', 'location',
        'server_retire_time', 'scan_interval',
        'cleanse_hosts', 'properties']


@admin.register(ViAgent)
class ViAgentAdmin(admin.ModelAdmin):
    inlines = [
        ViAgentPlatformInterfaceInline,
        ViServerGroupInline]


@admin.register(ViAgentPlatformInterface)
class ViAgentPlatformInterfaceAdmin(admin.ModelAdmin):
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }


@admin.register(ViAgentWorkOrder)
class ViAgentWorkOrderAdmin(admin.ModelAdmin):
    list_display = ('name', 'platform', 'api_call',
                    'active', 'complete', 'all_tasks_successful',
                    'created', 'modified')
    list_filter = ('api_call', 'platform', 'queue', 'active', 'complete')
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }


@admin.register(ViAccountTemplate)
class ViAccountTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'description', 'interface')
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
