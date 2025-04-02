from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark_read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark_all_read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('search/', views.user_search, name='user_search'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    path('add_extra_title/<int:user_id>/<str:title>/', views.add_extra_title, name='add_extra_title'),
]
