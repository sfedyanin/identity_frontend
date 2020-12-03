import logging

from rest_framework import serializers
from django_fsm_log.models import StateLog

from .models import ViAccessItem, ViAccessGroup, AccessGroupMembership
from .access_request import ViAccessItemRequest
from .group_request import ViAccessGroupRequest, Access_groupState

from id_platforms.models import ViPlatform
from id_identities.models import VdxIdentity

logger = logging.getLogger("vdx_id.%s" % __name__)


class ViAccessItemSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    platform = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field='title')

    class Meta:
        model = ViAccessItem
        fields = ('pk', 'url', 'identifier', 'platform')
        read_only_fields = ('identifier', 'platform')


class ViAccessItemSerializerDetail(ViAccessItemSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = ViAccessItem
        fields = (
            'pk', 'url', 'identifier', 'platform',
            'members')
        read_only_fields = ('identifier', 'platform', 'members')


class ViAccessGroupSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    access_items = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='identifier')
    access_groups = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='identifier')
    platform = serializers.SlugRelatedField(
        queryset=ViPlatform.objects.all(),
        many=False, read_only=False, slug_field='title')

    class Meta:
        model = ViAccessGroup
        fields = ('pk', 'url', 'identifier', 'description', 'owners',
                'access_groups', 'access_items', 'platform')


class ViAccessGroupSerializerDetail(ViAccessGroupSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    access_items = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='identifier')
    access_groups = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='identifier')
    
    # Todo: These fields are heavy, and mainly for demo; remove
    all_access = serializers.SerializerMethodField()

    def get_all_access(self, grp):
        # Hacked for frontend
        access_set = {
            "groups": {
                g.identifier: self._get_grp_access(g)
                for g in grp.access_groups.all()},
            "platform_access_set": {
                grp.platform.title: {
                    'items': grp.access_items.values_list(
                        'identifier', flat=True),
                    'servers': grp.platform.servers.values_list(
                        "fqdn", flat=True)
                }
            }
        }
        access_set['groups'][grp.identifier] = self._get_grp_access(grp)
        return access_set

    def _get_grp_access(self, grp):
        return {
            "direct_item_count": grp.access_items.count(),
            "rules": []
        }

    class Meta:
        model = ViAccessGroup
        fields = (
            'pk', 'url', 'identifier', 'description', 'owners',
            'access_groups', 'access_items', 'platform', 'all_access',
            'available', 'membership_autoexpiry' )


class StateLogSerializer(serializers.ModelSerializer):
    by = serializers.SerializerMethodField()
    
    def get_by(self, obj):
        if hasattr(obj.by, 'associated_identity'):
            return obj.by.associated_identity.unique_identifier
        else:
            return None

    class Meta:
        model = StateLog
        fields = ('timestamp', 'by',
            'source_state', 'state', 'transition')


class ViAccessRequestSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    platform = serializers.SlugRelatedField(
        queryset=ViPlatform.objects.all(),
        many=False, read_only=False, slug_field='title')
    identity = serializers.SlugRelatedField(
        queryset=VdxIdentity.objects.all(),
        many=False, read_only=False, slug_field='unique_identifier')
    access_item = serializers.SlugRelatedField(
        queryset=ViAccessItem.objects.all(),
        many=False, read_only=False, slug_field='identifier')

    class Meta:
        model = ViAccessItemRequest
        fields = ('pk', 'url',
                  'identity', 'platform', 'access_item',
                  'state', 'target_state',
                  'processing')


class ViAccessRequestSerializerDetail(ViAccessGroupSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    state_log = serializers.SerializerMethodField()

    identity = serializers.SlugRelatedField(
        queryset=VdxIdentity.objects.all(),
        many=False, read_only=False, slug_field='unique_identifier')
    access_item = serializers.SlugRelatedField(
        queryset=ViAccessItem.objects.all(),
        many=False, read_only=False, slug_field='identifier')

    def get_state_log(self, obj):
        state_logs = StateLog.objects.for_(obj).order_by('-timestamp')
        state_log_data = StateLogSerializer(state_logs, many=True).data
        return state_log_data

    class Meta:
        model = ViAccessItemRequest
        fields = (
            'pk', 'url',
            'identity', 'platform', 'account', 'access_item',
            'state', 'target_state', 'state_log',
            'processing')


class ViAccessGroupRequestSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    identity = serializers.SlugRelatedField(
        queryset=VdxIdentity.objects.all(),
        many=False, read_only=False, slug_field='unique_identifier')
    access_group = serializers.SlugRelatedField(
        queryset=ViAccessGroup.objects.all(),
        many=False, read_only=False, slug_field='identifier')

    class Meta:
        model = ViAccessGroupRequest
        fields = ('pk', 'url',
                  'identity', 'access_group', 'access_duration',
                  'state', 'target_state', 'processing')
        read_only_fields = ('state', 'processing')

    def create(self, validated_data):
        logger.info("Creating request with vDat: %s" % validated_data)
        updated_value_dict = {
            'target_state': validated_data.get(
                'target_state', Access_groupState.ACCESS_GROUP_MEMBER)
        }
        request, created = ViAccessGroupRequest.objects.update_or_create(
            identity=validated_data.get('identity', None),
            access_group=validated_data.get('access_group', None),
            defaults=updated_value_dict)
        if updated_value_dict['target_state'] == "member":
            request.reinitialize_state()
            request.save()

        return request


class ViAccessGroupRequestSerializerDetail(ViAccessGroupSerializer):
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    state_log = serializers.SerializerMethodField()

    identity = serializers.SlugRelatedField(
        queryset=VdxIdentity.objects.all(),
        many=False, read_only=False, slug_field='unique_identifier')
    access_group = serializers.SlugRelatedField(
        queryset=ViAccessGroup.objects.all(),
        many=False, read_only=False, slug_field='identifier')

    def get_state_log(self, obj):
        state_logs = StateLog.objects.for_(obj).order_by('-timestamp')
        logger.info("Retrieved state logs: %s" % state_logs)
        state_log_data = StateLogSerializer(state_logs, many=True).data
        logger.info("Serialized state logs: %s" % state_log_data)
        return state_log_data

    class Meta:
        model = ViAccessGroupRequest
        fields = (
            'pk', 'url', 'identity', 'access_group', 'state_log',
            'state', 'target_state', 'processing')


class ViAccessGroupMembershipSerializer(serializers.ModelSerializer):
    identity = serializers.SlugRelatedField(
        queryset=VdxIdentity.objects.all(),
        many=False, read_only=False, slug_field='unique_identifier')
    access_group = serializers.SlugRelatedField(
        queryset=ViAccessGroup.objects.all(),
        many=False, read_only=False, slug_field='identifier')

    class Meta:
        model = AccessGroupMembership
        fields = ('access_group', 'identity',
            'date_created', 'last_updated', 'membership_expiry')