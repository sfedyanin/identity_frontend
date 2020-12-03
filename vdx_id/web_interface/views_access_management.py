import json
import logging
import networkx as nx

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from bokeh.models import (BoxZoomTool, Circle, HoverTool,
                          MultiLine, Plot, Range1d, ResetTool,)
from bokeh.palettes import Spectral4
from bokeh.models.graphs import from_networkx
from bokeh.resources import CDN
from bokeh.embed import components

# from id_access.access_network import AccessNetwork
from id_access.models import ViAccessGroup, AccessGroupMembership
from id_access.group_request import ViAccessGroupRequest
from id_platforms.models import ViPlatform
from id_work_agent.models import ViAgentWorkOrder
from id_servers.models import ViServerGroup

logger = logging.getLogger('vdx_id.%s' % __name__)


######################
# Auth test decorator
######################

@login_required
def home(request):
    if request.session.get('new_visit') is None:
        request.session['new_visit'] = True
    elif request.session['new_visit']:
        request.session['new_visit'] = False

    identity = None
    if request.user.associated_identity:
        identity = request.user.associated_identity

    context = {
        "identity": identity,
    }
    return render(request, 'access_management/home.html', context)


##################
# Web UI Views
# Consider:
#   https://channels.readthedocs.io/en/latest/topixcs/sessions.html#session-persistence
#   https://sweetalert2.github.io/#examples
#   https://themeforest.net/tags/bootstrap
#   http://bl.ocks.org/Andrew-Reid/35d89fbcfbcfe9e819908ea77fc5bef6
##################

@login_required
@require_http_methods(["GET"])
def view_access(request):
    identity = None
    if request.user.associated_identity:
        identity = request.user.associated_identity.unique_identifier

    context = {
        'identity': identity,
        'referred_id': request.GET.get("identifier"),
        'member': False
    }
    # Populate account metrics
    return render(request, 'access_management/view_access.html',
                    context=context)


@login_required
@require_http_methods(["GET"])
def view_platforms(request, platform_id):
    context = {}
    platforms = ViPlatform.objects.all()
    context['platforms'] = platforms

    if platform_id:
        selected_platform = platforms.filter(id=platform_id).first()
        context['selected_platform'] = selected_platform
        sel_plat_wo = selected_platform.agent_work_orders
        coll_wo = sel_plat_wo.filter(
            api_call="collect_platform", complete=True)
        context['selected_platform_collection'] = None
        if coll_wo:
            context['selected_platform_collection'] = coll_wo.latest(
                'complete_time')

        context['sel_plat_wo'] = {
            "active": sel_plat_wo.filter(active=True),
            "pending": sel_plat_wo.filter(complete=False, active=False)
        }
    # Populate account metrics
    return render(request, 'access_management/view_platforms.html',
                  context=context)


@login_required
@require_http_methods(["GET"])
def view_servers(request, sgroup_id):
    context = {}
    server_groups = ViServerGroup.objects.all()
    context['server_groups'] = server_groups

    if sgroup_id:
        selected_group = server_groups.filter(id=sgroup_id).first()
        context['selected_group'] = selected_group
        context['selected_scan_definition'] = json.dumps(
            selected_group.scan_definition, indent=4)
        context['server_platforms'] = ViPlatform.objects.all()
        
    # Populate account metrics
    return render(request, 'access_management/view_servers.html',
                  context=context)



@login_required
@require_http_methods(["GET"])
def my_access(request):
    identity = None
    if request.user.associated_identity:
        identity = request.user.associated_identity
    # Todo: Optimize the below queries
    context = {
        'identity': identity,
        'group_req': {
            'processed': identity.access_group_requests.filter(processing=False).count(),
            'processing': identity.access_group_requests.filter(processing=True).count()
        },
        'item_req': {
            'processed': identity.access_item_requests.filter(processing=False).count(),
            'processing': identity.access_item_requests.filter(processing=True).count()
        }
    }
    # Populate account metrics
    return render(request, 'access_management/my_access.html',
                  context=context)


@login_required
@require_http_methods(["GET"])
def access_approvals(request):
    identity = None
    if request.user.associated_identity:
        identity = request.user.associated_identity
    # Todo: Optimize the below queries
    context = {
        'identity': identity,
        'pending_auth_access_requests': identity.auth_attention.filter(
            processing=True).prefetch_related('access_group')
    }
    # Populate account metrics
    return render(request, 'access_management/approve_access.html',
                  context=context)


@login_required
@require_http_methods(["GET"])
def access_network(request):
    context = {
        "bok_script": "",
        "bok_div": ""}

    logger.debug("Context: %s" % context)
    # Populate account metrics
    return render(request, 'access_management/net_graph.html',
                  context=context)


@require_http_methods(["GET"])
def map_visual(request):
    dataset = {}
    work_orders = ViAgentWorkOrder.objects.filter(
        celery_task='unix.interface_action',
        complete=False
    ).order_by('-id')[:5].prefetch_related('platform')
    for wo in work_orders:
        if wo.platform:
            dataset[wo.pk] = wo.generate_map_flows()
    # Clean up excessive labelling (labels get stacked and become intense..)
    labels_seen = []
    for pk, flows in dataset.items():
        for flow in flows:
            for idx, l in enumerate(flow['labels']):
                if l in labels_seen:
                    flow['labels'][idx] = ''
                else:
                    labels_seen.append(l)
    return render(
        request, 'access_management/map_visual.html',
        context={"dataset": dataset}
    )


@require_http_methods(["GET"])
def report_builder(request):
    context = {"embed_url": "/report_builder"}
    # Populate account metrics
    return render(request, 'access_management/iframe_embed.html',
                  context=context)


@require_http_methods(["GET"])
def sql_explorer(request):
    context = {"embed_url": "/explorer"}
    # Populate account metrics
    return render(request, 'access_management/iframe_embed.html',
                  context=context)
