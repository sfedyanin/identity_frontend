import logging

from rest_framework import serializers
from .models import ViPlatformServer, ViServerGroup

logger = logging.getLogger("vdx_id.%s" % __name__)


class ViServerSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    server_name = serializers.SerializerMethodField()
    created = serializers.DateTimeField()
    last_seen = serializers.DateTimeField(source='modified')

    def get_server_name(self, obj):
        return obj.__str__()

    class Meta:
        model = ViPlatformServer
        fields = ('url', 'fqdn', 'server_name', 'created', 'last_seen')


class ViServerSerializerDetail(ViServerSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = ViPlatformServer
        fields = ('pk', 'url', 'created', 'modified', 'fqdn')


class ViServerGroupSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    server_count = serializers.SerializerMethodField()

    def get_server_count(self, obj):
        return obj.servers.count()

    class Meta:
        model = ViServerGroup
        fields = ('pk', 'url', 'title', 'description', 'server_count')


class ViServerGroupSerializerDetail(ViServerGroupSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    servers = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='fqdn')
    scan_definition = serializers.JSONField(binary=True)

    class Meta:
        model = ViServerGroup
        fields = ('pk', 'url', 'title', 'description',
            'servers', 'scan_definition', 'scan_interval', 'server_retire_time')
