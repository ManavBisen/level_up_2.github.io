from django.urls import path
from . import views

urlpatterns = [
    path('', views.shop, name='shop'),
    path('manage/', views.manage_shop, name='manage_shop'),
    path('add-item/', views.add_shop_item, name='add_shop_item'),
    path('edit-item/<int:item_id>/', views.edit_shop_item, name='edit_shop_item'),
    path('delete-item/<int:item_id>/', views.delete_shop_item, name='delete_shop_item'),
    path('purchase/<int:item_id>/', views.purchase_item, name='purchase_item'),
    path('my-purchases/', views.my_purchases, name='my_purchases'),
    path('download/<int:purchase_id>/', views.download_purchased_item, name='download_purchased_item'),
]
