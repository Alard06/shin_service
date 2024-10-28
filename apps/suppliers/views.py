from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Supplier
from .forms import SupplierForm


def supplier_list(request):
    suppliers = Supplier.objects.all()  # Получаем всех поставщиков
    return render(request, 'supplier_list.html', {'suppliers': suppliers})


def create_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')  # Перенаправление на страницу со списком поставщиков
    else:
        form = SupplierForm()
    return render(request, 'create_supplier.html', {'form': form})

def edit_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)  # Получаем поставщика по ID
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)  # Передаем существующий объект
        if form.is_valid():
            form.save()
            return redirect('supplier_list')  # Перенаправление на страницу со списком поставщиков
    else:
        form = SupplierForm(instance=supplier)  # Заполняем форму существующими данными
    return render(request, 'edit_supplier.html', {'form': form, 'supplier': supplier})


@require_POST
def delete_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    supplier.delete()
    return redirect('supplier_list')