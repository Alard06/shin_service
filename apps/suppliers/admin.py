from django.contrib import admin

from .models import Supplier, City, CompanySupplier

# Register your models here.
admin.site.register(Supplier)
admin.site.register(City)
admin.site.register(CompanySupplier)
