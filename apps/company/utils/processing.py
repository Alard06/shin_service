import xml.etree.ElementTree as ET
from datetime import datetime

from django.utils import timezone
from itertools import groupby

from apps.suppliers.models import Tire, TireSupplier, Supplier, CompanySupplier, TruckTireSupplier, DiskSupplier, \
    SpecialTireSupplier, MotoTireSupplier


def get_available_products_for_company(company_id, types, availability):
    # Получаем всех поставщиков, связанных с данной компанией через CompanySupplier
    print(types, availability)

    suppliers = Supplier.objects.filter(companysupplier__company_id=company_id)

    # Инициализируем словарь для группировки доступных продуктов
    grouped_products = {
        'tires': {},
        'disks': {},
        'truck_tires': {},
        'special_tires': {},
        'moto_tires': {}
    }

    # Проверяем, какие типы продуктов были выбраны
    # Проверяем, какие типы продуктов были выбраны
    if 'tires' in types:
        # Получаем все шины, которые в наличии у этих поставщиков
        tire_filters = {
            'supplier__in': suppliers,
        }
        if availability == 'in_stock':
            tire_filters['quantity__gt'] = 0
        elif availability == 'out_of_stock':
            tire_filters['quantity__lte'] = 0

        available_tires = TireSupplier.objects.filter(**tire_filters).select_related('tire')

        for tire_supplier in available_tires:
            tire_id = tire_supplier.tire.id_tire
            if tire_id not in grouped_products['tires']:
                grouped_products['tires'][tire_id] = {
                    'product': tire_supplier.tire,
                    'suppliers': []
                }
            grouped_products['tires'][tire_id]['suppliers'].append(tire_supplier)

    if 'disks' in types:
        # Получаем все диски, которые в наличии у этих поставщиков
        disk_filters = {
            'supplier__in': suppliers,
        }
        if availability == 'in_stock':
            disk_filters['quantity__gt'] = 0
        elif availability == 'out_of_stock':
            disk_filters['quantity__lte'] = 0

        available_disks = DiskSupplier.objects.filter(**disk_filters).select_related('disk')

        for disk_supplier in available_disks:
            disk_id = disk_supplier.disk.id_disk  # Предполагается, что у модели Disk есть поле id_disk
            if disk_id not in grouped_products['disks']:
                grouped_products['disks'][disk_id] = {
                    'product': disk_supplier.disk,
                    'suppliers': []
                }
            grouped_products['disks'][disk_id]['suppliers'].append(disk_supplier)

    if 'truck_tires' in types:
        # Получаем все грузовые шины, которые в наличии у этих поставщиков
        truck_tire_filters = {
            'supplier__in': suppliers,
        }
        if availability == 'in_stock':
            truck_tire_filters['quantity__gt'] = 0
        elif availability == 'out_of_stock':
            truck_tire_filters['quantity__lte'] = 0

        available_truck_tires = TruckTireSupplier.objects.filter(**truck_tire_filters).select_related('truck_tire')

        for truck_tire_supplier in available_truck_tires:
            truck_tire_id = truck_tire_supplier.truck_tire.id_truck  # Предполагается, что у модели TruckTire есть поле id_truck_tire
            if truck_tire_id not in grouped_products['truck_tires']:
                grouped_products['truck_tires'][truck_tire_id] = {
                    'product': truck_tire_supplier.truck_tire,
                    'suppliers': []
                }
            grouped_products['truck_tires'][truck_tire_id]['suppliers'].append(truck_tire_supplier)

    if 'special_tires' in types:
        # Получаем все специальные шины, которые в наличии у этих поставщиков
        special_tire_filters = {
            'supplier__in': suppliers,
        }
        if availability == 'in_stock':
            special_tire_filters['quantity__gt'] = 0
        elif availability == 'out_of_stock':
            special_tire_filters['quantity__lte'] = 0

        available_special_tires = SpecialTireSupplier.objects.filter(**special_tire_filters).select_related(
            'special_tire')

        for special_tire_supplier in available_special_tires:
            special_tire_id = special_tire_supplier.special_tire.id_special  # Предполагается, что у модели SpecialTire есть поле id_special_tire
            if special_tire_id not in grouped_products['special_tires']:
                grouped_products['special_tires'][special_tire_id] = {
                    'product': special_tire_supplier.special_tire,
                    'suppliers': []
                }
            grouped_products['special_tires'][special_tire_id]['suppliers'].append(special_tire_supplier)

    if 'moto_tires' in types:
        # Получаем все мотоциклетные шины, которые в наличии у этих поставщиков
        moto_tire_filters = {
            'supplier__in': suppliers,
        }
        if availability == 'in_stock':
            moto_tire_filters['quantity__gt'] = 0
        elif availability == 'out_of_stock':
            moto_tire_filters['quantity__lte'] = 0

        available_moto_tires = MotoTireSupplier.objects.filter(**moto_tire_filters).select_related('moto_tire')

        for moto_tire_supplier in available_moto_tires:
            moto_tire_id = moto_tire_supplier.moto_tire.id_moto  # Предполагается, что у модели MotoTire есть поле id_moto_tire
            if moto_tire_id not in grouped_products['moto_tires']:
                grouped_products['moto_tires'][moto_tire_id] = {
                    'product': moto_tire_supplier.moto_tire,
                    'suppliers': []
                }
            grouped_products['moto_tires'][moto_tire_id]['suppliers'].append(moto_tire_supplier)

    # Сохраняем данные в XML файл
    save_tires_to_xml_availability(grouped_products, company_id, types)
    return grouped_products


