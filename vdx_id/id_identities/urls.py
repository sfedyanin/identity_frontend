from django.urls import path
from . import views

app_name = 'id_identities'

urlpatterns = [
    path('identitiy/', views.VdxIdentityList.as_view(),
         name='identitiy-list'),
    path('identitiy/<int:pk>/', views.VdxIdentityDetail.as_view(),
         name='identitiy-detail')
]
