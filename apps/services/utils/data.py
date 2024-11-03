from django.utils import timezone
import xml.etree.ElementTree as ET
from asgiref.sync import sync_to_async

from apps.services.utils.db import get_tire_objects, tire_supplier_bulk_create, get_truck_objects, \
    truck_tire_supplier_bulk_create, get_special_tire_objects, special_tire_supplier_bulk_create, get_moto_tire_objects, \
    moto_tire_supplier_bulk_create, get_disk_elements_objects, disk_supplier_bulk_create, get_trucks_disks_objects, \
    trucks_disks_supplier_bulk_create
from apps.suppliers.models import TireSupplier, Tire, DiskSupplier, Disk, TruckTireSupplier, TruckTire, \
    SpecialTireSupplier, SpecialTire, MotoTireSupplier, MotoTire, TruckDisk, TruckDiskSupplier

from lxml import etree


async def tires_elements(suppliers, cities, file_path):
    print('tires_elements')
    tire_suppliers_to_create = []
    tire_objects = {}

    # Use lxml for faster parsing
    for event, elem in etree.iterparse(file_path, events=('end',), tag='tire'):
        tire_data = {
            'id_tire': elem.get('id'),
            'brand': elem.get('brand'),
            'brand_article': elem.get('brandArticul'),
            'product': elem.get('product'),
            'image': elem.get('image'),
            'full_title': elem.get('fullTitle'),
            'model': elem.get('model'),
            'season': elem.get('season'),
            'spike': elem.get('spike') == 'да',
            'runflat': elem.get('runflat') == 'да',
            'lightduty': elem.get('lightduty') == 'да',
            'indexes': elem.get('indexes'),
            'width': elem.get('width'),
            'height': elem.get('height'),
            'diameter': elem.get('diameter'),
            'system': elem.get('system'),
            'omolagation': elem.get('omolagation'),
            'mud': elem.get('mud'),
            'at': elem.get('at'),
            'runFlatTitle': elem.get('runFlatTitle'),
            'fr': elem.get('fr'),
            'xl': elem.get('xl')
        }

        tire_obj = tire_objects.get(tire_data['full_title'])
        if tire_obj is None:
            tire_obj, created = await get_tire_objects(**tire_data)
            tire_objects[tire_data['full_title']] = tire_obj
        for supplier in elem.findall('supplier'):
            articul = supplier.get('articul')
            price = supplier.get('price')
            input_price = supplier.get('inputPrice')
            quantity = supplier.get('quantity')
            supplier_title = supplier.get('supplierTitle')
            city_name = supplier.get('city')
            presence = supplier.get('presence')
            delivery_period_days = supplier.get('deliveryPeriodDays')
            last_availability_date = supplier.get('lastAvailabilityDate')
            sale = supplier.get('sale') == 'yes'

            if last_availability_date:
                last_availability_date_aware = timezone.make_aware(
                    timezone.datetime.strptime(last_availability_date, '%d.%m.%Y %H:%M:%S')
                )
            else:
                last_availability_date_aware = None

            supplier_obj = suppliers.get(supplier_title)
            city_obj = cities.get(city_name)

            if supplier_obj and city_obj:
                tire_suppliers_to_create.append(
                    TireSupplier(
                        tire=tire_obj,
                        articul=articul,
                        price=price,
                        input_price=input_price,
                        quantity=quantity,
                        supplier=supplier_obj,
                        city=city_obj,
                        presence=presence,
                        delivery_period_days=delivery_period_days,
                        last_availability_date=last_availability_date_aware,
                        sale=sale
                    )
                )
        elem.clear()  # Clear the element to free memory
        if len(tire_suppliers_to_create) >= 50:
            try:
                await tire_supplier_bulk_create(tire_suppliers_to_create)
                tire_suppliers_to_create.clear()  # Clear the list after bulk insert
            except Exception as e:
                print(f"Error during bulk_create: {e}")
                print('created tire')

    if tire_suppliers_to_create:
        try:

            await tire_supplier_bulk_create(tire_suppliers_to_create)
            print('created tire_supplier_bulk_create')
        except Exception as e:
            print(f"Error during final bulk_create: {e}")

    print('TIRE OK')

