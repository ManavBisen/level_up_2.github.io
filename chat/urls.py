from django.urls import path
from . import views

urlpatterns = [
    path('direct-messages/', views.direct_messages, name='direct_messages'),
    path('direct-messages/<str:username>/', views.direct_message_conversation, name='direct_message_conversation'),
    path('send-direct-message/', views.send_direct_message, name='send_direct_message'),
    path('delete-direct-message/<int:message_id>/', views.delete_direct_message, name='delete_direct_message'),
    path('community/', views.community_chat, name='community_chat'),
    path('send-community-message/', views.send_community_message, name='send_community_message'),
    path('delete-community-message/<int:message_id>/', views.delete_community_message, name='delete_community_message'),
]
