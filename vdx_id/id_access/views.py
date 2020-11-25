import logging

import django_filters
from rest_framework.renderers import JSONRenderer
from rest_framework import generics

from .models import (
    ViAccessItem, ViAccessGroup,
    AccessItemMembership, AccessGroupMembership)
from .access_request import ViAccessItemRequest
from .group_request import ViAccessGroupRequest
from .serializers import (
    ViAccessItemSerializer, ViAccessItemSerializerDetail,
    ViAccessGroupSerializer, ViAccessGroupSerializerDetail,
    ViAccessGroupMembershipSerializer,
    ViAccessRequestSerializer, ViAccessRequestSerializerDetail,
    ViAccessGroupRequestSerializer, ViAccessGroupRequestSerializerDetail)
from vdx_id.api_renderers import VdxIdApiRenderer
# from django_datatables_view.base_datatable_view import BaseDatatableView

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from vdx_id.user_permissions import IsOwnIdentityOrAdmin
logger = logging.getLogger("%s" % __name__)


class ViAccessItemList(generics.ListAPIView):
    serializer_class = ViAccessItemSerializer
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    queryset = ViAccessItem.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    pagination_class = None


class ViAccessItemDetail(generics.RetrieveAPIView):
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    serializer_class = ViAccessItemSerializerDetail
    queryset = ViAccessItem.objects.all()


class ViAccessGroupList(generics.ListAPIView):
    queryset = ViAccessGroup.objects.all()
    serializer_class = ViAccessGroupSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    pagination_class = None


class ViAccessGroupDetail(generics.RetrieveAPIView):
    queryset = ViAccessGroup.objects.all()
    serializer_class = ViAccessGroupSerializerDetail
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)


class ViAccessItemRequestList(generics.ListAPIView):
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    serializer_class = ViAccessRequestSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    queryset = ViAccessItemRequest.objects.all()
    filterset_fields = ['identity', 'access_item', 'processing']
    pagination_class = None


class ViAccessItemRequestDetail(generics.RetrieveAPIView):
    queryset = ViAccessItemRequest.objects.all()
    serializer_class = ViAccessRequestSerializerDetail
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)


class ViAccessGroupRequestList(generics.ListCreateAPIView):
    """AccessGroup Requests are working objects of the Identity System.
    A user can create a group request specifying an identity and group.
    The system will then begin to request and provision access accordingly.

    AccessItemRequests are generated by AccessGroupRequests"""
    queryset = ViAccessGroupRequest.objects.all()
    serializer_class = ViAccessGroupRequestSerializer
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    pagination_class = None
    permission_classes = (IsOwnIdentityOrAdmin,)
    filterset_fields = ['identity', 'access_group', 'processing']
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class ViAccessGroupRequestDetail(generics.RetrieveAPIView):
    queryset = ViAccessGroupRequest.objects.all()
    serializer_class = ViAccessGroupRequestSerializerDetail
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)


class ViAccessGroupMembershipList(generics.ListAPIView):
    queryset = AccessGroupMembership.objects.all()
    serializer_class = ViAccessGroupMembershipSerializer
    renderer_classes = (JSONRenderer, VdxIdApiRenderer,)
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['identity', 'access_group']
    pagination_class = None


@login_required
@require_http_methods(["POST"])
def approve_request(request, pk):
    note = request.POST.get('note', 'N/A')
    access_req = ViAccessGroupRequest.objects.get(pk=pk)
    access_req.auth_approve(by=request.user, note=note)
    logger.info("Access Request: %s" % access_req)
    access_req.save()
    return JsonResponse(access_req.authorization_state)

@login_required
@require_http_methods(["POST"])
def reject_request(request, pk):
    note = request.POST.get('note', 'N/A')
    access_req = ViAccessGroupRequest.objects.get(pk=pk)
    access_req.auth_reject(by=request.user, note=note)
    logger.info("Access Request: %s" % access_req)
    access_req.save()
    return JsonResponse(access_req.authorization_state)
