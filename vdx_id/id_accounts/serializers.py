import logging

from rest_framework import serializers
from .models import ViAccount

logger = logging.getLogger("vdx_id.%s" % __name__)


class ViAccountSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = ViAccount
        fields = ('url', 'identifier')


class ViAccountSerializerDetail(ViAccountSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = ViAccount
        fields = (
            'pk', 'url', 'identifier')
