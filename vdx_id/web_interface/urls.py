from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    
    path('access_management/',
        include(('web_interface.urls_access_management', 'api'),
                namespace='acm')),

    path('administration/',
        include(('web_interface.urls_administration', 'api'),
                namespace='adm')),
]
