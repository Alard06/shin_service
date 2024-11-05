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