
import logging

from rest_framework.renderers import JSONRenderer
from rest_framework import generics

from .models import ViAccount
from .serializers import (
    ViAccountSerializer, ViAccountSerializerDetail
)
import django_filters
from vdx_id.api_renderers import VdxIdApiRenderer

logger = logging.getLogger("%s" % __name__)


class ViAccountList(generics.ListAPIView):
    serializer_class = ViAccountSerializer
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    queryset = ViAccount.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class ViAccountDetail(generics.RetrieveAPIView):
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    serializer_class = ViAccountSerializerDetail
    queryset = ViAccount.objects.all()
