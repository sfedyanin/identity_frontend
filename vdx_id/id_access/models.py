import logging
import rules
import hashlib

from django.db import models
from django.dispatch import receiver
from django.db.models import signals as db_signal
from django_fsm import FSMField
from django.core.exceptions import ValidationError

from datetime import timedelta
from django.contrib.postgres.fields import JSONField
from id_identities.models import VdxIdentity

from id_access.group_change import ViAccessGroupChangeRequest

from rest_framework.reverse import reverse
import web_interface.tasks as web_tasks

logger = logging.getLogger('vdx_id.%s' % __name__)


# Todo: supercharge ORM: https://medium.com/kolonial-no-product-tech/pushing-the-orm-to-its-limits-d26d87a66d28

class ViAccessItem(models.Model):
    """A singular item of Access on a platform, for a platform account."""
    identifier = models.CharField(max_length=255)
    available = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    properties = JSONField(default=dict, blank=True)
    # display_name = models.CharField(max_length=120, blank=True, null=True)

    # Metadata
    description = models.TextField(
        blank=True, null=True)

    collection_data = JSONField(
        default=dict, blank=True)
    collection_data_variance = models.BooleanField(default=False)

    platform = models.ForeignKey(
        'id_platforms.ViPlatform',
        on_delete=models.PROTECT,
        related_name='access_items')

    members = models.ManyToManyField(
        'id_accounts.ViAccount',
        through='AccessItemMembership')

    parent_properties_ref = "platform"

    def __str__(self):
        return "%s" % (self.identifier)

    class Meta:
        ordering = ['identifier']
        unique_together = ('identifier', 'platform')

    @property
    def task_parameters(self):
        """Returns dicts for parameter resolving"""
        yield self.properties
        yield self.collection_data

    @property
    def unique_id(self):
        return "%s|%s" % (self.platform.pk, self.identifier)

    def get_absolute_url(self, obj, view_name, request, format):
        return reverse(
            'api:iam:id_access:item-detail', kwargs={'pk': self.pk})

    def has_member(self, account):
        return self.members.filter(
            id=account.id).exists()

    def get_accounts(self):
        accounts = AccessItemMembership.objects.filter(
            access=self).values_list(
            'account', flat=True).order_by('id')
        return accounts


class ViAccessGroup(models.Model):
    """
    Sets (inclusive and exclusive) of access and policies.
    The concept of a policy can be described by a Policy.
    Policies can be inherited without limit.

    Access can be added or removed from inherited policies.
    If an access is removed, inheriting policies are notified to
    trigger an equal-but-opposite change being created;
    This is done to maintain the equivalent policy access.

    Each policy can only include Access from a single platform.
    But policies can include/exclude policies from any platforms.

    Access is evaluated in the following order:
        1) Access(Inherited policies) added to access
        2) Access(Inherited_exclude policies) subtracted
        3) Access(included) added
        4) Access(excluded) removed
    """
    identifier = models.CharField(max_length=255)
    description = models.TextField(default="")
    available = models.BooleanField(
        default=True, help_text="Only available groups can be requested")

    owners = models.ManyToManyField(
        "id_identities.VdxIdentity", related_name='owned_access_groups')

    access_groups = models.ManyToManyField(
        "self", blank=True, symmetrical=False,
        related_name="inheriting_groups")
    access_items = models.ManyToManyField(
        ViAccessItem, blank=True, related_name="inheriting_groups")

    # This is required for Access Items only
    platform = models.ForeignKey(
        'id_platforms.ViPlatform',
        on_delete=models.SET_NULL, blank=True, null=True,
        related_name='associated_groups',
        help_text="The Platform associated to AccessItems if present")

    # access_rules = models.ManyToManyField(VdxAccessRule, blank=True)
    rule_list = JSONField(
        default=list, blank=True, help_text="List of rules to apply")

    members = models.ManyToManyField(
        'id_identities.VdxIdentity',
        through='AccessGroupMembership')
    membership_autoexpiry = models.DurationField(
        default=timedelta(days=30)
    )

    stored_access_state = JSONField(default=dict, blank=True)

    @property
    def access_state(self):
        return {
            "groups": list(self.access_groups.values_list('pk', flat=True)),
            "items": list(self.access_items.values_list('pk', flat=True))
        }

    def __str__(self):
        return self.identifier

    def has_member(self, identity):
        if identity:
            return self.members.filter(
                id=identity.id).exists()

    def get_meta_json(self):
        """Returns JSON metadata bout the group. Used for demo UI"""
        access_items = self.get_access_by_accgroup_id(self.identifier)
        platform_pks = list(set([int(acc.split("|")[0])
                            for acc in access_items]))
        # servers = ViServer.objects.filter(platform__pk__in=platform_pks)
        logger.info("Access Items: %s" % access_items)
        # logger.info("Access servers: %s" % servers)
        return {
            "total_access_items": ["%s" % x for x in access_items],
            "platform_pks": platform_pks}
    
    def clean(self):
        enabled_rules = list(rules.rulesets.default_rules.keys())
        for rule in self.rule_list:
            if rule not in enabled_rules:
                raise ValidationError(
                    "Rule(%s) not available in %s" % (rule, enabled_rules))


class AccessItemMembership(models.Model):
    """This model is used to represent the active membership of access"""
    access = models.ForeignKey(
        ViAccessItem,
        related_name='accessitem_memberships', on_delete=models.CASCADE)
    account = models.ForeignKey(
        'id_accounts.ViAccount', null=True,
        related_name='accessitem_memberships', on_delete=models.SET_NULL)

    embedded_access = models.BooleanField(
        default=False,
        help_text="True if access item is embedded to identity."
            " (e.g. default group for unix user)")

    date_created = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)


class AccessGroupMembership(models.Model):
    """This model is used to represent the active membership of access"""
    access_group = models.ForeignKey(
        ViAccessGroup,
        related_name='accessgroup_memberships', on_delete=models.CASCADE)
    identity = models.ForeignKey(
        'id_identities.VdxIdentity', null=True,
        related_name='accessgroup_memberships', on_delete=models.SET_NULL)

    date_created = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)

    membership_expiry = models.DateTimeField(null=True, blank=True)

    def get_absolute_url(self, obj, view_name, request, format):
        return reverse(
            'api:iam:id_access:group-detail', kwargs={'pk': self.access_group.pk})


# --------------------------
# Signals
# --------------------------
@receiver(db_signal.post_save, sender=AccessGroupMembership)
def outsync_postsave(sender, instance, **kwargs):
    logger.info("Post_save membership - marking identity out of sync (%s)" % instance)
    instance.identity.access_synchronized = False
    instance.identity.save(update_fields=['access_synchronized'])


@receiver(db_signal.pre_delete, sender=AccessGroupMembership)
def outsync_predelete(sender, instance, **kwargs):
    logger.info("Pre_delete membership - marking identity out of sync (%s)" % instance)
    instance.identity.access_synchronized = False
    instance.identity.save(update_fields=['access_synchronized'])