from decimal import Decimal, InvalidOperation


async def safe_decimal_conversion(value):
    if value:
        try:
            # Replace comma with period for decimal conversion
            return Decimal(value.replace(',', '.'))
        except InvalidOperation:
            return Decimal('0.00')  # Default value if conversion fails
    return Decimal('0.00')  # Default value for empty strings


async def trucks_disks_elements(suppliers, cities, root):
    disks_element = root.find('truckDisks')
    if disks_element is not None:
        disk_suppliers_to_create = []
        disk_objects = {}

        # Сбор данных о дисках
        for disk in disks_element.findall('truckDisk'):
            disk_data = {
                'id_disk': disk.get('id'),
                'brand_articul': disk.get('brandArticul'),
                'brand': disk.get('brand'),
                'product': disk.get('product'),
                'image': disk.get('image'),
                'full_title': disk.get('fullTitle'),
                'model': disk.get('model'),
                'pcd': disk.get('pcd'),
                'outfit': disk.get('outfit'),
                'color': disk.get('color'),
                'type': disk.get('type'),
                'width': disk.get('width'),
                'diameter': disk.get('diameter'),
                'boltcount': disk.get('boltcount'),
                'dia': disk.get('dia'),

            }

            # Создаем объект диска только если его еще нет
            disk_obj = disk_objects.get(disk_data['full_title'])
            if disk_obj is None:
                disk_obj, created = await get_trucks_disks_objects(**disk_data)
                disk_objects[disk_data['full_title']] = disk_obj

            # Обработка поставщиков дисков
            for supplier in disk.findall('supplier'):
                articul = supplier.get('articul')
                price = supplier.get('price')
                input_price = supplier.get('inputPrice')
                quantity = supplier.get('quantity')
                supplier_title = supplier.get('supplierTitle')
                city_name = supplier.get('city')
                presence = supplier.get('presence')
                delivery_period_days = supplier.get('deliveryPeriodDays')
                last_availability_date = supplier.get('lastAvailabilityDate')
                sale = supplier.get('sale') == 'yes'

                # Конвертация даты
                last_availability_date_aware = None
                if last_availability_date:
                    last_availability_date_aware = timezone.make_aware(
                        timezone.datetime.strptime(last_availability_date, '%d.%m.%Y %H:%M:%S')
                    )

                supplier_obj = suppliers.get(supplier_title)
                city_obj = cities.get(city_name)

                if supplier_obj and city_obj:
                    disk_suppliers_to_create.append(
                        TruckDiskSupplier(
                            truck_disk=disk_obj,
                            articul=articul,
                            price=price,
                            input_price=input_price,
                            quantity=quantity,
                            supplier=supplier_obj,
                            city=city_obj,
                            presence=presence,
                            delivery_period_days=delivery_period_days,
                            last_availability_date=last_availability_date_aware,
                            sale=sale
                        )
                    )

        # Bulk create all DiskSupplier instances at once
        if disk_suppliers_to_create:
            batch_size = 5
            for i in range(0, len(disk_suppliers_to_create), batch_size):
                batch = disk_suppliers_to_create[i:i + batch_size]
                try:
                    await trucks_disks_supplier_bulk_create(batch)
                except Exception as e:
                    ...
        print('TRUCK DISK OK')


