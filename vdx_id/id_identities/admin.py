from django.contrib import admin
from .models import VdxIdentity
from id_accounts.models import ViAccount
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget


class ViAccountAdmin(admin.StackedInline):
    model = ViAccount
    max_num = 0


@admin.register(VdxIdentity)
class VdxIdentityAdmin(admin.ModelAdmin):
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
    inlines = [ViAccountAdmin, ]
