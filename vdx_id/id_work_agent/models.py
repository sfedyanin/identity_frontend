import logging
from datetime import datetime
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from django_fsm import FSMField

from id_accounts.models import ViAccount

from django.db.models.signals import pre_save
import web_interface.tasks as web_tasks
from web_interface.sockets import send_map_update as socket_map_update
from vdx_id.util import arg_search

logger = logging.getLogger('vdx_id.%s' % __name__)


class ViAgent(models.Model):
    active = FSMField(default=False)

    # Metadata
    agent_name = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=40)
    heartbeat_time = models.DateTimeField(blank=True, null=True)
    health_state = models.IntegerField(default=-1)
    queue_name_override = models.CharField(
        max_length=80, blank=True, null=True)
    
    location = JSONField(default=list)

    @property
    def map_location(self):
        if self.location == []:
            self.location = [5.5697225, 51.441642]
            self.save(update_fields=['location'])
        return self.location

    @property
    def queue_name(self):
        if self.queue_name_override:
            return self.queue_name_override
        else:
            return self.agent_name

    def get_absolute_url(self):
        return "%i/" % self.pk

    def update_platform_interfaces_api(self, api_json):
        """Create/Update the APIs of available agent platform interfaces"""
        for platform_interface, api in api_json.items():
            agent_pif, _created = ViAgentPlatformInterface.objects.\
                get_or_create(
                    interface_name=platform_interface, agent=self
                )
            agent_pif.api = api
            agent_pif.task_signature = api['CONNECTION']['signature']
            agent_pif.save()
            agent_pif.create_templates()

    def __str__(self):
        return '%s (Active:%s)' % (self.agent_name, self.active)


class ViAgentPlatformInterface(models.Model):
    interface_name = models.CharField(max_length=255)
    last_update = models.DateTimeField('last_updated', auto_now=True)
    api = JSONField(default=dict, blank=True)
    task_signature = models.CharField(max_length=255, null=True)

    complete_api_interfaces = [
        "collect_platform", "set_password",
        "create_account", "update_account", "delete_account",
        "create_access_item", "delete_access_item", "update_access_item",
        "add_membership", "remove_membership"
    ]

    agent = models.ForeignKey(
        ViAgent,
        on_delete=models.CASCADE,
        related_name='interfaces'
    )

    @property
    def api_signature(self):
        if self.task_signature:
            return self.task_signature
        else:
            raise Exception("Task Signature undefined - any agent heartbeat?")

    def __str__(self):
        return '[%s] %s' % (self.agent.agent_name, self.interface_name)

    def get_absolute_url(self):
        return "%i/" % self.pk

    def get_apicall_args_kwargs(self, api_command):
        required_task_args = self.api[api_command]['required']
        optional_task_args = self.api[api_command]['optional']
        required_connection_args = self.api['CONNECTION']['required']
        optional_connection_args = self.api['CONNECTION']['optional']
        args = required_task_args + required_connection_args
        kwargs = optional_task_args + optional_connection_args
        return args, kwargs

    def create_templates(self):
        # Creates object templates for each type of template
        template_sets = [
            ('account', ViAccountTemplate,)
            # ('access_item', ViAccessItemTemplate)
        ]
        for template_key, template_cls in template_sets:
            templates = self.api['TEMPLATES'].get(template_key)
            for template in templates:
                template_name = template['name']
                template_obj, created = template_cls.objects.update_or_create(
                    interface=self,
                    name=template_name,
                    defaults=template
                )
                if created:
                    logger.info("Created new template: %s" % template_obj)
                else:
                    logger.info("Updated template: %s" % template_obj)
                

class ViInterfaceObjectTemplate(models.Model):
    """A template to be used when creating a new account or access item.
    Each platform can specify a default account/item template"""
    name = models.CharField(max_length=120)
    identifier = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")

    properties = JSONField(default=dict)
    propogate_params_to_identity = JSONField(
        default=list, blank=True,
        help_text="Use this field to specify parameters that should "
        "be propogated to the owning identity.")
    
    interface = models.ForeignKey(
        ViAgentPlatformInterface,
        on_delete=models.PROTECT,
        related_name='templates')

    class Meta:
        verbose_name = 'Access Object Template'
        abstract = True

    def get_or_create_object(self, obj_class, platform, *param_src_objects):
        properties = self.properties.copy()
        prop_params = self.propogate_params_to_identity

        # Modify the properties using identity values
        arg_search.fulfil_args_from_objects(
            properties, param_src_objects + (platform,))
        # And ensure something changed
        if properties == self.properties:
            raise Exception(
                "Template parameters were not modified by passed objects")

        instance_identifier = self.identifier.format(**properties)
        obj_inst, created = obj_class.objects.get_or_create(
            platform=platform, identifier=instance_identifier,
        )
        obj_inst.properties = properties
        return obj_inst, created


class ViAccountTemplate(ViInterfaceObjectTemplate):
    
    def __str__(self):
        return "%s - %s" % (self.name, self.interface)

    def get_or_create_account(self, platform, identity):
        account, created = self.get_or_create_object(
            ViAccount, platform, identity)
        if created:
            logger.info("Created new account: %s" % account)
            account.identity = identity
            account.propogate_params_to_identity = \
                self.propogate_params_to_identity
            account.save()
        else:
            logger.info("Identified existing account: %s" % account)
        
        return account, created