async def disks_elements(suppliers, cities, root):
    print('trucks_disks_elements')
    disks_element = root.find('disks')
    if disks_element is not None:
        disk_suppliers_to_create = []
        disk_objects = {}

        # Сбор данных о дисках
        for disk in disks_element.findall('disk'):
            disk_data = {
                'id_disk': disk.get('id'),
                'brand_articul': disk.get('brandArticul'),
                'brand': disk.get('brand'),
                'product': disk.get('product'),
                'image': disk.get('image'),
                'full_title': disk.get('fullTitle'),
                'model': disk.get('model'),
                'pcd': disk.get('pcd'),
                'outfit': disk.get('outfit'),
                'color': disk.get('color'),
                'type': disk.get('type'),
                'width': disk.get('width'),
                'diameter': disk.get('diameter'),
                'boltcount': disk.get('boltcount'),
                'dia': disk.get('dia'),

            }

            # Создаем объект диска только если его еще нет
            disk_obj = disk_objects.get(disk_data['full_title'])
            if disk_obj is None:
                disk_obj, created = await get_disk_elements_objects(**disk_data)
                disk_objects[disk_data['full_title']] = disk_obj

            # Обработка поставщиков дисков
            for supplier in disk.findall('supplier'):
                articul = supplier.get('articul')
                price = supplier.get('price')
                input_price = supplier.get('inputPrice')
                quantity = supplier.get('quantity')
                supplier_title = supplier.get('supplierTitle')
                city_name = supplier.get('city')
                presence = supplier.get('presence')
                delivery_period_days = supplier.get('deliveryPeriodDays')
                last_availability_date = supplier.get('lastAvailabilityDate')
                sale = supplier.get('sale') == 'yes'

                # Конвертация даты
                last_availability_date_aware = None
                if last_availability_date:
                    last_availability_date_aware = timezone.make_aware(
                        timezone.datetime.strptime(last_availability_date, '%d.%m.%Y %H:%M:%S')
                    )

                supplier_obj = suppliers.get(supplier_title)
                city_obj = cities.get(city_name)

                if supplier_obj and city_obj:
                    disk_suppliers_to_create.append(
                        DiskSupplier(
                            disk=disk_obj,
                            articul=articul,
                            price=price,
                            input_price=input_price,
                            quantity=quantity,
                            supplier=supplier_obj,
                            city=city_obj,
                            presence=presence,
                            delivery_period_days=delivery_period_days,
                            last_availability_date=last_availability_date_aware,
                            sale=sale
                        )
                    )

        # Bulk create all DiskSupplier instances at once
        if disk_suppliers_to_create:
            batch_size = 5
            for i in range(0, len(disk_suppliers_to_create), batch_size):
                batch = disk_suppliers_to_create[i:i + batch_size]
                try:
                    await disk_supplier_bulk_create(batch)
                except Exception as e:
                    ...
        print('DISK OK')


async def truck_tires_element(suppliers, cities, root):
    print('truck tires elements')
    truck_tires_element = root.find('truckTires')
    if truck_tires_element is not None:
        truck_tire_suppliers_to_create = []
        truck_tire_objects = {}

        # Сбор данных о грузовых шинах
        for truck_tire in truck_tires_element.findall('truckTire'):
            truck_tire_data = {
                'id_truck': truck_tire.get('id'),
                'brand_articul': truck_tire.get('brandArticul'),
                'brand': truck_tire.get('brand'),
                'product': truck_tire.get('product'),
                'image': truck_tire.get('image'),
                'full_title': truck_tire.get('fullTitle'),
                'model': truck_tire.get('model'),
                'season': truck_tire.get('season'),
                'indexes': truck_tire.get('indexes'),
                'quadro': truck_tire.get('quadro') == 'да',
                'lightduty': truck_tire.get('lightduty') == 'да',
                'special': truck_tire.get('special') == 'да',
                'width': truck_tire.get('width'),
                'height': truck_tire.get('height'),
                'diameter': truck_tire.get('diameter'),
                'number_of_plies': truck_tire.get('numberOfPlies'),
                'axis': truck_tire.get('axis') or ''
            }

            # Создаем объект грузовой шины только если его еще нет
            truck_tire_obj = truck_tire_objects.get(truck_tire_data['full_title'])
            if truck_tire_obj is None:
                truck_tire_obj, created = await get_truck_objects()
                truck_tire_objects[truck_tire_data['full_title']] = truck_tire_obj

            # Обработка поставщиков грузовых шин
            for supplier in truck_tire.findall('supplier'):
                articul = supplier.get('articul')
                price = supplier.get('price')
                input_price = supplier.get('inputPrice')
                quantity = supplier.get('quantity')
                supplier_title = supplier.get('supplierTitle')
                city_name = supplier.get('city')
                presence = supplier.get('presence')
                delivery_period_days = supplier.get('deliveryPeriodDays')
                last_availability_date = supplier.get('lastAvailabilityDate')
                sale = supplier.get('sale') == 'yes'

                # Конвертация даты
                last_availability_date_aware = None
                if last_availability_date:
                    last_availability_date_aware = timezone.make_aware(
                        timezone.datetime.strptime(last_availability_date, '%d.%m.%Y %H:%M:%S')
                    )

                supplier_obj = suppliers.get(supplier_title)
                city_obj = cities.get(city_name)

                if supplier_obj and city_obj:
                    truck_tire_suppliers_to_create.append(
                        TruckTireSupplier(
                            truck_tire=truck_tire_obj,
                            articul=articul,
                            price=price,
                            input_price=input_price,
                            quantity=quantity,
                            supplier=supplier_obj,
                            city=city_obj,
                            presence=presence,
                            delivery_period_days=delivery_period_days,
                            last_availability_date=last_availability_date_aware,
                            sale=sale
                        )
                    )

        # Bulk create all TruckTireSupplier instances at once
        if truck_tire_suppliers_to_create:
            batch_size = 100
            for i in range(0, len(truck_tire_suppliers_to_create), batch_size):
                batch = truck_tire_suppliers_to_create[i:i + batch_size]
                try:
                    await truck_tire_supplier_bulk_create(batch)
                    print('Successfully created')
                except Exception as e:
                    ...
        print('TRUCK OK')


