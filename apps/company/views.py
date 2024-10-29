from django.shortcuts import render, redirect, get_object_or_404

from apps.company.forms import CompanyForm
from apps.company.models import Company
from apps.suppliers.models import Supplier, CompanySupplier


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

    if request.method == 'POST':
        selected_suppliers = request.POST.getlist('suppliers')

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
        return redirect('company_detail', company_id=company.id)  # Перенаправляем обратно на страницу компании

    return render(request, 'company_detail.html', {
        'company': company,
        'suppliers': suppliers,  # Поставщики, связанные с компанией
        'available_suppliers': available_suppliers,  # Поставщики, которые еще не выбраны
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


def delete_supplier(request, supplier_id, company_id):
    # Получаем связь между поставщиком и компанией
    company_supplier = get_object_or_404(CompanySupplier, supplier_id=supplier_id, company_id=company_id)

    if request.method == 'POST':
        company_supplier.delete()  # Удаляем связь между поставщиком и компанией
        return redirect('company_detail', company_id=company_id)  # Перенаправляем на страницу компании

    return redirect('company_detail', company_id=company_id)  # В случае GET-запроса также перенаправляем