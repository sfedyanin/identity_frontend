import logging

from rest_framework.renderers import JSONRenderer
from rest_framework import generics
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

import django_filters
from django.shortcuts import get_object_or_404

from .models import ViPlatformServer, ViServerGroup
from .serializers import (
    ViServerSerializer, ViServerSerializerDetail,
    ViServerGroupSerializer, ViServerGroupSerializerDetail
)
from id_work_agent.serializers import ViAgentWorkOrderSerializerDetail

from vdx_id.api_renderers import VdxIdApiRenderer
from vdx_id.permissions import IsAdminOrOwner

logger = logging.getLogger("%s" % __name__)


class ViServerViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = ViPlatformServer.objects.all()
    serializer_class = ViServerSerializer
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    def retrieve(self, request, pk=None):
        queryset = ViPlatformServer.objects.all()
        platform = get_object_or_404(queryset, pk=pk)
        serializer = ViServerSerializerDetail(platform)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=[IsAdminOrOwner])
    def collection(self, request, pk=None):
        server = ViPlatformServer.objects.get(server_pk=int(pk))
        logger.info("Requesting server collection for %s" % server)
        return Response(server.collection_data)


class ViServerGroupViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = ViServerGroup.objects.all()
    serializer_class = ViServerGroupSerializer
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    def retrieve(self, request, pk=None):
        queryset = ViServerGroup.objects.all()
        platform = get_object_or_404(queryset, pk=pk)
        serializer = ViServerGroupSerializerDetail(platform)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, permission_classes=[IsAdminOrOwner])
    def scan(self, request, pk=None):
        server_group = ViServerGroup.objects.get(id=int(pk))
        logger.info("Requesting server group scan for %s" % server_group)
    
        cel_chain, workorder = server_group.perform_scan()       
        wo_serializer = ViAgentWorkOrderSerializerDetail(workorder)
        return Response(wo_serializer.data)
