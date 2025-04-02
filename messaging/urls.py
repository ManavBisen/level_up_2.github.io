from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('dm/<str:username>/', views.direct_message, name='direct_message'),
    path('dm/delete/<int:message_id>/', views.delete_direct_message, name='delete_direct_message'),
    path('community/', views.community, name='community'),
    path('community/delete/<int:message_id>/', views.delete_community_message, name='delete_community_message'),
    path('unread-count/', views.unread_message_count, name='unread_message_count'),
]