def save_tires_to_xml_availability(grouped_products, company_id, types):
    # Создаем корневой элемент
    root = ET.Element("root")

    # Обрабатываем шины
    if 'tires' in types:
        process_tires(root, grouped_products['tires'], company_id)

    if 'disks' in types:
        process_disks(root, grouped_products['disks'], company_id)

    # Обрабатываем грузовые шины
    if 'truck_tires' in types:
        process_truck_tires(root, grouped_products['truck_tires'], company_id)

    # Генерируем строку XML
    xml_str = ET.tostring(root, encoding='utf-8', xml_declaration=True).decode('utf-8')
    date = datetime.now().strftime("%d-%m-%H-%M")
    name = f'Обработчик-{date}.xml'

    # Сохраняем XML в файл
    with open(f'media/uploads/{name}', 'a', encoding='utf-8') as xml_file:
        xml_file.write(xml_str.replace("><", ">\n<"))  # Добавляем переносы строк между элементами

    print(f"XML сохранен в файл: {name}")


def process_tires(root, tires, company_id):
    tires_elements = ET.SubElement(root, 'tires')
    for tire_id, data in tires.items():
        tire_element = ET.SubElement(tires_elements, "tire",
                                     id=tire_id,
                                     brandArticul=str(data['product'].brand_article) if data[
                                         'product'].brand_article else '',
                                     brand=data['product'].brand,
                                     product=data['product'].product,
                                     fullTitle=data['product'].full_title,
                                     headline='#',  # TODO
                                     measurement='метрическая',
                                     recommendedPrice='',
                                     model=data['product'].model,
                                     width=data['product'].width,
                                     height=data['product'].height,
                                     diameter=data['product'].diameter,
                                     season=data['product'].season,
                                     spike="да" if data['product'].spike else "нет",
                                     lightduty="да" if data['product'].lightduty else "нет",
                                     indexes=str(data['product'].indexes) if data['product'].indexes else '',
                                     system='',
                                     omolagation=str(data['product'].omolagation) if data[
                                         'product'].omolagation else '',
                                     mud=str(data['product'].mud) if data['product'].mud else '',
                                     at=str(data['product'].at) if data['product'].at else '',
                                     runFlatTitle=str(data['product'].runflat) if data['product'].runflat else '',
                                     fr=str(data['product'].fr) if data['product'].fr else '',
                                     xl=str(data['product'].xl) if data['product'].xl else '',
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
                                     runflat="да" if data['product'].runflat else "нет",
                                     ProtectorType=""
                                     )

        sorted_suppliers = sort_suppliers(data['suppliers'], company_id)

        articuls, best_supplier, best_price, total_quantity, best_delivery_period_days, product_supplier = process_suppliers(
            sorted_suppliers, data['product'], company_id)

        if best_supplier:
            create_supplier_element(tire_element, articuls, best_supplier, best_price, total_quantity,
                                    best_delivery_period_days, product_supplier)


