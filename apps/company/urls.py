from django.urls import path

from .views import company_list, create_company, company_detail, add_suppliers_to_company, delete_supplier

urlpatterns = [
    path('companies/', company_list, name='company_list'),
    path('companies/create/', create_company, name='create_company'),
    path('companies/<int:company_id>/', company_detail, name='company_detail'),
path('companies/<int:company_id>/add-suppliers/', add_suppliers_to_company, name='add_suppliers_to_company'),
    path('supplier/delete/<int:supplier_id>/company/<int:company_id>/', delete_supplier, name='delete_supplier'),
]
