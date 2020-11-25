import logging

from rest_framework.renderers import JSONRenderer
from rest_framework import generics

from .models import (
    ViAgent, ViAgentPlatformInterface, ViAgentWorkOrder)
from .serializers import (
    ViAgentSerializer, ViAgentSerializerDetail,
    ViAgentInterfaceSerializer, ViAgentInterfaceSerializerDetail,
    ViAgentWorkOrderSerializer, ViAgentWorkOrderSerializerDetail
)
import django_filters
from vdx_id.api_renderers import VdxIdApiRenderer

logger = logging.getLogger("%s" % __name__)


class ViAgentList(generics.ListAPIView):
    serializer_class = ViAgentSerializer
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    queryset = ViAgent.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class ViAgentDetail(generics.RetrieveAPIView):
    serializer_class = ViAgentSerializerDetail
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    queryset = ViAgent.objects.all()


class ViAgentWorkOrderList(generics.ListAPIView):
    serializer_class = ViAgentWorkOrderSerializer
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    queryset = ViAgentWorkOrder.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class ViAgentWorkOrderDetail(generics.RetrieveAPIView):
    serializer_class = ViAgentWorkOrderSerializerDetail
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    queryset = ViAgentWorkOrder.objects.all()


class ViAgentPlatformInterfaceList(generics.ListAPIView):
    serializer_class = ViAgentInterfaceSerializer
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    queryset = ViAgentPlatformInterface.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class ViAgentPlatformInterfaceDetail(generics.RetrieveAPIView):
    serializer_class = ViAgentInterfaceSerializerDetail
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    queryset = ViAgentPlatformInterface.objects.all()
