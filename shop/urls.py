from django.urls import path
from . import views

urlpatterns = [
    path('', views.shop, name='shop'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('download/<int:purchase_id>/', views.download_item, name='download_item'),
    path('purchases/', views.my_purchases, name='my_purchases'),
    path('create/', views.create_shop_item, name='create_shop_item'),
    path('edit/<int:item_id>/', views.edit_shop_item, name='edit_shop_item'),
    path('delete/<int:item_id>/', views.delete_shop_item, name='delete_shop_item'),
]
