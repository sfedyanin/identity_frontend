from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


######################
# Auth test decorator
######################
@login_required
def index(request):
    return render(request, 'administration/index.html', {})


##################
# Web UI Views
##################
def admin_view(request):
    context = {"embed_url": "/admin"}
    # Populate account metrics
    return render(request, 'administration/iframe_embed.html',
                  context=context)


@require_http_methods(["GET"])
def report_builder(request):
    context = {"embed_url": "/report_builder"}
    # Populate account metrics
    return render(request, 'administration/iframe_embed.html',
                  context=context)


@require_http_methods(["GET"])
def sql_explorer(request):
    context = {"embed_url": "/explorer"}
    # Populate account metrics
    return render(request, 'administration/iframe_embed.html',
                  context=context)
