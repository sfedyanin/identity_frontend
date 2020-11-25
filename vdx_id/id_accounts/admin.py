from django.contrib import admin
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget

from .models import ViAccount
from id_access.models import ViAccessItem


class AccessItemInline(admin.TabularInline):
    model = ViAccessItem.members.through
    can_delete = False
    max_num = 0


@admin.register(ViAccount)
class ViAccountAdmin(admin.ModelAdmin):
    inlines = [
        AccessItemInline,
    ]
    list_filter = ('platform', 'identity')
    list_display = (
        'identifier', 'identity', 'platform', )
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