async def special_tires_element(suppliers, cities, root):
    print('special_tires_element')
    special_tires_element = root.find('specialTires')
    if special_tires_element is not None:
        special_tire_suppliers_to_create = []
        special_tire_objects = {}

        # Сбор данных о специальных шинах
        for special_tire in special_tires_element.findall('specialTire'):
            special_tire_data = {
                'id_special': special_tire.get('id'),
                'brand_articul': special_tire.get('brandArticul'),
                'brand': special_tire.get('brand'),
                'product': special_tire.get('product'),
                'image': special_tire.get('image'),
                'full_title': special_tire.get('fullTitle'),
                'model': special_tire.get('model'),
                'diameter': special_tire.get('diameter'),
                'typesize': special_tire.get('typesize'),
                'kit': special_tire.get('kit'),
                'indexes': special_tire.get('indexes'),
                'layers': special_tire.get('layers'),
                'camera': special_tire.get('camera'),
                'diagonal': special_tire.get('Dioganal') == 'да',
                'solid': special_tire.get('Solid') == 'да',
                'note': special_tire.get('Note', ''),
                'countries': special_tire.get('Countries', ''),
                'protector_type': special_tire.get('ProtectorType', '')
            }

            # Создаем объект специальной шины только если его еще нет
            special_tire_obj = special_tire_objects.get(special_tire_data['full_title'])
            if special_tire_obj is None:
                special_tire_obj, created = await get_special_tire_objects(**special_tire_data)
                special_tire_objects[special_tire_data['full_title']] = special_tire_obj

            # Обработка поставщиков специальных шин
            for supplier in special_tire.findall('supplier'):
                articul = supplier.get('articul')
                price = supplier.get('price')
                input_price = supplier.get('inputPrice')
                quantity = supplier.get('quantity')
                supplier_title = supplier.get('supplierTitle')
                city_name = supplier.get('city')
                presence = supplier.get('presence')
                delivery_period_days = supplier.get('deliveryPeriodDays')
                last_availability_date = supplier.get('lastAvailabilityDate')
                sale = supplier.get('sale') == 'yes'

                # Конвертация даты
                last_availability_date_aware = None
                if last_availability_date:
                    last_availability_date_aware = timezone.make_aware(
                        timezone.datetime.strptime(last_availability_date, '%d.%m.%Y %H:%M:%S')
                    )

                supplier_obj = suppliers.get(supplier_title)
                city_obj = cities.get(city_name)

                if supplier_obj and city_obj:
                    special_tire_suppliers_to_create.append(
                        SpecialTireSupplier(
                            special_tire=special_tire_obj,
                            articul=articul,
                            price=price,
                            input_price=input_price,
                            quantity=quantity,
                            supplier=supplier_obj,
                            city=city_obj,
                            presence=presence,
                            delivery_period_days=delivery_period_days,
                            last_availability_date=last_availability_date_aware,
                            sale=sale
                        )
                    )

        # Bulk create all SpecialTireSupplier instances at once
        if special_tire_suppliers_to_create:
            batch_size = 100
            for i in range(0, len(special_tire_suppliers_to_create), batch_size):
                batch = special_tire_suppliers_to_create[i:i + batch_size]
                try:
                    await special_tire_supplier_bulk_create(batch)
                except Exception as e:
                    ...
    print('SPECIAL OK')


