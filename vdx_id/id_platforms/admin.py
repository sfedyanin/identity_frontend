from django import forms
from django.contrib import admin

from django_json_widget.widgets import JSONEditorWidget
from django.contrib.postgres import fields

from .models import ViPlatform
from id_servers.models import ViPlatformServer


def run_collection(modeladmin, request, queryset):
    for plat in queryset:
        plat.request_collection()
run_collection.short_description = "Collect Platform"


@admin.register(ViPlatform)
class ViPlatformAdmin(admin.ModelAdmin):
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
    readonly_fields = ('collection_task',)
    actions = [run_collection]
    list_display = (
        'title', 'interface',
        'generate_new_accounts', 'generate_new_access_items')
    list_filter = ('interface',)
