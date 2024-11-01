import xml.etree.ElementTree as ET
from datetime import datetime

from django.utils import timezone

from apps.suppliers.models import Tire, TireSupplier, Supplier, CompanySupplier


def get_available_tires_for_company(company_id):
    # Получаем всех поставщиков, связанных с данной компанией через CompanySupplier
    suppliers = Supplier.objects.filter(companysupplier__company_id=company_id)

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

    # Сохраняем данные в XML файл
    save_tires_to_xml_availability(grouped_tires, company_id)

    return grouped_tires


def save_tires_to_xml_availability(grouped_tires, company_id):
    # Создаем корневой элемент
    root = ET.Element("tires")

    for tire_id, data in grouped_tires.items():
        tire_element = ET.SubElement(root, "tire",
                                     id=tire_id,
                                     brandArticul=str(data['tire'].brand_article) if data['tire'].brand_article else '',
                                     brand=data['tire'].brand,
                                     product=data['tire'].product,
                                     fullTitle=data['tire'].full_title,
                                     headline='#', # TODO
                                     measurement='метрическая',
                                     recommendedPrice='',
                                     model=data['tire'].model,
                                     width=data['tire'].width,
                                     height=data['tire'].height,
                                     diameter=data['tire'].diameter,
                                     season=data['tire'].season,
                                     spike="да" if data['tire'].spike else "нет",
                                     lightduty="да" if data['tire'].lightduty else "нет",
                                     indexes=str(data['tire'].indexes) if data['tire'].indexes else '',
                                     system='',
                                     omolagation=str(data['tire'].omolagation) if data['tire'].omolagation else '',
                                     mud=str(data['tire'].mud) if data['tire'].mud else '',
                                     at=str(data['tire'].at) if data['tire'].at else '',
                                     runFlatTitle=str(data['tire'].runflat) if data['tire'].runflat else '',
                                     fr=str(data['tire'].fr) if data['tire'].fr else '',
                                     xl=str(data['tire'].xl) if data['tire'].xl else '',
                                     autobrand="",
                                     pcd="",
                                     boltcount="",
                                     drill="",
                                     outfit="",
                                     dia="",
                                     color="",
                                     type="",
                                     numberOfPlies="",
                                     axis="",
                                     quadro="",
                                     special="",
                                     note="",
                                     typesize="",
                                     kit="",
                                     layers="",
                                     camera="",
                                     Dioganal="",
                                     Solid="",
                                     Note="",
                                     Countries="",
                                     runflat="да" if data['tire'].runflat else "нет",
                                     ProtectorType=""
                                     )

        # Получаем и сортируем поставщиков по priority и visual_priority
        sorted_suppliers = sorted(
            data['suppliers'],
            key=lambda s: (
                -CompanySupplier.objects.get(company_id=company_id, supplier=s.supplier).priority,
                CompanySupplier.objects.get(company_id=company_id, supplier=s.supplier).visual_priority
            )
        )

        # Объединяем артикулы и выбираем лучшего поставщика
        articuls = []
        best_supplier = None
        best_price = None
        total_quantity = 0  # Сумма всех шин у всех поставщиков
        best_quantity = None
        best_delivery_period_days = None

        for supplier in sorted_suppliers:
            company_supplier = CompanySupplier.objects.get(company_id=company_id, supplier=supplier.supplier)
            articuls.append(company_supplier.article_number or '')

            # Получаем информацию о цене и количестве из TireSupplier
            tire_supplier = TireSupplier.objects.filter(tire=data['tire'], supplier=supplier.supplier).first()

            if tire_supplier:
                total_quantity += tire_supplier.quantity  # Суммируем количество

                # Определяем лучшего поставщика
                if best_supplier is None or (
                        company_supplier.priority < best_supplier.priority or
                        (
                                company_supplier.priority == best_supplier.priority and company_supplier.visual_priority < best_supplier.visual_priority)
                ):
                    best_supplier = company_supplier
                    best_price = tire_supplier.price
                    best_delivery_period_days = tire_supplier.delivery_period_days  # Получаем delivery_period_days

        # Создаем элемент поставщика с данными лучшего поставщика
        if best_supplier:
            supplier_element = ET.SubElement(tire_element, "supplier",
                                             articul=", ".join(set(articuls)),
                                             supplierTitle=articuls[0] or '',
                                             quantity=str(total_quantity),  # Используем количество лучшего поставщика
                                             price=best_price,
                                             inputPrice=tire_supplier.input_price if tire_supplier else '',
                                             price_rozn=best_price if tire_supplier else '',
                                             deliveryPeriodDays=str(
                                                 best_delivery_period_days) if best_delivery_period_days is not None else '',
                                             tireType="Обычная",
                                             stock='Наличие',
                                             supplier=str(best_supplier.supplier.id),
                                             presence='В наличии',
                                             lastAvailabilityDate=tire_supplier.last_availability_date.strftime(
                                                 "%d.%m.%Y %H:%M:%S") if tire_supplier else '',
                                             sale="yes" if supplier.sale else "no",
                                             year=""
                                             )

    # Генерируем строку XML
    xml_str = ET.tostring(root, encoding='utf-8', xml_declaration=True).decode('utf-8')
    date = datetime.now().strftime("%d-%m-%H-%M")
    name = f'Обработчик-{date}.xml'
    # Сохраняем XML в файл
    with open(f'media/uploads/{name}', 'w', encoding='utf-8') as xml_file:
        xml_file.write(xml_str.replace("><", ">\n<"))  # Добавляем переносы строк между элементами

    print(f"XML сохранен в файл: {name}")


