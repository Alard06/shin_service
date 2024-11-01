from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from apps.company.forms import CompanyForm
from apps.company.models import Company
from apps.company.utils.processing import get_available_products_for_company
from apps.suppliers.models import Supplier, CompanySupplier, SpecialTireSupplier, TireSupplier, DiskSupplier, \
    TruckTireSupplier, MotoTireSupplier


# Create your views here.
def company_list(request):
    """ Функция для отображения списка всех компаний """
    companies = Company.objects.all()  # Получаем все компании
    return render(request, 'company_list.html', {'companies': companies})


def create_company(request):
    """ Функция для создания новой компании """
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем новую компанию
            return redirect('company_list')  # Перенаправляем на список компаний
    else:
        form = CompanyForm()

    return render(request, 'create_company.html', {'form': form})


def company_detail(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    # Получаем всех поставщиков, связанных с данной компанией
    suppliers = CompanySupplier.objects.filter(company=company).select_related('supplier')

    # Получаем всех поставщиков
    all_suppliers = Supplier.objects.all()

    # Исключаем поставщиков, которые уже связаны с данной компанией
    selected_supplier_ids = suppliers.values_list('supplier_id', flat=True)
    available_suppliers = all_suppliers.exclude(id__in=selected_supplier_ids)

    # Получаем специальные шины для выбранных поставщиков
    special_tires = SpecialTireSupplier.objects.filter(supplier__in=suppliers.values_list('supplier', flat=True))
    tires = TireSupplier.objects.filter(supplier__in=suppliers.values_list('supplier', flat=True))
    moto = MotoTireSupplier.objects.filter(supplier__in=suppliers.values_list('supplier', flat=True))
    disk = DiskSupplier.objects.filter(supplier__in=suppliers.values_list('supplier', flat=True))
    truck = TruckTireSupplier.objects.filter(supplier__in=suppliers.values_list('supplier', flat=True))

    if request.method == 'POST':
        selected_suppliers = request.POST.getlist('suppliers')

        # Обработка генерации XML
        if 'generate_xml' in request.POST:
            # get_available_products_for_company(company.id)
            return redirect('company_detail', company_id=company.id)  # Перенаправляем обратно

        # Обработка выбора поставщиков и их приоритетов
        if selected_suppliers:
            for supplier_id in selected_suppliers:
                supplier = get_object_or_404(Supplier, id=supplier_id)
                priority = request.POST.get(f'priority_{supplier_id}', 1)  # Получаем приоритет для каждого поставщика
                visual_priority = request.POST.get(f'visual_priority_{supplier_id}', 1)  # Получаем визуальный приоритет

                # Убедитесь, что приоритет и визуальный приоритет корректно сохраняются
                CompanySupplier.objects.update_or_create(
                    company=company,
                    supplier=supplier,
                    defaults={'priority': priority, 'visual_priority': visual_priority}
                )

        # Обработка выбора типов и наличия
        types = request.POST.getlist('types')  # Получаем список выбранных типов
        availability = request.POST.get('availability')  # Получаем выбранное значение наличия
        if types and availability:
            get_available_products_for_company(company_id, types, availability)
        # Здесь можно добавить логику для обработки типов и наличия, если это необходимо
        # Например, можно сохранить эти данные в базе данных или выполнить другие действия

        return redirect('company_detail', company_id=company.id)  # Перенаправляем обратно на страницу компании

    return render(request, 'company_detail.html', {
        'company': company,
        'suppliers': suppliers,  # Поставщики, связанные с компанией
        'available_suppliers': available_suppliers,  # Поставщики, которые еще не выбраны
        'special_tires': special_tires,  # Специальные шины для выбранных поставщиков
        'tires': tires,  # Шины для выбранных поставщиков
        'disks': disk,  # Диски для выбранных поставщиков
        'moto': moto,  # Мото для выбранных поставщиков
        'trucks': truck,  # Truck для выбранных поставщиков
    })



def add_suppliers_to_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        # Получаем строку с идентификаторами и разбиваем её на список
        selected_suppliers = request.POST.get('suppliers', '').split(',')
        priority = request.POST.get('priority')

        for supplier_id in selected_suppliers:
            if supplier_id:  # Проверяем, что идентификатор не пустой
                supplier = get_object_or_404(Supplier, id=supplier_id)
                CompanySupplier.objects.update_or_create(
                    company=company,
                    supplier=supplier,
                    defaults={'priority': priority}
                )
        return redirect('company_detail', company_id=company.id)  # Перенаправляем обратно на страницу компании

    all_suppliers = Supplier.objects.all()  # Получаем всех поставщиков для выбора
    return render(request, 'add_suppliers.html', {
        'company': company,
        'all_suppliers': all_suppliers,
    })


def delete_supplier_company(request, supplier_id, company_id):
    # Attempt to retrieve the CompanySupplier object or return a 404 error if not found
    print(supplier_id, company_id)

    company_supplier = get_object_or_404(CompanySupplier, supplier_id=supplier_id, company_id=company_id)

    if request.method == 'POST':
        # Log the deletion and delete the relationship
        company_supplier.delete()
        messages.success(request, 'Supplier relationship successfully deleted.')
        return redirect('company_detail', company_id=company_id)

    # If the request method is not POST, redirect to the company detail page
    messages.info(request, 'No changes made.')


def edit_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect('company_detail', company_id=company.id)  # Перенаправляем обратно на страницу компании
    else:
        form = CompanyForm(instance=company)

    return render(request, 'edit_company.html', {'form': form, 'company': company})


def delete_company(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        company.delete()
        return redirect('company_list')  # Перенаправляем на список компаний после удаления

    return render(request, 'confirm_delete.html', {'company': company})
