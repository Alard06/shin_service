from django.urls import path

from apps.suppliers.views import supplier_list, create_supplier, edit_supplier, delete_supplier

urlpatterns = [
    path('', supplier_list, name='supplier_list'),
    path('create/', create_supplier, name='create_supplier'),
    path('edit/<int:supplier_id>/', edit_supplier, name='edit_supplier'),
    path('delete/<int:supplier_id>/', delete_supplier, name='delete_supplier'),
]