async def moto_tires_element(suppliers, cities, root):
    print('moto_tires_element')
    moto_tires_element = root.find('mototires')
    if moto_tires_element is not None:
        moto_tire_suppliers_to_create = []
        moto_tire_objects = {}

        # Сбор данных о мотоциклетных шинах
        for moto_tire in moto_tires_element.findall('motoTire'):
            moto_tire_data = {
                'id_moto': moto_tire.get('id'),
                'brand_articul': moto_tire.get('brandArticul'),
                'brand': moto_tire.get('brand'),
                'product': moto_tire.get('product'),
                'image': moto_tire.get('image'),
                'full_title': moto_tire.get('fullTitle'),
                'width': moto_tire.get('width'),
                'height': moto_tire.get('height'),
                'diameter': moto_tire.get('diameter'),
                'indexes': moto_tire.get('indexes'),
                'axis': moto_tire.get('axis'),
                'system': moto_tire.get('system', ''),
                'volume': moto_tire.get('volume'),
                'weight': moto_tire.get('weight'),
                'year': moto_tire.get('year', ''),
                'camera': moto_tire.get('camera'),
                'runflat': moto_tire.get('runflat') == 'да',
                'omolagation': moto_tire.get('omolagation', '')
            }

            # Создаем объект мотоциклетной шины только если его еще нет
            moto_tire_obj = moto_tire_objects.get(moto_tire_data['full_title'])
            if moto_tire_obj is None:
                moto_tire_obj, created = await get_moto_tire_objects(**moto_tire_data)
                moto_tire_objects[moto_tire_data['full_title']] = moto_tire_obj

            # Обработка поставщиков мотоциклетных шин
            for supplier in moto_tire.findall('supplier'):
                articul = supplier.get('articul')
                price = supplier.get('price')
                input_price = supplier.get('inputPrice')
                quantity = supplier.get('quantity')
                supplier_title = supplier.get('supplierTitle')
                city_name = supplier.get('city')
                presence = supplier.get('presence')
                delivery_period_days = supplier.get('deliveryPeriodDays')
                last_availability_date = supplier.get('lastAvailabilityDate')
                sale = supplier.get('sale') == 'yes'

                # Конвертация даты
                last_availability_date_aware = None
                if last_availability_date:
                    last_availability_date_aware = timezone.make_aware(
                        timezone.datetime.strptime(last_availability_date, '%d.%m.%Y %H:%M:%S')
                    )

                supplier_obj = suppliers.get(supplier_title)
                city_obj = cities.get(city_name)

                if supplier_obj and city_obj:
                    moto_tire_suppliers_to_create.append(
                        MotoTireSupplier(
                            moto_tire=moto_tire_obj,
                            articul=articul,
                            price=price,
                            input_price=input_price,
                            quantity=quantity,
                            supplier=supplier_obj,
                            city=city_obj,
                            presence=presence,
                            delivery_period_days=delivery_period_days,
                            last_availability_date=last_availability_date_aware,
                            sale=sale
                        )
                    )

        # Bulk create all MotoTireSupplier instances at once
        if moto_tire_suppliers_to_create:
            batch_size = 100
            for i in range(0, len(moto_tire_suppliers_to_create), batch_size):
                batch = moto_tire_suppliers_to_create[i:i + batch_size]
                try:
                    await moto_tire_supplier_bulk_create(batch)
                except Exception as e:
                    ...
        print('MOTO OK')
