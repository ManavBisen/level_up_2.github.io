from django.urls import path
from . import views

urlpatterns = [
    path('daily/', views.daily_tasks, name='daily_tasks'),
    path('good-work/', views.good_work_timer, name='good_work_timer'),
    path('start-timer/', views.start_timer, name='start_timer'),
    path('stop-timer/', views.stop_timer, name='stop_timer'),
    path('create-extra-task/', views.create_extra_task, name='create_extra_task'),
]
