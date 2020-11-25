import logging

from rest_framework import serializers
from .models import VdxIdentity

logger = logging.getLogger("vdx_id.%s" % __name__)


class VdxIdentitySerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = VdxIdentity
        fields = ('pk', 'url',
                  'unique_identifier')


class VdxIdentitySerializerDetail(VdxIdentitySerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = VdxIdentity
        fields = ('pk', 'url')
