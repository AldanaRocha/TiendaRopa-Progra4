from django.urls import path
from . import views


urlpatterns = [

    path("", views.product_list, name="product-list"),
    path("create/", views.product_create, name="product-create"),
    path("edit/<int:pk>/", views.product_edit, name="product-edit"),
    path("delete/<int:pk>/", views.product_delete, name="product-delete"),
 
    path('checkout/<int:product_id>/', views.checkout, name='checkout'),
    path('pago/exitoso/', views.pago_exitoso, name='pago_exitoso'),
    path('pago/fallido/', views.pago_fallido, name='pago_fallido'),
    path('pago/pendiente/', views.pago_pendiente, name='pago_pendiente'),

]