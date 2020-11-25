import logging

from django.db import models
from django.contrib.postgres.fields import JSONField

logger = logging.getLogger('vdx_id.%s' % __name__)


class VdxIdentity(models.Model):
    properties = JSONField(default=dict, blank=True)
    unique_identifier = models.CharField(
        'Unique identifier for this identity',
        blank=False, max_length=80, unique=True)

    access_synchronized = models.BooleanField(default=True)

    def __str__(self):
        return "Id: %s" % self.unique_identifier

    @property
    def code(self):
        return "id_%s" % self.pk

    def get_absolute_url(self):
        return "%i/" % self.pk

    class Meta:
        permissions = (
            ("identity_admin", "User can alter all VdxIdentity objects"),
        )
