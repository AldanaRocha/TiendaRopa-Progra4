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

    path("pago/<int:product_id>/", views.create_preference_cart, name="crear-preferencia"),
 
    # Carrito
    path('add/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('cart/', views.view_cart, name='view-cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove-from-cart'),
    path('update/<int:product_id>/', views.update_cart_quantity, name='update-cart'),
    path('clear/', views.clear_cart, name='clear-cart'),
    path('create-preference/', views.create_preference_cart, name='create-preference-cart'),
]

