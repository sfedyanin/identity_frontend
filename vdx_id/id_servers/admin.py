from django.contrib import admin
from .models import ViPlatformServer, ViServerGroup
from django_json_widget.widgets import JSONEditorWidget
from django.contrib.postgres import fields


def scan_group(modeladmin, request, queryset):
    for sgroup in queryset:
        sgroup.perform_scan()


def mark_inactive(modeladmin, request, queryset):
    servers = []
    for server in queryset:
        server.active = False
        servers.append(server)
    ViPlatformServer.objects.bulk_update(servers, ['active'])


def assign_all_to_same_platform(modeladmin, request, queryset):
    plat = queryset.exclude(platform__isnull=True)
    if plat.exists():
        plat = plat.first().platform
    else:
        raise Exception("No platform found in selection")
    for server in queryset:
        server.platform = plat
        server.save()


scan_group.short_description = "Scan Server Groups"
mark_inactive.short_description = "Mark Inactive"
assign_all_to_same_platform.short_description = "Assign to first platform"


@admin.register(ViPlatformServer)
class ViServerAdmin(admin.ModelAdmin):
    read_only_fields = ('created', 'modified', 'active')
    list_display = (
        'fqdn', 'platform', 'server_group', 'location',
        'created', 'modified', 'active')
    list_filter = ('platform', 'server_group', 'active')
    actions = [mark_inactive, assign_all_to_same_platform]
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }


@admin.register(ViServerGroup)
class ViServerGroupAdmin(admin.ModelAdmin):
    read_only_fields = ('scan_results',)
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
    actions = [scan_group]