def process_disks(root, disks, company_id):
    disks_elements = ET.SubElement(root, 'disks')
    for disk_id, data in disks.items():
        disk_element = ET.SubElement(disks_elements, "disk",
                                     id=disk_id,
                                     brandArticul=str(data['product'].brand_articul) if data[
                                         'product'].brand_articul else '',
                                     brand=data['product'].brand,
                                     product=data['product'].product,
                                     fullTitle=data['product'].full_title,
                                     headline='#',
                                     measurement='#',
                                     recommendedPrice='',
                                     model=data['product'].model,
                                     width=data['product'].width,
                                     height='',
                                     diameter=data['product'].diameter,
                                     season='',
                                     spike='',
                                     lightduty="",
                                     indexes='',
                                     system='',
                                     omolagation='',
                                     mud='',
                                     at='',
                                     runFlatTitle= '',
                                     fr='',
                                     xl='',
                                     autobrand='',
                                     pcd=data['product'].pcd,
                                     boltcount=str(data['product'].boltcount) if data['product'].boltcount else '',
                                     drill='',
                                     outfit=str(data['product'].outfit) if data['product'].outfit else '',
                                     dia=str(data['product'].dia) if data['product'].dia else '',
                                     color=data['product'].color,
                                     type=data['product'].type,
                                     numberOfPlies='',
                                     axis='',
                                     quadro='',
                                     special='',
                                     note='',
                                     typesize='',
                                     kit='',
                                     layers='',
                                     camera='',
                                     Dioganal='',
                                     Solid='',
                                     Note='',
                                     Countries='',
                                     runflat="",
                                     ProtectorType='',
                                     Type=str(data['product'].type) if data['product'].type else ''
                                     )

        sorted_suppliers = sort_suppliers(data['suppliers'], company_id)

        articuls, best_supplier, best_price, total_quantity, best_delivery_period_days, product_supplier = process_suppliers(
            sorted_suppliers, data['product'], company_id, is_disk=True)

        if best_supplier:
            create_supplier_element(disk_element, articuls, best_supplier, best_price, total_quantity,
                                    best_delivery_period_days, product_supplier, is_disk=True)


def process_truck_tires(root, truck_tires, company_id):
    trucks = ET.SubElement(root, 'trucks')
    for truck_tire_id, data in truck_tires.items():
        truck_tire_element = ET.SubElement(trucks, "truckTire",
                                           id=truck_tire_id,
                                           brandArticul=str(data['product'].brand_articul) if data[
                                               'product'].brand_articul else '',
                                           brand=data['product'].brand,
                                           product=data['product'].product,
                                           fullTitle=data['product'].full_title,
                                           headline='#',
                                           measurement='метрическая',
                                           recommendedPrice='',
                                           model=data['product'].model,
                                           width=data['product'].width,
                                           height='',
                                           diameter=data['product'].diameter,
                                           season='',
                                           spike="",
                                           lightduty="да" if data['product'].lightduty else "нет",
                                           indexes=str(data['product'].indexes) if data['product'].indexes else '',
                                           system='',
                                           omolagation='',
                                           mud='',
                                           at='',
                                           runFlatTitle='',
                                           fr='',
                                           xl='',
                                           autobrand='',
                                           pcd='',
                                           boltcount='',
                                           drill='',
                                           outfit='',
                                           dia='',
                                           color='',
                                           type='',
                                           numberOfPlies=str(data['product'].number_of_plies) if data[
                                               'product'].number_of_plies else '',
                                           axis=str(data['product'].axis) if data[
                                               'product'].axis else '',
                                           quadro=str(data['product'].quadro) if data[
                                               'product'].quadro else '',
                                           special=str(data['product'].special) if data[
                                               'product'].special else '',
                                           note='',
                                           typesize='',
                                           kit='',
                                           layers='',
                                           camera='',
                                           Dioganal='',
                                           Solid='',
                                           Note='',
                                           Countries='',
                                           runflat='',
                                           ProtectorType='',
                                           Type=''
                                           )

        sorted_suppliers = sort_suppliers(data['suppliers'], company_id)

        articuls, best_supplier, best_price, total_quantity, best_delivery_period_days, product_supplier = process_suppliers(
            sorted_suppliers, data['product'], company_id, is_truck_tire=True)

        if best_supplier:
            create_supplier_element(truck_tire_element, articuls, best_supplier, best_price, total_quantity,
                                    best_delivery_period_days, product_supplier, is_truck_tire=True)


