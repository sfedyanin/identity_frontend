import logging

from rest_framework.renderers import JSONRenderer
from rest_framework import generics

from .models import VdxIdentity
from .serializers import (
    VdxIdentitySerializer, VdxIdentitySerializerDetail,
)
from vdx_id.api_renderers import VdxIdApiRenderer

logger = logging.getLogger("%s" % __name__)


class VdxIdentityList(generics.ListAPIView):
    serializer_class = VdxIdentitySerializer
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    queryset = VdxIdentity.objects.all()


class VdxIdentityDetail(generics.RetrieveAPIView):
    queryset = VdxIdentity.objects.all()
    serializer_class = VdxIdentitySerializerDetail
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