class ViAgentWorkOrder(models.Model):
    """The model for Agent WorkOrders.
    If a new workorder is submitted, and the task_id is specified,
    any pending api_call matching that task_id is revoked.
    Any workorders associated to such a task will reference the
    new workorder through the deferred_to field.
    """
    name = models.CharField(max_length=128, default="Agent API call")
    api_call = models.CharField(max_length=255)
    celery_task = models.CharField(max_length=255)
    queue = models.CharField(max_length=128, default='platform')

    # Todo: Make these logged FSM protected fields
    all_tasks_successful = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)
    active = models.BooleanField(default=False)

    # Used to store additional Kwargs for task
    task_parameters = JSONField(default=dict, blank=True)
    pooling_time = models.IntegerField(default=5)

    trigger_platform_collection = models.BooleanField(
        default=False,
        help_text="Perform a platform collection on complete "
            "if no other platform tasks pending")
    
    # Used to store the tasks sent through to ext agents
    #   agent_workorders = {
    #     host: {
    #       task_id: xxx, status: xxx, complete: bool
    #     }, host..
    #   }]
    agent_workorders = JSONField(default=dict, blank=True)
    exception = models.TextField(null=True, blank=True)

    # Optional fields to track relations to other entities
    identity = models.ForeignKey(
        'id_identities.VdxIdentity',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='agent_work_orders')
    identity_account = models.ForeignKey(
        'id_accounts.ViAccount',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='agent_work_orders')
    access_item = models.ForeignKey(
        'id_access.ViAccessItem',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='agent_work_orders')
    platform = models.ForeignKey(
        'id_platforms.ViPlatform',
        on_delete=models.SET_NULL, null=True,
        related_name='agent_work_orders')

    server_pk_subset = JSONField(default=list, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    complete_time = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        unique_together = (
            # Unique with complete_time so completed workorders dont compete
            'task_parameters', 'complete', 'complete_time',
            'name', 'api_call', 'celery_task',
            'queue', 'platform', 'identity')

    def __str__(self):
        return "%s: Active(%s) Complete(%s)" % (
            self.api_call, self.active, self.complete)

    @property
    def text(self):
        if self.api_call and len(self.api_call) > 0:
            return self.api_call
        elif self.name and len(self.name) > 0:
            return self.name
        else:
            return self.celery_task

    @property
    def pool_time_elapsed(self):
        if self.pooling_time == 0:
            return True
        else:
            time_sec = (timezone.now() - self.modified).seconds
            return time_sec > self.pooling_time

    @property
    def tasks_complete(self):
        # Todo: Optimize this
        workorders = self.agent_workorders
        for task_data in workorders.values():
            if not task_data.get('ready', False):
                return False
        return True

    @property
    def tasks_successful(self):
        # Todo: Optimize this
        workorders = self.agent_workorders
        for task_data in workorders.values():
            if not task_data.get('successful', False):
                return False
        return True

    def get_absolute_url(self):
        return "%i/" % self.pk

    def send_notification(self):
        msg = "Created (%s)" % self.text
        style = "wo-created"
        if self.active:
            msg = "Processing (%s)" % self.text
            style = "wo-processing"
        if self.complete:
            msg = "Complete (%s)" % self.text
            style = "wo-complete"
        try:
            web_tasks.send_notification_task(
                text=msg, style=style)
        except Exception:
            logger.exception("Error sending notification")

    def generate_map_flows(self):
        from id_servers.models import ViPlatformServer
        map_flow = []
        if self.platform:
            map_flow.append({
            "from": settings.MAPPING_PLATFORM_LOC,
            "to": self.platform.interface.agent.map_location,
            "labels":[
                "VDX Identify",
                "%s" % self.platform.interface.agent.agent_name],
            "color":"#4076e3",
            "value": 1
        })
        if self.active:
            servers = []
            if self.server_pk_subset:
                servers = ViPlatformServer.objects.filter(
                    pk__in=list(self.server_pk_subset), active=True)
            elif self.platform:
                servers = self.platform.servers.filter(active=True)
                    
            map_flow = []
            for server in servers:
                map_flow.append({
                    "from": self.platform.interface.agent.map_location,
                    "to": server.map_location,
                    "labels":[
                        self.platform.interface.agent.agent_name,
                        "%s" % server
                    ],
                    "color":"#3a3aA1",
                    "value": 1
                })
                map_flow.append({
                    "to": self.platform.interface.agent.map_location,
                    "from": server.map_location,
                    "labels":[
                        "%s" % server,
                        self.platform.interface.agent.agent_name,
                    ],
                    "color":"#40e3b2",
                    "value": 1
                })
        if self.complete:
            if self.platform:
                map_flow = [{
                    "from": self.platform.interface.agent.map_location,
                    "to": settings.MAPPING_PLATFORM_LOC,
                    "labels":[
                        self.platform.interface.agent.agent_name,
                        "VDX Identify"
                    ],
                    "color":"#36c943",
                    "value": len(self.server_pk_subset)
                }]
        logger.debug("Sending updated map flows: %s" % map_flow)
        return map_flow


@receiver(pre_save, sender=ViAgentWorkOrder)
def send_workorder_notification(sender, instance, **kwargs):
    """Sends a dumb notification to the platform"""
    logger.debug("Sending a group message! : %s" % instance)
    if instance.complete and instance.complete_time is None:
        instance.complete_time = datetime.now()
    # Send a simple notification about status
    socket_map_update({instance.pk: instance.generate_map_flows()})
    instance.send_notification()
