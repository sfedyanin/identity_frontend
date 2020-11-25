from django.urls import path
from . import views

app_name = 'id_access'

urlpatterns = [
     path('items', views.ViAccessItemList.as_view(),
          name='item-list'),
     path('items/<int:pk>/', views.ViAccessItemDetail.as_view(),
          name='item-detail'),

     path('groups/', views.ViAccessGroupList.as_view(),
          name='group-list'),
     path('groups/<int:pk>/', views.ViAccessGroupDetail.as_view(),
          name='group-detail'),

     path('item_requests/', views.ViAccessItemRequestList.as_view(),
          name='item_request-list'),
     path('item_requests/<int:pk>/', views.ViAccessItemRequestDetail.as_view(),
          name='item_request-detail'),

     path('group_requests/',
          views.ViAccessGroupRequestList.as_view(),
          name='group_request-list'),
     path('group_requests/<int:pk>/',
          views.ViAccessGroupRequestDetail.as_view(),
          name='group_request-detail'),
          
     path('group_requests/<int:pk>/approve',
          views.approve_request,
          name='group_request-approve'),
     path('group_requests/<int:pk>/reject',
          views.reject_request,
          name='group_request-reject'),

     path('group_memberships/',
          views.ViAccessGroupMembershipList.as_view(),
          name='group_membership-list'),
     # # Datatable view
     # path('datatable/accessgroups', views.AccessGroupJson.as_view(),
     #      name='data-accessgroups'),
     # path('datatable/accessgroup_memberships', views.AccessMembershipJson.as_view(),
     #      name='data-accessmemberships'),
]
