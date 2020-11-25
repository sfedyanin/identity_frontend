import logging

from django.db import models, transaction
from django.conf import settings
from django.dispatch import receiver

from id_accounts.models import ViAccount

from django_fsm import FSMField
from django_fsm import transition
from django_fsm_log.decorators import fsm_log_by

from vdx_id.signals import account_missing_host
from vdx_id.util import resolve_param_string

from vdx_id.engines.graph_net import ViStateGraphEngine
from id_work_agent.models import ViAgentWorkOrder
import web_interface.tasks as web_tasks

logger = logging.getLogger('vdx_id.%s' % __name__)


class Access_itemState(object):
    '''
    Constants to represent the `state`s of the AccountAccess_item
    '''
    INIT = 'initialized'                   # Access_item request initialized

    ACCOUNT_PENDING = 'account_pending'    # Pending account for access_item
    ACCOUNT_PRESENT = 'account_present'

    MEMBERSHIP_REQUESTED = 'membership_requested'
    ACCESS_ITEM_MEMBER = 'member'

    PENDING_REMOVAL = 'pending_removal'
    REMOVAL_REQUESTED = 'removal_requested'
    ACCESS_ITEM_REMOVED = 'removed'

    ERROR = 'error'                    # Soft delete state

    CHOICES = (
        (INIT, INIT),
        (ACCOUNT_PENDING, ACCOUNT_PENDING),
        (ACCOUNT_PRESENT, ACCOUNT_PRESENT),
        (MEMBERSHIP_REQUESTED, MEMBERSHIP_REQUESTED),
        (ACCESS_ITEM_MEMBER, ACCESS_ITEM_MEMBER),
        (PENDING_REMOVAL, PENDING_REMOVAL),
        (ACCESS_ITEM_REMOVED, ACCESS_ITEM_REMOVED),
        (REMOVAL_REQUESTED, REMOVAL_REQUESTED),
    )

    TARGET_CHOICES = (
        (ACCESS_ITEM_MEMBER, ACCESS_ITEM_MEMBER),
        (ACCESS_ITEM_REMOVED, ACCESS_ITEM_REMOVED),
    )


class ViAccessItemRequest(ViStateGraphEngine):
    # One state to rule them all
    state = FSMField(
        default=Access_itemState.INIT,
        verbose_name='Current Access_item State',
        choices=Access_itemState.CHOICES,
    )
    # Target state for the Request (facilitate removal request)
    target_state = FSMField(
        default=Access_itemState.ACCESS_ITEM_MEMBER,
        verbose_name='Target Access_item State',
        choices=Access_itemState.TARGET_CHOICES
    )

    identity = models.ForeignKey(
        'id_identities.VdxIdentity',
        on_delete=models.CASCADE, null=False,
        related_name='access_item_requests'
    )
    account = models.ForeignKey(
        'id_accounts.ViAccount',
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='access_item_requests'
    )
    account_template = models.ForeignKey(
        'id_work_agent.ViAccountTemplate',
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='access_item_requests'
    )
    platform = models.ForeignKey(
        'id_platforms.ViPlatform',
        on_delete=models.PROTECT,
        related_name='access_item_requests'
    )
    access_item = models.ForeignKey(
        'id_access.ViAccessItem',
        on_delete=models.PROTECT, null=True,
        related_name='access_item_requests'
    )

    class Meta:
        verbose_name = 'Access-Item Request'
        verbose_name_plural = 'Access-Item Requests'
        unique_together = ('identity', 'platform', 'access_item'),

    def __unicode__(self):
        return self.access_item.title
