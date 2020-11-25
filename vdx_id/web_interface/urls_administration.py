from django.urls import path

from . import views_administration as views

urlpatterns = [
    path('index', views.index, name='index'),
    path('admin_view', views.admin_view, name='admin_view'),
    path('report_builder', views.report_builder, name='report_builder'),
    path('sql_explorer', views.sql_explorer, name='sql_explorer'),
]
