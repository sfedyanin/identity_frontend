from django.urls import path
from . import views_access_management as views


urlpatterns = [
     path('home', views.home,
          name='home'),

     path('view_access', views.view_access,
          name='view_access'),
     path('my_access', views.my_access,
          name='my_access'),
     path('access_approvals', views.access_approvals,
          name='access_approvals'),
     
     path('view_platforms', views.view_platforms,
          kwargs={'platform_id': None}, name='view_platforms'),
     path('view_platforms/<platform_id>/', views.view_platforms,
          name='view_platforms'),

     path('view_servers', views.view_servers,
          kwargs={'sgroup_id': None}, name='view_servers'),
     path('view_servers/<sgroup_id>/', views.view_servers,
          name='view_servers'),

     path('access_network', views.access_network,
          name='access_network'),
     
     path('map_visual', views.map_visual,
          name='map_visual'),
     
     path('report_builder', views.report_builder, name='report_builder'),
     path('sql_explorer', views.sql_explorer, name='sql_explorer')
]
