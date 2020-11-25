import logging
from django import forms
from django.contrib import admin
from django_fsm_log.admin import StateLogInline
from django_json_widget.widgets import JSONEditorWidget
from django.contrib.postgres import fields
from fsm_admin.mixins import FSMTransitionMixin
from .models import ViAccessItem, ViAccessGroup
from .access_request import ViAccessItemRequest
from .group_request import ViAccessGroupRequest
from .group_change import ViAccessGroupChangeRequest


logger = logging.getLogger('vdx_id.%s' % __name__)


class ItemMemberInline(admin.TabularInline):
    model = ViAccessItem.members.through
    extra = 0


@admin.register(ViAccessItem)
class ViAccessItemAdmin(admin.ModelAdmin):
    list_filter = ('platform', 'identifier')
    list_display = (
        'identifier', 'platform',)
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
    inlines = [ItemMemberInline]


def reinitialize_request(modeladmin, request, queryset):
    requests = []
    for req in queryset:
        req.reinitialize_state()
        requests.append(req)
    ViAccessItemRequest.objects.bulk_update(requests, ['state'])

reinitialize_request.short_description = "Reinitialize Requests"


@admin.register(ViAccessItemRequest)
class ViAccessItemRequestAdmin(FSMTransitionMixin, admin.ModelAdmin):
    # The name of one or more FSMFields on the model to transition
    list_display = (
        'identity', 'access_item', 'platform',
        'state', 'target_state', 'processing')
    list_filter = ('identity', 'state', 'processing')
    # readonly_fields = ('identity', 'state', 'processing')
    fsm_field = ['state', ]
    inlines = [StateLogInline]
    actions = [reinitialize_request,]


class GroupMemberInline(admin.TabularInline):
    model = ViAccessGroup.members.through
    extra = 0


class AccessGroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        plat_acc_items = ViAccessItem.objects.filter(
            platform=self.instance.platform)
        w = self.fields['access_items'].widget
        choices = []
        for acc_item in plat_acc_items:
            choices.append((acc_item.id, acc_item.identifier))
        w.choices = choices


@admin.register(ViAccessGroup)
class AccessGroupAdmin(admin.ModelAdmin):
    read_only_fields = ('stored_access_state',)
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }
    inlines = [GroupMemberInline]
    form = AccessGroupForm

    def get_queryset(self, request):
        qs = super(AccessGroupAdmin, self).get_queryset(request)
        qs = qs.prefetch_related(
            'access_groups', 'access_items')
        return qs


@admin.register(ViAccessGroupRequest)
class ViAccessGroupRequestAdmin(FSMTransitionMixin, admin.ModelAdmin):
    # The name of one or more FSMFields on the model to transition
    list_display = (
        'identity', 'access_group', 'parent_request',
        'state', 'processing')
    list_filter = ('state', 'processing', 'parent_request')
    # readonly_fields = ('state', 'processing')
    fsm_field = ['state', ]
    inlines = [StateLogInline]


@admin.register(ViAccessGroupChangeRequest)
class ViAccessGroupChangeRequestAdmin(FSMTransitionMixin, admin.ModelAdmin):
    # The name of one or more FSMFields on the model to transition
    list_display = (
        'access_group', 'priority', 'description', 'state', 'actioned')
    list_filter = ('access_group', 'actioned', 'state', 'priority')
    readonly_fields = ('actioned', 'priority', 'state')
    fsm_field = ['state', ]
