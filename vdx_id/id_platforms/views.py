import json
import logging

from rest_framework.renderers import JSONRenderer
from rest_framework import generics

from .models import ViPlatform
from .serializers import (
    ViPlatformSerializer, ViPlatformSerializerDetail
)
import django_filters
from vdx_id.api_renderers import VdxIdApiRenderer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.http import JsonResponse
from vdx_id.permissions import IsAdminOrOwner
from id_work_agent.serializers import ViAgentWorkOrderSerializerDetail
from id_servers.models import ViPlatformServer

logger = logging.getLogger("%s" % __name__)


class PlatformViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = ViPlatform.objects.all()
    serializer_class = ViPlatformSerializer
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    def retrieve(self, request, pk=None):
        logger.info("Showing platform page")
        queryset = ViPlatform.objects.all()
        platform = get_object_or_404(queryset, pk=pk)
        serializer = ViPlatformSerializerDetail(platform)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=[IsAdminOrOwner])
    def collect(self, request, pk=None):
        """Request a collection of the platform. Returns a WO for the collection.
        If a collection is already in progress, that WO is returned instead."""
        platform = ViPlatform.objects.get(id=int(pk))
        logger.info("Requesting collection for %s" % platform)
    
        workorder = platform.request_collection()
        if workorder is None:
            logger.info("Collection already in progress, retrieving WO")
            workorder = platform.agent_work_orders.get(
                api_call="collect_platform", complete=False)
        
        wo_serializer = ViAgentWorkOrderSerializerDetail(workorder)
        return Response(wo_serializer.data)

    @action(methods=['post'], detail=True, permission_classes=[IsAdminOrOwner])
    def attach_servers(self, request, pk=None):
        """Submit an array of server pks to be assigned to this platform."""
        server_pks = request.data.get("server_pks")
        logger.info("Attaching Servers %s to platform_pk=%s" % (server_pks, pk))
        server_pks = [int(spk) for spk in server_pks]
        res = ViPlatformServer.objects.filter(
            pk__in=server_pks).update(
                platform=pk)
        return JsonResponse({'success': "%s" % res})
