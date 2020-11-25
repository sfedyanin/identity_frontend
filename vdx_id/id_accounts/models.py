import logging

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
# from id_work_agent.models import ViInterfaceObjectTemplate

logger = logging.getLogger('vdx_id.%s' % __name__)


class ViAccount(models.Model):
    """An associated account for an identity"""
    # Metadata
    active = models.BooleanField(default=False)
    identifier = models.CharField(
        max_length=120, help_text="Used to correlate memberships")

    properties = JSONField(default=dict, blank=True)
    propogate_params_to_identity = JSONField(
        default=list, blank=True,
        help_text="Account parameters to propogate to identity")

    collection_data = JSONField(
        default=dict, blank=True)
    collection_data_variance = models.BooleanField(default=False)

    platform = models.ForeignKey(
        'id_platforms.ViPlatform',
        on_delete=models.PROTECT,
        related_name='accounts')
    identity = models.ForeignKey(
        'id_identities.VdxIdentity',
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='accounts')

    @property
    def account_creation_taskid(self):
        return "id_%s_account_%s_create" % (
            self.identity.pk, self.pk)

    @property
    def task_parameters(self):
        """Returns dicts for parameter resolving"""
        yield self.properties
        yield self.collection_data
        
    def __str__(self):
        return 'P%s_A%s-%s' % (
            self.platform.pk, self.pk, self.identifier)

    def get_absolute_url(self):
        return "%i/" % self.pk

    class Meta:
        verbose_name = 'Access Account'
        unique_together = ('identifier', 'platform')
