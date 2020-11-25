import math
import celery
import logging
from django.db import models
from django.contrib.postgres.fields import JSONField
from id_work_agent.models import ViAgentWorkOrder, ViAgent
import web_interface.tasks as web_tasks
from django.db import transaction


logger = logging.getLogger('vdx_id.%s' % __name__)


class ViServerGroup(models.Model):
    """Group used to define many servers using network ranges or lists."""
    # Todo: Make this self-referential so that property-network can be
    # abused better
    title = models.CharField(max_length=255)
    description = models.TextField(default="")

    scan_definition = JSONField(
        default=dict,
        help_text="A JSON object: 'ports':[], 'ranges':[{},]")
    scan_results = JSONField(default=dict, blank=True)

    scan_interval = models.DurationField(
        help_text="Rescan this network group after this much time",
        default='30:00')
    server_retire_time = models.DurationField(
        help_text="Remove any server that has not been detected in this time",
        default='60:00')

    associated_agent = models.ForeignKey(
        ViAgent, related_name='server_groups',
        null=True, on_delete=models.SET_NULL)

    modified = models.DateTimeField(auto_now=True)
    location = JSONField(default=list)

    @property
    def map_location(self):
        if self.location == []:
            self.location = [5.4697225, 51.441642]
            self.save(update_fields=['location'])
        return self.location

    def __str__(self):
        if hasattr(self, "servers") and self.servers:
            return "%s [%s hosts - %s active]" % (
                self.title, self.servers.count(),
                self.servers.filter(active=True).count())
        else:
            return "%s [EMPTY]" % (self.title)

    def get_absolute_url(self):
        return "%i/" % self.pk

    def perform_scan(self):
        if self.associated_agent is None:
            raise Exception("No agent has been set for group")
        if not self.associated_agent.active:
            raise Exception("Agent %s is not active" % self.associated_agent)

        # Collection work on agents
        celtask_wo = self.create_netscan_workorder()
        celtask_chain = None
        logger.info("Called chain: %s" % celtask_chain)
        return celtask_chain, celtask_wo

    def create_netscan_workorder(self):
        """Creates a new workorder for agents."""

        agent_workorders = {}
        # Store a placeholder state in the workorder def
        # TODO: Don't hardcode this
        agent_workorders["network_scan_task"] = {
            "state": 'PENDING',
            "ready": False,
            "successful": False}

        # Create the WORKORDER and let it wait for complete
        workorder = ViAgentWorkOrder.objects.create(
            name="Network Scan",
            complete=False, active=True,
            agent_workorders=agent_workorders)

        logger.info("Created workorder: %s" % workorder)
        return workorder

    def update_servers(self):
        """This is called from tasks.read_netscan_result to parse self.scan_results
        The scan_result attribute is populated as the result is read."""
        # TODO: Optimize this to a JSONField query

        hosts_detected = 0

        for agent_id, agent_data in self.scan_results.items():
            logger.info("Reading scan from agent id: %s" % agent_id)
            for host, p_scan in agent_data.items():

                fully_connected = False not in [
                    result['connected']
                    for port, result in p_scan.items()]
                if fully_connected:
                    logger.debug("Host found: %s" % host)
                    hosts_detected += 1
                else:
                    logger.debug("Host not connected: %s" % host)
                    continue
                
                ports = list(p_scan.keys())
                server, created = ViPlatformServer.objects.update_or_create(
                    fqdn=host, server_group=self,
                    human_readable_name="Disc[%s] (P: %s)" % (host, ports),
                    defaults={'active': True})
                if created:
                    logger.info("Discovered new server: [%10s] %s" % (host, server))

        # Create a servergroup notification
        web_tasks.send_notification_task.delay(
            text="(%s) Scan complete [%s hosts]" % (
                self.title, hosts_detected),
            style="success", lane="platform")


class ViPlatformServer(models.Model):
    server_pk = models.AutoField(primary_key=True)
    fqdn = models.CharField(max_length=255)
    active = models.BooleanField(
        default=True,
        help_text="Servers detected within SrvGrp.server_retire_time")
    properties = JSONField(default=dict, blank=True)

    human_readable_name = models.CharField(
        max_length=256, blank=True, null=True)
    hostname = models.CharField(
        max_length=256, blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    server_group = models.ForeignKey(
        ViServerGroup, related_name='servers',
        null=True, on_delete=models.SET_NULL)
    platform = models.ForeignKey(
        'id_platforms.ViPlatform', on_delete=models.SET_NULL,
        related_name='servers', null=True, blank=True)

    collection_data = JSONField(default=dict, blank=True)
    location = JSONField(default=list, blank=True)

    @property
    def task_parameters(self):
        """Returns dicts for parameter resolving"""
        yield self.properties

    @property
    def map_location(self):
        if self.location == []:
            loc = self.server_group.map_location
            server_pks = sorted(list(
                self.server_group.servers.values_list('pk', flat=True)))
            circ_radius = float(len(server_pks)) / 150
            arc_seg = (math.pi * 2)/len(server_pks)
            loc[0] += circ_radius * math.sin(arc_seg * server_pks.index(self.pk))
            loc[1] += circ_radius * math.cos(arc_seg * server_pks.index(self.pk))
            self.location = loc
            self.save(update_fields=['location'])
        return self.location

    def get_absolute_url(self):
        return "%i/" % self.pk

    def __str__(self):
        return self.human_readable_name or self.hostname or self.fqdn
