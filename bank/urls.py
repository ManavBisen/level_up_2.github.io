from django.urls import path
from . import views

urlpatterns = [
    path('', views.bank, name='bank'),
    path('transaction/', views.make_transaction, name='make_transaction'),
    path('transaction/history/', views.transaction_history, name='transaction_history'),
    path('set-password/', views.set_bank_password, name='set_bank_password'),
]