def sort_suppliers(suppliers, company_id):
    return sorted(
        suppliers,
        key=lambda s: (
            -CompanySupplier.objects.get(company_id=company_id, supplier=s.supplier).priority,
            CompanySupplier.objects.get(company_id=company_id, supplier=s.supplier).visual_priority
        )
    )


def process_suppliers(sorted_suppliers, product, company_id, is_disk=False, is_truck_tire=False):
    articuls = []
    best_supplier = None
    best_price = None
    total_quantity = 0
    best_delivery_period_days = None
    product_supplier = None  # Initialize product_supplier

    for supplier in sorted_suppliers:
        company_supplier = CompanySupplier.objects.get(company_id=company_id, supplier=supplier.supplier)
        articuls.append(company_supplier.article_number or '')

        if is_disk:
            product_supplier = DiskSupplier.objects.filter(disk=product, supplier=supplier.supplier).first()
        elif is_truck_tire:
            product_supplier = TruckTireSupplier.objects.filter(truck_tire=product, supplier=supplier.supplier).first()
        else:
            product_supplier = TireSupplier.objects.filter(tire=product, supplier=supplier.supplier).first()

        if product_supplier:
            total_quantity += int(product_supplier.quantity)

            if best_supplier is None or (
                    company_supplier.priority < best_supplier.priority or
                    (
                            company_supplier.priority == best_supplier.priority and company_supplier.visual_priority < best_supplier.visual_priority
                    )
            ):
                best_supplier = company_supplier
                best_price = product_supplier.price
                best_delivery_period_days = product_supplier.delivery_period_days

    return articuls, best_supplier, best_price, total_quantity, best_delivery_period_days, product_supplier  # Ensure product_supplier is returned


def create_supplier_element(parent_element, articuls, best_supplier, best_price, total_quantity,
                            best_delivery_period_days, product_supplier=None, is_disk=False, is_truck_tire=False):
    supplier_element = ET.SubElement(parent_element, "supplier",
                                     articul=", ".join([el for el, _ in groupby(articuls)]),
                                     supplierTitle=articuls[0] or '',
                                     quantity=str(total_quantity),
                                     price=best_price,
                                     inputPrice=product_supplier.input_price if product_supplier else '',
                                     price_rozn=best_price if best_supplier else '',
                                     deliveryPeriodDays=str(
                                         best_delivery_period_days) if best_delivery_period_days is not None else '',
                                     tireType="Обычная" if not is_disk and not is_truck_tire else "Специальная" if is_disk else "Грузовая",
                                     stock='Наличие',
                                     supplier=str(best_supplier.supplier.id),
                                     presence='В наличии',
                                     lastAvailabilityDate=product_supplier.last_availability_date.strftime(
                                         "%d.%m.%Y %H:%M:%S") if product_supplier else '',
                                     sale='',
                                     year=""
                                     )
