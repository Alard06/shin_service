from lxml import etree
from django.utils import timezone


from django.db.models import Q

from apps.suppliers.models import Supplier, TireSupplier


def get_available_tires_for_company(company_id):
    # Получаем всех поставщиков, связанных с данной компанией
    suppliers = Supplier.objects.filter(companies__id=company_id)

    # Получаем все шины, которые в наличии у этих поставщиков
    available_tires = TireSupplier.objects.filter(
        supplier__in=suppliers,
        quantity__gt=0  # Убедитесь, что количество больше 0
    ).select_related('tire')

    # Группируем шины по их идентификатору, чтобы получить одинаковые шины у разных поставщиков
    grouped_tires = {}
    for tire_supplier in available_tires:
        tire_id = tire_supplier.tire.id_tire
        if tire_id not in grouped_tires:
            grouped_tires[tire_id] = {
                'tire': tire_supplier.tire,
                'suppliers': []
            }
        grouped_tires[tire_id]['suppliers'].append(tire_supplier)

    return grouped_tires

get_available_tires_for_company(1)