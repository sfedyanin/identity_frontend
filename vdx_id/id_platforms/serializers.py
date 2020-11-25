import logging

from rest_framework import serializers
from .models import ViPlatform

logger = logging.getLogger("vdx_id.%s" % __name__)


class ViPlatformSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = ViPlatform
        fields = ('pk', 'url', 'title')
        read_only_fields = ()


class ViPlatformSerializerDetail(ViPlatformSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = ViPlatform
        fields = (
            'pk', 'url', 'title', 'description')
