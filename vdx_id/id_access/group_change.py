import logging

from enum import Enum

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.postgres.fields import JSONField

from django_fsm import FSMField
from django_fsm import transition
from django_fsm_log.decorators import fsm_log_by

logger = logging.getLogger('vdx_id.%s' % __name__)


class ChangeState(object):
    '''
    Constants to represent the `state`s of the AccountAccess_item
    '''
    PENDING = 'pending'

    APPROVED = 'approved'
    REJECTED = 'rejected'
    COMPLETED = 'completed'
    
    ERROR = 'error'                    # Soft delete state

    CHOICES = (
        (PENDING, PENDING),
        (APPROVED, APPROVED),
        (REJECTED, REJECTED),
        (COMPLETED, COMPLETED),
    )


class ViAccessGroupChangeRequest(models.Model):
    actioned = models.BooleanField(default=False)

    state = FSMField(
        default=ChangeState.PENDING,
        verbose_name='AccessGroup Change State',
        choices=ChangeState.CHOICES,
        protected=True)
    
    date_created = models.DateField(auto_now_add=True)

    description = models.TextField()
    notes = models.TextField()

    priority = models.PositiveSmallIntegerField(
        default=0, help_text="Higher number for higher priority")
    # Todo: Support group removal/creation to optimize access graphs

    access_group = models.ForeignKey(
        'id_access.ViAccessGroup',
        related_name='change_requests', on_delete=models.CASCADE)

    access_groups_add = JSONField(default=list, blank=True)
    access_items_add =JSONField(default=list, blank=True)
    
    access_groups_remove = JSONField(default=list, blank=True)
    access_items_remove = JSONField(default=list, blank=True)

    class Meta:
        verbose_name = 'Access-Group Change Request'
        verbose_name_plural = 'Access-Group Change Requests'

    def __unicode__(self):
        return "Change[%s] %s" % (self.pk, self.access_group.title)


########################################################
# AccessGroupChangeRequest Attributes
########################################################
    def rule_sample(self):
        """Returns True"""
        return True

########################################################
# Change Transitions
########################################################
    # Todo: optimize these for a safer more straight forward
    @fsm_log_by
    @transition(field=state,
                source=["*"],
                target=ChangeState.PENDING)
    def reset_change(self, by=None, *args, **kwargs):
        logger.warn("Resetting state to Pending")

    @fsm_log_by
    @transition(field=state,
                source=[ChangeState.PENDING],
                target=ChangeState.APPROVED,
                conditions=[])
    def approve_change(self, by=None):
        pass

    @fsm_log_by
    @transition(field=state,
                source=ChangeState.APPROVED,
                target=ChangeState.COMPLETED,
                conditions=[])
    def perform_change(self, by=None):
        pass

    @fsm_log_by
    @transition(field=state,
                source=ChangeState.PENDING,
                target=ChangeState.REJECTED,
                conditions=[])
    def reject_change(self, by=None):
        pass


@receiver(pre_save, sender=ViAccessGroupChangeRequest)
def set_request_processing(sender, instance, **kwargs):
    instance.actioned = instance.state in [
        ChangeState.COMPLETED, ChangeState.REJECTED]
