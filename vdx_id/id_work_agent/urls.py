from django.urls import path
from . import views

app_name = 'id_agents'

urlpatterns = [
    path('agents/',
         views.ViAgentList.as_view(),
         name='agent-list'),
    path('agents/<int:pk>/',
         views.ViAgentDetail.as_view(),
         name='agent-detail'),
    path('agent_interfaces/',
         views.ViAgentPlatformInterfaceList.as_view(),
         name='agent_iface-list'),
    path('agent_interfaces/<int:pk>/',
         views.ViAgentPlatformInterfaceDetail.as_view(),
         name='agent_iface-detail'),
    path('work_orders/',
         views.ViAgentWorkOrderList.as_view(),
         name='agentwo-list'),
    path('work_orders/<int:pk>/',
         views.ViAgentWorkOrderDetail.as_view(),
         name='agentwo-detail'),
]
