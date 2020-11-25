from django.urls import path
from . import views

app_name = 'id_accounts'

urlpatterns = [
    path('account/', views.ViAccountList.as_view(),
         name='account-list'),
    path('account/<int:pk>/', views.ViAccountDetail.as_view(),
         name='account-detail'),
]
