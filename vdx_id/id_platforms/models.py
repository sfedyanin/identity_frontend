import logging

import celery

from time import strftime

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import CrontabSchedule
from django_celery_beat.models import PeriodicTask
from django.core.cache import cache
from django.contrib.postgres.fields import JSONField

from id_work_agent.models import ViAgentPlatformInterface, ViAgentWorkOrder


logger = logging.getLogger('vdx_id.%s' % __name__)


class ViPlatform(models.Model):
    """A platform managed by the application.
    Comprised of ServerGroups, and associated AccessItems"""

    # Task used to trigger a collection against all accounts
    collection_task_sig = 'id_platforms.tasks.read_platform'
    properties = JSONField(default=dict, blank=True)

    # Metadata
    title = models.CharField(max_length=40)
    description = models.CharField(max_length=40)

    collection_task = models.ForeignKey(
        PeriodicTask, on_delete=models.PROTECT,
        related_name='platform_collections',
        null=True, blank=True)

    interface = models.ForeignKey(
        ViAgentPlatformInterface,
        on_delete=models.PROTECT,
        related_name='platforms',
        null=True, blank=True)

    default_account_template = models.ForeignKey(
        'id_work_agent.ViAccountTemplate',
        on_delete=models.PROTECT,
        related_name='platforms', null=True)
    
    generate_new_accounts = models.BooleanField(
        default=False,
        help_text="Allows collections to generate new Accounts")
    generate_new_access_items = models.BooleanField(
        default=False,
        help_text="Allows collections to generate new Entitlements")

    def __str__(self):
        return '%s (%s servers)' % (self.title, self.servers.count())

    @property
    def task_parameters(self):
        """Returns dicts for parameter resolving"""
        yield self.properties

    def get_absolute_url(self):
        return "%i/" % self.pk

    def get_collection_id(self):
        coll_id = "COLL_P%s_%s" % (
            self.id, strftime(settings.COLL_TSTAMP))
        logger.debug("Created Collection ID: %s" % coll_id)
        return coll_id

    def create_agent_workorder(self, task_name, task_parameters={},
                               identity=None, identity_account=None,
                               access_item=None, server_pk_subset=[],
                               trigger_platform_collection=True):
        """Creates a new workorder for agents."""
        logger.debug("Creating agent workorder (%s)" % (task_name))
        if self.interface is None:
            raise Exception("Platform(%s) interface is None" % self)
        workorder, created = ViAgentWorkOrder.objects.get_or_create(
            api_call=task_name,
            queue=self.interface.agent.queue_name,
            celery_task=self.interface.task_signature,
            pooling_time=settings.AGENT_TASK_POOL_TIME,
            complete=False, server_pk_subset=server_pk_subset,
            access_item=access_item, platform=self,
            trigger_platform_collection=trigger_platform_collection,
            identity=identity, identity_account=identity_account,
            task_parameters=task_parameters)
        if created:
            logger.info("Created new workorder: %s" % workorder)
        else:
            logger.warning("Ignoring duplicated workorder: %s" % workorder)
        return workorder

    def request_collection(self):
        # Check for pending collections first
        pending_collections = ViAgentWorkOrder.objects.filter(
            api_call='collect_platform', platform=self,
            complete=False)
        if pending_collections.exists():
            logger.debug("Skipping extra collection")
            return
        logger.debug("Preparing Collection: %s" % self)
        coll_sigs, coll_wo = self._collection_wo_sig_chain()
        return coll_wo

    def _collection_wo_sig_chain(self):
        # Collection work on agents
        coll_id = self.get_collection_id()
        coll_wo = self.create_agent_workorder(
            'collect_platform',
            trigger_platform_collection=False,
            task_parameters={
                "collection_id": coll_id
            }
        )
        return None, coll_wo

    def create_default_collection_task(self):
        crontab_schedule, _ = CrontabSchedule.objects.get_or_create(
            minute='0', hour='*',
            day_of_week='*', day_of_month='*', month_of_year='*')
        self.collection_task, _created = \
            PeriodicTask.objects.get_or_create(
                name='Platform %s(%s) Collection' % (
                    self.pk, self.title),
                task=self.collection_task_sig,
                crontab=crontab_schedule, args=[self.pk])


@receiver(post_save, sender=ViPlatform)
def create_schedules(sender, instance, created, **kwargs):
    # Todo: This is very lazy
    cache.clear()
    if not created:
        return
    if instance.collection_task is None:
        instance.create_default_collection_task()
        instance.save()
