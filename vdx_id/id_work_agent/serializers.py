import logging

from rest_framework import serializers
from .models import ViAgent, ViAgentPlatformInterface, ViAgentWorkOrder

logger = logging.getLogger("vdx_id.%s" % __name__)


class ViAgentSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = ViAgent
        fields = ('pk', 'url', 'agent_name', 'description', 'active')
        read_only_fields = ('active',)


class ViAgentSerializerDetail(ViAgentSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = ViAgent
        fields = (
            'pk', 'url', 'agent_name', 'description', 'active',
            'heartbeat_time', 'queue_name_override', 'technical_contacts')
        read_only_fields = ('identifier', 'platform', 'members')


class ViAgentInterfaceSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = ViAgentPlatformInterface
        fields = ('url', 'interface_name', 'last_update', 'agent')


class ViAgentInterfaceSerializerDetail(ViAgentInterfaceSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = ViAgentPlatformInterface
        fields = (
            'pk', 'url', 'interface_name', 'last_update', 'agent',
            'api')


class ViAgentWorkOrderSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    identity = serializers.SlugRelatedField(
        read_only=True, slug_field='unique_identifier')
    identity_account = serializers.SlugRelatedField(
        read_only=True, slug_field='identifier')
    access_item = serializers.SlugRelatedField(
        read_only=True, slug_field='identifier')
    platform = serializers.SlugRelatedField(
        read_only=True, slug_field='title')

    class Meta:
        model = ViAgentWorkOrder
        fields = ('url', 'name', 'api_call', 'complete', 'active',
                  'identity', 'identity_account', 'access_item', 'platform')


class ViAgentWorkOrderSerializerDetail(ViAgentWorkOrderSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    identity = serializers.SlugRelatedField(
        read_only=True, slug_field='unique_identifier')
    identity_account = serializers.SlugRelatedField(
        read_only=True, slug_field='identifier')
    access_item = serializers.SlugRelatedField(
        read_only=True, slug_field='identifier')
    platform = serializers.SlugRelatedField(
        read_only=True, slug_field='title')

    class Meta:
        model = ViAgentWorkOrder
        fields = (
            'pk', 'name', 'api_call', 'complete', 'active',
            'identity', 'identity_account', 'access_item', 'platform',
            'task_parameters', 'queue', 'agent_workorders')
