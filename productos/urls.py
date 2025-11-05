from django.urls import path
from . import views


urlpatterns = [

    path("", views.product_list, name="product-list"),
    path("create/", views.product_create, name="product-create"),
    path("edit/<int:pk>/", views.product_edit, name="product-edit"),
    path("delete/<int:pk>/", views.product_delete, name="product-delete"),

    # path("pago/<int:product_id>/", create_preference, name="crear-preferencia"),
 

]