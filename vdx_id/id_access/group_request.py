import rules
import logging
import datetime

from django.db import models
from django.db import transaction

from django_fsm import FSMField, RETURN_VALUE, transition
from django_fsm_log.decorators import fsm_log_by
from django.contrib.postgres.fields import JSONField
from vdx_id.engines.graph_net import ViStateGraphEngine
from channels.layers import get_channel_layer
from rest_framework.reverse import reverse
import web_interface.tasks as web_tasks

from .access_request import ViAccessItemRequest

channel_layer = get_channel_layer()
logger = logging.getLogger('vdx_id.%s' % __name__)


class Access_groupState(object):
    '''
    Constants to represent the `state`s of the AccountAccess_item
    '''
    INIT = 'initialized'                   # Access_item request initialized

    AUTHORIZATION_REJECTED = 'authorization_rejected'
    AUTHORIZATION_REQUESTED = 'authorization_requested'
    AUTHORIZATION_PENDING = 'authorization_pending'
    ACCESS_GROUP_MEMBER = 'member'
    ACCESS_GROUP_REMOVED = 'removed'

    ERROR = 'error'                    # Soft delete state

    CHOICES = (
        (INIT, INIT),
        (AUTHORIZATION_REJECTED, AUTHORIZATION_REJECTED),
        (AUTHORIZATION_REQUESTED, AUTHORIZATION_REQUESTED),
        (AUTHORIZATION_PENDING, AUTHORIZATION_PENDING),
        (ACCESS_GROUP_MEMBER, ACCESS_GROUP_MEMBER),
        (ACCESS_GROUP_REMOVED, ACCESS_GROUP_REMOVED),
    )

    TARGET_CHOICES = (
        (ACCESS_GROUP_MEMBER, ACCESS_GROUP_MEMBER),
        (ACCESS_GROUP_REMOVED, ACCESS_GROUP_REMOVED),
    )


class ViAccessGroupRequest(ViStateGraphEngine):
    """AccessGroup Requests are working objects of the Identity System.
    A user can create a group request specifying an identity and group.
    The system will then begin to request and provision access accordingly"""
    # One state to rule them all
    state = FSMField(
        default=Access_groupState.INIT,
        verbose_name='Group Request State',
        choices=Access_groupState.CHOICES)

    # Target state for the Request (facilitate removal request)
    target_state = FSMField(
        default=Access_groupState.ACCESS_GROUP_MEMBER,
        verbose_name='Target State',
        choices=Access_groupState.TARGET_CHOICES)
    
    identity = models.ForeignKey(
        'id_identities.VdxIdentity',
        on_delete=models.PROTECT,
        related_name='access_group_requests')
    access_group = models.ForeignKey(
        'id_access.ViAccessGroup',
        on_delete=models.PROTECT,
        related_name='access_group_requests')

    authorization_state = JSONField(default=dict, blank=True)
    
    attention_identities = models.ManyToManyField(
        "id_identities.VdxIdentity", related_name='auth_attention',
        blank=True)
    
    access_duration = models.DurationField(
        blank=True, null=True,
        help_text='If > 0, will automatically revoke access once duration elapsed.'
            'Will inherit AccessGroup duration if None. Child memberships will inherit this duration.')

    justification = models.TextField(default="", blank=True)

    parent_request = models.ForeignKey(
        "self", blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name="child_group_requests")
        
    class Meta:
        verbose_name = 'Access-Group Request'
        verbose_name_plural = 'Access-Group Requests'

    def __unicode__(self):
        return self.access_group.title

    @property
    def get_absolute_url(self):
        return reverse(
            'api:iam:id_access:group_request-detail', kwargs={'pk': self.pk})

    @property
    def data_foldername(self):
        return "GroupRequests"

    @property
    def approval_states(self):
        states = []
        for rn, rs in self.authorization_state.items():
            if rs:
                states.append(rs['state'].lower())
            else:
                states.append(False)
        return states
