from django.urls import path
from . import views

urlpatterns = [
    path('daily/', views.daily_tasks, name='daily_tasks'),
    path('extra/', views.extra_tasks, name='extra_tasks'),
    path('extra/add/', views.add_extra_task, name='add_extra_task'),
    path('extra/complete/<int:task_id>/', views.complete_extra_task, name='complete_extra_task'),
    path('good-work/', views.good_work, name='good_work'),
    path('good-work/start/', views.start_good_work, name='start_good_work'),
    path('good-work/end/', views.end_good_work, name='end_good_work'),
    path('submit-daily-tasks/', views.submit_daily_tasks, name='submit_daily_tasks'),
    path('update-daily-task/', views.update_daily_task, name='update_daily_task'),
]
